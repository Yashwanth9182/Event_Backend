

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'reviews', views.ReviewViewSet)

urlpatterns = [
    path('api/auth/register/', views.RegisterView.as_view()),
    path('api/auth/login/', views.LoginView.as_view(),name='login'),
    path('api/auth/logout/', views.LogoutView.as_view()),
    path('api/auth/user/', views.CurrentUserView.as_view()),
    path('api/users/', views.AllUsersView.as_view(), name='all-users'),
    path('api/users/manage/', views.UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-manage'),
    path('api/', include(router.urls)),
]

