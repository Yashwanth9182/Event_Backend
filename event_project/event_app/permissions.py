# permissions.py
from rest_framework import permissions

class IsOrganizerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Write permissions for organizer of event or admin
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user or request.user.is_staff

    def has_permission(self, request, view):
        # Only authenticated users can create/update/delete
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
