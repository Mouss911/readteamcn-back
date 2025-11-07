from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer
from catalog.serializers import ComponentSerializer

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer()
    target = ComponentSerializer()
    review = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'target', 'review', 'message', 'is_read', 'created_at']

    def get_review(self, obj):
        return {"id": obj.review.id, "rating": obj.review.rating} if obj.review else None