from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import logging

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .permissions import IsPlatformAdmin

logger = logging.getLogger(__name__)
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register(request):
    """Inscription d'un nouvel utilisateur"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.email}")
        
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
        return Response(
            {'detail': "Email ou mot de passe incorrect."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        logger.warning(f"Failed login attempt for: {email}")
        return Response(
            {'detail': "Email ou mot de passe incorrect."}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'detail': "Ce compte est désactivé."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    # ✅ Mise à jour last_login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    refresh = RefreshToken.for_user(user)
    
    logger.info(f"User logged in: {user.email}")
    
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
@permission_classes([IsPlatformAdmin])
def promote_to_platform_admin(request):
    """
    Endpoint ADMIN : Promouvoir un user en Platform Admin
    
    Body: {"user_id": 123}
    """
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response(
            {'detail': 'user_id requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Utilisateur introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user.is_platform_admin = True
    user.save(update_fields=['is_platform_admin'])
    
    logger.info(f"User {user.email} promoted to Platform Admin by {request.user.email}")
    
    return Response({
        'message': f'{user.email} est maintenant Platform Admin',
        'user': UserSerializer(user).data
    })

@api_view(['GET'])
@permission_classes([IsPlatformAdmin])
def list_all_users(request):
    """
    Endpoint ADMIN : Liste TOUS les users (réservé aux Platform Admins)
    """
    users = User.objects.all().order_by('-date_joined')
    serializer = UserSerializer(users, many=True)
    
    return Response({
        'count': users.count(),
        'users': serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsPlatformAdmin])
def delete_user(request, user_id):
    """
    Endpoint ADMIN : Supprimer un user
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
    
    email = user.email
    user.delete()
    
    logger.warning(f"User {email} deleted by {request.user.email}")
    
    return Response({
        'message': f'Utilisateur {email} supprimé avec succès'
    }, status=status.HTTP_200_OK)