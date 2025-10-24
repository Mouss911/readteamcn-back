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
    components = Component.objects.all()
    serializer = ComponentSerializer(components, many=True)
    return Response(serializer.data)