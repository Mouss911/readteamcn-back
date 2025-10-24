from rest_framework.permissions import BasePermission
from .models import Membership, Organization

class IsPlatformAdmin(BasePermission):
    """
    Seuls les Platform Admins (is_platform_admin=True ou is_staff=True)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.is_platform_admin
        )


class IsOrgAdmin(BasePermission):
    """
    User doit être admin de l'organisation concernée
    Ou être Platform Admin
    """
    def has_permission(self, request, view):
        # Platform admin bypass
        if request.user.is_staff or request.user.is_platform_admin:
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Platform admin bypass
        if request.user.is_staff or request.user.is_platform_admin:
            return True
        
        # Récupérer l'organisation de l'objet
        if hasattr(obj, 'organization'):
            org = obj.organization
        elif isinstance(obj, Organization):
            org = obj
        else:
            return False
        
        # Vérifier si user est admin de cette org
        return Membership.objects.filter(
            user=request.user,
            organization=org,
            role='admin'
        ).exists()


class IsAdminOrCoach(BasePermission):
    """
    Admin OU Coach (pour validation/publication)
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.is_staff or request.user.is_platform_admin:
            return True
        
        return Membership.objects.filter(
            user=request.user,
            role__in=['admin', 'coach']
        ).exists()


class IsSelfOrAdmin(BasePermission):
    """
    User peut modifier ses propres données, ou admin peut tout modifier
    """
    def has_object_permission(self, request, view, obj):
        # Platform admin bypass
        if request.user.is_staff or request.user.is_platform_admin:
            return True
        
        # L'objet est un User
        if hasattr(obj, 'email'):
            return obj == request.user
        
        return False