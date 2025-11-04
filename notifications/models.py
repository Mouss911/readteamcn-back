from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Component
from reviews.models import Review

User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('review_created', 'Nouvelle review'),
        ('review_updated', 'Review mise à jour'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    verb = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    target = models.ForeignKey(Component, on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor} {self.get_verb_display()} sur {self.target}"