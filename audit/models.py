from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class AuditLog(models.Model):
    """
    Historique des actions effectuées sur la plateforme
    """
    
    ACTION_CHOICES = [
        # Auth
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_register', 'User Register'),
        ('login_failed', 'Login Failed'),
        
        # User Management
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('role_changed', 'Role Changed'),
        ('user_activated', 'User Activated'),
        ('user_deactivated', 'User Deactivated'),
        
        # Content (pour plus tard)
        ('challenge_created', 'Challenge Created'),
        ('challenge_updated', 'Challenge Updated'),
        ('challenge_deleted', 'Challenge Deleted'),
        ('solution_submitted', 'Solution Submitted'),
        ('solution_validated', 'Solution Validated'),
        
        # Admin actions
        ('admin_action', 'Admin Action'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Qui a fait l'action
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs',
        help_text="User qui a effectué l'action (null si action système)"
    )
    
    # Quoi
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Sur quoi/qui
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs_as_target',
        help_text="User cible de l'action (si applicable)"
    )
    
    target_model = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Type de l'objet ciblé (User, Challenge, etc.)"
    )
    
    target_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="ID de l'objet ciblé"
    )
    
    # Détails
    description = models.TextField(
        blank=True,
        help_text="Description lisible de l'action"
    )
    
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Détails des changements (avant/après)"
    )
    
    # Contexte
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Adresse IP de l'utilisateur"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="User-Agent du navigateur"
    )
    
    # Quand
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    # Niveau de criticité
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
    ]
    
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='info'
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else 'System'
        return f"[{self.get_severity_display()}] {user_str} - {self.get_action_display()} @ {self.timestamp}"