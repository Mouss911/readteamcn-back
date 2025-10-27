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