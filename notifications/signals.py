from django.db.models.signals import post_save
from django.dispatch import receiver
from reviews.models import Review
from .models import Notification

@receiver(post_save, sender=Review)
def create_review_notification(sender, instance, created, **kwargs):
    if created:
        # Notifier le créateur du composant
        if instance.component.created_by != instance.user:
            Notification.objects.create(
                recipient=instance.component.created_by,
                actor=instance.user,
                verb='review_created',
                target=instance.component,
                review=instance,
                message=f"{instance.user.email} a ajouté une review sur votre composant"
            )
    else:
        # Mise à jour → notifier seulement si c'est pas la même personne
        if instance.component.created_by != instance.user:
            Notification.objects.create(
                recipient=instance.component.created_by,
                actor=instance.user,
                verb='review_updated',
                target=instance.component,
                review=instance,
                message=f"{instance.user.email} a mis à jour sa review"
            )