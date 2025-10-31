from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    actor = UserSerializer()
    target = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'target', 'review', 'message', 'is_read', 'created_at']

    def get_target(self, obj):
        return {"id": obj.target.id, "name": obj.target.name} if obj.target else None

    def get_review(self, obj):
        return {"id": obj.review.id, "rating": obj.review.rating} if obj.review else None