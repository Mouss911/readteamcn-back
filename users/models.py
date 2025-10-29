from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    """Utilisateur de la plateforme RedTeamCN"""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Rôle de l'utilisateur sur la plateforme
    ROLE_CHOICES = [
        ('admin', 'Admin'),        # UN SEUL admin
        ('coach', 'Coach'),
        ('developer', 'Developer'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='developer',
        help_text="Rôle de l'utilisateur sur la plateforme"
    )
    
    # Infos supplémentaires (optionnel)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    # ============================================
    # Méthodes helper pour les permissions
    # ============================================
    
    def is_admin(self):
        """Vérifie si user est Admin"""
        return self.role == 'admin' or self.is_staff or self.is_superuser
    
    def is_coach(self):
        """Vérifie si user est Coach ou Admin"""
        return self.role in ['admin', 'coach']
    
    def can_create_content(self):
        """Tous les users peuvent créer du contenu"""
        return self.role in ['developer', 'coach', 'admin']
    
    def can_validate(self):
        """Vérifie si user peut valider des soumissions (Coach+)"""
        return self.is_coach()
    
    def can_publish(self):
        """Vérifie si user peut publier directement (Coach+)"""
        return self.is_coach()
    
    def can_manage_users(self):
        """Vérifie si user peut gérer les users (Admin uniquement)"""
        return self.is_admin()