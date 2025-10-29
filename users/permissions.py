from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission : Seul l'Admin unique a accès
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin()
        )


class IsCoach(BasePermission):
    """
    Permission : Coach ou Admin
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_coach()
        )


class IsOwnerOrCoach(BasePermission):
    """
    Permission : Propriétaire de l'objet OU Coach/Admin
    """
    def has_object_permission(self, request, view, obj):
        # Coach/Admin peuvent tout modifier
        if request.user.is_coach():
            return True
        
        # Propriétaire peut modifier son propre contenu
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        if hasattr(obj, 'author'):
            return obj.author == request.user
        
        return False