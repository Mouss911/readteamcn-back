from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Component
from .serializers import ComponentSerializer
from notifications.models import Notification

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_component(request):
    serializer = ComponentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_components(request):
    # Récupérer le filtre
    category = request.query_params.get('category')

    # Base : seulement les composants validés
    components = Component.objects.filter(status='approved')

    # Filtrer par catégorie si demandé
    if category:
        components = components.filter(category=category.upper())
    
    # RECHERCHE PAR NOM
    search = request.query_params.get('search')
    if search:
        components = components.filter(name__icontains=search)

    serializer = ComponentSerializer(components, many=True)
    return Response(serializer.data)

# Modification d'un component
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_component(request, pk):
    try:
        component = Component.objects.get(pk=pk, created_by=request.user)
    except Component.DoesNotExist:
        return Response({'error': 'Component not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ComponentSerializer(component, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Suppression d'un component
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_component(request, pk):
    try:
        component = Component.objects.get(pk=pk, created_by=request.user)
    except Component.DoesNotExist:
        return Response({'error': 'Component not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
    
    component.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# Soumission d'un component pour validation
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_for_review(request, component_id):
    try:
        component = Component.objects.get(id=component_id, created_by=request.user)
    except Component.DoesNotExist:
        return Response({'error': 'Composant introuvable'}, status=404)

    if component.status != 'draft':
        return Response({'error': 'Déjà soumis ou traité'}, status=400)

    component.status = 'pending'
    component.save()

    # NOTIFIER LES COACHS ET ADMINS
    actor_name = request.user.get_full_name() or request.user.username
    coaches = User.objects.filter(role='coach')
    admins = User.objects.filter(role='admin')

    for user in list(coaches) + list(admins):
        Notification.objects.create(
            recipient=user,
            actor=request.user,
            verb='component_submitted',
            target=component,
            message=f"{actor_name} a soumis '{component.name}' pour validation"
        )

    return Response({'message': 'Soumis pour validation'})

# Validation ou rejet d'un component par un Coach
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_component(request, component_id):
    if request.user.role != 'coach':
        return Response(
            {'error': 'Seuls les Coachs peuvent valider/rejeter'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        component = Component.objects.get(id=component_id, status='pending')
    except Component.DoesNotExist:
        return Response({'error': 'Composant non trouvé ou non en attente'}, status=404)

    action = request.data.get('action')
    reason = request.data.get('reason', '')

    if action not in ['approve', 'reject']:
        return Response({'error': 'action doit être "approve" ou "reject"'}, status=400)

    component.status = 'approved' if action == 'approve' else 'rejected'
    component.save()

    actor_name = request.user.get_full_name() or request.user.username
    admins = User.objects.filter(role='admin')

    # NOTIFIER LE DEVELOPER
    Notification.objects.create(
        recipient=component.created_by,
        actor=request.user,
        verb='component_reviewed',
        target=component,
        message=f"Votre composant '{component.name}' a été {action == 'approve' and 'validé' or 'rejeté'}"
        + (f" : {reason}" if reason else "")
    )

    # Notifier l'Admin
    for admin in admins:
        Notification.objects.create(
            recipient=admin,
            actor=request.user,
            verb='component_reviewed',
            target=component,
            message=f"{actor_name} a {action == 'approve' and 'validé' or 'rejeté'} le composant '{component.name}'"
        )

    return Response({
        'message': f'Composant {action == "approve" and "validé" or "rejeté"}',
        'status': component.status
    })

# Permettre à l'utilisateur de voir tous ses composants
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_components(request):
    # Tous les composants du user connecté
    components = Component.objects.filter(created_by=request.user)
    
    # Optionnel : trier par date
    components = components.order_by('-created_at')

    serializer = ComponentSerializer(components, many=True)
    return Response(serializer.data)

# Statistiques pour le dashboard Coach
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coach_dashboard_stats(request):
    if request.user.role != 'coach':
        return Response({'error': 'Access denied'}, status=403)

    stats = {
        'pending': Component.objects.filter(status='pending').count(),
        'approved': Component.objects.filter(status='approved').count(),
        'rejected': Component.objects.filter(status='rejected').count(),
    }
    return Response(stats)
# Composants en attente pour les Coachs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def coach_pending_components(request):
    if request.user.role != 'coach':
        return Response({'error': 'Accès refusé'}, status=403)

    components = Component.objects.filter(status='pending')
    serializer = ComponentSerializer(components, many=True)
    return Response(serializer.data)

# Liste des catégories de composants
@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    categories = [
        {'value': code, 'label': label}
        for code, label in Component.CATEGORIES
    ]
    return Response(categories)