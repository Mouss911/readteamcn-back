from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    UserSerializer, 
    MembershipSerializer
)

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ChangeRoleSerializer
from .permissions import IsAdmin
from audit.utils import create_audit_log, get_client_ip, log_user_action


logger = logging.getLogger(__name__)
User = get_user_model()
token_generator = PasswordResetTokenGenerator()


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register(request):
    """Inscription d'un nouvel utilisateur (toujours Developer)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
        # ✅ Log d'audit
        create_audit_log(
            action='user_register',
            user=user,
            description=f"New user registered: {user.email}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='info'
        )
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login(request):
    """Connexion utilisateur"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.warning(f"Login attempt with non-existent email: {email}")
        
        # ✅ Log d'échec de connexion (email inexistant)
        create_audit_log(
            action='login_failed',
            description=f"Failed login attempt with non-existent email: {email}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='warning'
        )
        
        return Response(
            {'detail': "Email ou mot de passe incorrect."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    

    if not user.check_password(password):
        logger.warning(f"Failed login attempt for: {email}")
        # ✅ Log d'échec de connexion (mauvais password)
        create_audit_log(
            action='login_failed',
            user=user,
            description=f"Failed login attempt: wrong password for {email}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            severity='warning'
        )
        return Response(
            {'detail': "Email ou mot de passe incorrect."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'detail': "Ce compte est désactivé."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # Mise à jour last_login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    refresh = RefreshToken.for_user(user)
    
    logger.info(f"User logged in: {user.email}")
    
    # ✅ Log de connexion réussie
    create_audit_log(
        action='user_login',
        user=user,
        description=f"User {user.email} logged in successfully",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='info'
    )
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Informations de l'utilisateur connecté"""
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Déconnexion (blacklist le refresh token)"""
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        logger.info(f"User logged out: {request.user.email}")
        
        # ✅ Log de déconnexion
        log_user_action(
            request=request,
            action='user_logout',
            description=f"User {request.user.email} logged out",
            severity='info'
        )
        
        return Response(
            {'message': 'Successfully logged out'}, 
            status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================
# SECTION ADMIN (UN SEUL ADMIN)
# ============================================

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_all_users(request):
    """
    Liste TOUS les users (Admin uniquement)
    """
    users = User.objects.all().order_by('-date_joined')
    serializer = UserSerializer(users, many=True)
    
    return Response({
        'count': users.count(),
        'users': serializer.data
    })


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def change_user_role(request, user_id):
    """
    Changer le rôle d'un user (Coach ou Developer)
    L'Admin ne peut PAS créer d'autres Admins
    
    Body: {"role": "coach"}
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Utilisateur introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Empêcher de modifier le rôle de l'Admin unique
    if user.is_admin():
        return Response(
            {'detail': 'Impossible de modifier le rôle de l\'Admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = ChangeRoleSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    new_role = serializer.validated_data['role']
    old_role = user.role
    
    user.role = new_role
    user.save(update_fields=['role'])
    
    logger.info(f"User {user.email} role changed from {old_role} to {new_role} by {request.user.email}")
    # ✅ Log de changement de rôle
    log_user_action(
        request=request,
        action='role_changed',
        target_user=user,
        description=f"Role changed from {old_role} to {new_role} for {user.email}",
        changes={
            'old_role': old_role,
            'new_role': new_role
        },
        severity='info'
    )
    
    return Response({
        'message': f'Rôle de {user.email} changé de {old_role} à {new_role}',
        'user': UserSerializer(user).data
    })


@api_view(['PATCH'])
@permission_classes([IsAdmin])
def toggle_user_active(request, user_id):
    """
    Activer/Désactiver un user (Admin uniquement)
    
    Body: {"is_active": false}
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Utilisateur introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Empêcher de se désactiver soi-même
    if user == request.user:
        return Response(
            {'detail': 'Vous ne pouvez pas vous désactiver vous-même'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Empêcher de désactiver l'Admin
    if user.is_admin():
        return Response(
            {'detail': 'Impossible de désactiver l\'Admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    is_active = request.data.get('is_active')
    
    if is_active is None:
        return Response(
            {'detail': 'is_active requis (true/false)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Sauvegarder l'ancien statut pour le log
    old_status = user.is_active
    
    user.is_active = is_active
    user.save(update_fields=['is_active'])
    
    action = "activé" if is_active else "désactivé"
    logger.warning(f"User {user.email} {action} by {request.user.email}")
    
    # ✅ Log d'activation/désactivation - CORRECTION: old_status est maintenant défini
    log_user_action(
        request=request,
        action='user_activated' if is_active else 'user_deactivated',
        target_user=user,
        description=f"User {user.email} {action} by {request.user.email}",
        changes={
            'old_status': old_status,  # ← Maintenant défini
            'new_status': is_active
        },
        severity='warning'
    )
    
    return Response({
        'message': f'Utilisateur {user.email} {action}',
        'user': UserSerializer(user).data
    })


@api_view(['DELETE'])
@permission_classes([IsAdmin])
def delete_user(request, user_id):
    """
    Supprimer définitivement un user (Admin uniquement)
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Utilisateur introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Empêcher de se supprimer soi-même
    if user == request.user:
        return Response(
            {'detail': 'Vous ne pouvez pas vous supprimer vous-même'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Empêcher de supprimer l'Admin
    if user.is_admin():
        return Response(
            {'detail': 'Impossible de supprimer l\'Admin'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    email = user.email
    username = user.username
    
    # Sauvegarder les données de l'utilisateur avant suppression pour le log
    user_data = {
        'email': email,
        'username': username,
        'role': user.role
    }
    
    user.delete()
    
    logger.warning(f"User {email} DELETED by {request.user.email}")
    
    # ✅ Log de suppression - CORRECTION: user_data est maintenant défini
    log_user_action(
        request=request,
        action='user_deleted',
        description=f"User {email} permanently deleted by {request.user.email}",
        changes={'deleted_user': user_data},  # ← Maintenant défini
        severity='critical'
    )
    
    return Response({
        'message': f'Utilisateur {email} supprimé définitivement'
    }, status=status.HTTP_200_OK)

# ============================================
# SECTION PUBLIQUE
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    Liste basique des users actifs (pour tous les users authentifiés)
    """
    users = User.objects.filter(is_active=True).order_by('-date_joined')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# gestion de mot de passe oubliée
@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Ne pas révéler si l'email existe ou non (sécurité)
        return Response({'message': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)

    # Générer token et UID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    # Construire le lien de réinitialisation
    reset_url = request.build_absolute_uri(
        reverse('reset_password', kwargs={'uidb64': uid, 'token': token})
    )

    # Envoyer l'email
    send_mail(
        subject='Réinitialisation de votre mot de passe',
        message=f'Cliquez sur ce lien pour réinitialiser votre mot de passe : {reset_url}',
        from_email='no-reply@redteamcn.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

    return Response({'message': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

    if not token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    if not new_password or new_password != confirm_password:
        return Response({'error': 'Passwords do not match or are missing'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)