from rest_framework import serializers
from .models import AuditLog
from users.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les logs d'audit"""
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'action',
            'action_display',
            'target_user',
            'target_user_email',
            'target_model',
            'target_id',
            'description',
            'changes',
            'ip_address',
            'user_agent',
            'timestamp',
            'severity',
            'severity_display'
        ]
        read_only_fields = ['id', 'timestamp']


class AuditLogListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des logs"""
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    target_user_email = serializers.CharField(source='target_user.email', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user_email',
            'action',
            'action_display',
            'target_user_email',
            'description',
            'timestamp',
            'severity',
            'severity_display'
        ]