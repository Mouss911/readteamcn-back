from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # ✅ Nouveau champ pour Platform Admin
    is_platform_admin = models.BooleanField(
        default=False,
        help_text="Désigne si l'utilisateur est un admin de la plateforme (accès global)"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def is_admin(self):
        """Vérifie si user est Admin (Platform Admin OU role admin dans son org)"""
        if self.is_platform_admin or self.is_staff:
            return True
        
        # Vérifier le rôle dans la membership
        membership = self.membership_set.first()
        return membership.role == 'admin' if membership else False
    
    def is_coach(self):
        """Vérifie si user est Coach ou Admin"""
        if self.is_admin():
            return True
        
        membership = self.membership_set.first()
        return membership.role in ['coach', 'admin'] if membership else False
    
    def can_validate(self):
        """Vérifie si user peut valider (Coach ou Admin)"""
        return self.is_coach()
    
    def can_manage_users(self):
        """Vérifie si user peut gérer les users (Platform Admin uniquement)"""
        return self.is_platform_admin or self.is_staff
    
    

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    plan_tier = models.CharField(
        max_length=20, 
        choices=[('free', 'Free'), ('pro', 'Pro'), ('enterprise', 'Enterprise')],
        default='free'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('developer', 'Developer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['user', 'organization']
    
    def __str__(self):
        return f"{self.user.email} - {self.role} - {self.organization.name}"