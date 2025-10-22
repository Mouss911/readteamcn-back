from rest_framework import serializers
from .models import AuditLog, Notification, TokenSet, Membership, Review, KpiEvent

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class TokenSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenSet
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class KpiEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = KpiEvent
        fields = '__all__'