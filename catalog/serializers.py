from rest_framework import serializers
from .models import Component

class ComponentSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Component
        fields = ['id', 'name', 'description', 'category', 'code', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']