from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Component
from .serializers import ComponentSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_component(request):
    serializer = ComponentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_components(request):
    components = Component.objects.filter(status='approved')  # SEULEMENT VALIDÉS
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

    return Response({
        'message': f'Composant {action == "approve" and "validé" or "rejeté"}',
        'status': component.status
    })