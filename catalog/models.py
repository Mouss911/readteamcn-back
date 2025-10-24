from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Component(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('BUTTON', 'Button'),
        ('CARD', 'Card'),
        ('INPUT', 'Input'),
        ('MODAL', 'Modal'),
    ])
    code = models.TextField()  # HTML/CSS/JS du composant
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='components')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name