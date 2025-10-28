from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Membership
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from allauth.account.models import EmailConfirmation

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les infos d'un user"""
    organizations = serializers.SerializerMethodField()
    is_platform_admin = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User

        fields = ['id', 'email', 'username', 'is_active', 'last_login','first_name', 'last_name']
        read_only_fields = ['id', 'is_active', 'last_login']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    organization_name = serializers.CharField(max_length=255, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'organization_name', 'first_name', 'last_name']
    
    def create(self, validated_data):
        organization_name = validated_data.pop('organization_name', None)
        password = validated_data.pop('password')
        first_name=validated_data.get('first_name', ''),
        last_name=validated_data.get('last_name', '')
        
        # ✅ Fix : create_user hash déjà le password
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password
        )
        
        # Créer organisation si fournie
        if organization_name:
            org = Organization.objects.create(
                name=organization_name, 
                domain=f"{user.username}.redteamcn.com"
            )
            Membership.objects.create(
                user=user, 
                organization=org, 
                role='admin'  # Premier user = admin de l'org
            )
        
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

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

class MembershipSerializer(serializers.ModelSerializer):
    """Serializer pour les memberships"""
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True, required=False)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'user', 'user_email', 
            'organization', 'organization_name',
            'role', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']