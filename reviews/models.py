from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Component
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Review(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('component', 'user')  # 1 review par user

    def __str__(self):
        return f"{self.user.email} - {self.component.name} - {self.rating} étoile(s)"