from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    """Manager personnalisé pour User basé sur l'email"""

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Créer un utilisateur standard"""
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Créer un superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superuser doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Utilisateur de la plateforme RedTeamCN"""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coach', 'Coach'),
        ('developer', 'Developer'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='developer',
        help_text="Rôle de l'utilisateur sur la plateforme"
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Plus besoin de 'username'

    objects = UserManager()  # Manager personnalisé

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    # Méthodes helper pour les permissions
    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def is_coach(self):
        return self.role in ['admin', 'coach']

    def can_create_content(self):
        return self.role in ['developer', 'coach', 'admin']

    def can_validate(self):
        return self.is_coach()

    def can_publish(self):
        return self.is_coach()

    def can_manage_users(self):
        return self.is_admin()
