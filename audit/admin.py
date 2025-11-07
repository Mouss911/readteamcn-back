from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Interface d'administration pour AuditLog"""
    
    list_display = ['timestamp', 'user', 'action', 'target_user', 'severity', 'ip_address']
    list_filter = ['action', 'severity', 'timestamp']
    search_fields = ['user__email', 'target_user__email', 'description', 'ip_address']
    readonly_fields = ['id', 'timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Qui', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Quoi', {
            'fields': ('action', 'description', 'severity')
        }),
        ('Cible', {
            'fields': ('target_user', 'target_model', 'target_id')
        }),
        ('Détails', {
            'fields': ('changes',)
        }),
        ('Timestamp', {
            'fields': ('id', 'timestamp')
        }),
    )
    
    def has_add_permission(self, request):
        """Empêcher la création manuelle de logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Empêcher la modification des logs"""
        return False