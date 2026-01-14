from rest_framework import viewsets, permissions
from .models import Event,Ticket,Comment,Review
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer,EventSerializer,TicketSerializer,CommentSerializer,ReviewSerializer
# from event_app.models import User
from event_app.models import User
from django.contrib.auth import authenticate 
from rest_framework.permissions import IsAdminUser

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD operations for User management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only superusers/staff can access




class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username:
            username = username.strip()
        if password:
            password = password.strip()
            
        if not username or not password:
            return Response({'non_field_errors': ['Both username and password are required.']}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            print(f"✅ USER AUTHENTICATED: {user.username}")  # DEBUG
            print(f"   is_active: {user.is_active}, is_staff: {user.is_staff}")  # DEBUG
            
            if not user.is_active:
                return Response({'non_field_errors': ['User account is disabled.']}, status=400)
            
            try:
                print("🔄 Creating token...")  # DEBUG
                token, created = Token.objects.get_or_create(user=user)
                print(f"✅ TOKEN CREATED: {token.key[:10]}...")  # DEBUG
            except Exception as e:
                print(f"❌ TOKEN ERROR: {e}")  # DEBUG
                return Response({'non_field_errors': [f'Token error: {str(e)}']}, status=400)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
            }, status=200)
        
        return Response({'non_field_errors': ['Unable to log in with provided credentials.']}, status=400)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer  # ✅ ADD THIS

    def get_object(self):
        return self.request.user  # ✅ Standard DRF pattern

class AllUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  # Only admins see all users

class IsOrganizerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # CREATE action - no object exists yet
        if request.method == 'POST':
            return request.user and request.user.is_authenticated and request.user.role in ['organizer', 'admin']
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # UPDATE/DELETE - check object ownership
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user or request.user.role == 'admin'




class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOrganizerOrAdmin]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

from rest_framework import viewsets, permissions

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # Assuming Ticket has user field


class CommentViewSet(viewsets.ModelViewSet):
    # Only logged-in users can add/edit/delete
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    # Owners or admins can edit/delete
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
