from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from allauth.account.models import EmailConfirmation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos d'un user"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 
            'role', 'role_display',
            'is_active', 'last_login', 'date_joined',
            'first_name', 'last_name',
        ]
        read_only_fields = ['id', 'is_active', 'last_login', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription"""
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # Par défaut, nouveau user = Developer
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='developer'  # Toujours Developer à l'inscription
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour le login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangeRoleSerializer(serializers.Serializer):
    """Serializer pour changer le rôle d'un user (Admin only)"""
    role = serializers.ChoiceField(
        choices=[
            ('coach', 'Coach'),
            ('developer', 'Developer'),
            # 'admin' n'est PAS dans les choix (un seul admin)
        ]
    )


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate_token(self, value):
        try:
            uidb64, token = value.split('-')
            uid = force_str(urlsafe_base64_decode(uidb64))
            confirmation = EmailConfirmation.objects.get(key=token, email_address__user__username=uid)
            confirmation.confirm()
        except (ValueError, EmailConfirmation.DoesNotExist):
            raise serializers.ValidationError("Token invalide")
        return value

