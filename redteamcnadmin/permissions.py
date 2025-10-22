from rest_framework import permissions
from .models import Membership

class IsAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return Membership.objects.filter(user=request.user, role='Admin').exists()