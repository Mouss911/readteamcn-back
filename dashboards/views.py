# developer_dashboard, coach_dashboard, admin_dashboard

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Si vous avez des permissions personnalisées, décommentez l'import ci-dessous
# et assurez-vous d'implémenter IsDeveloper / IsCoach / IsAdmin dans dashboards/permissions.py
# from .permissions import IsDeveloper, IsCoach, IsAdmin

from .serializers import DeveloperDashboardSerializer, CoachDashboardSerializer, AdminDashboardSerializer

class DeveloperDashboardView(APIView):
    # Remplacez IsAuthenticated par [IsAuthenticated, IsDeveloper] après avoir créé IsDeveloper
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = {}  # TODO: construire la payload (brouillons, soumissions, etc.)
        serializer = DeveloperDashboardSerializer(instance=data)
        return Response(serializer.data)

class CoachDashboardView(APIView):
    # Remplacez IsAuthenticated par [IsAuthenticated, IsCoach] après avoir créé IsCoach
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = {}  # TODO: construire la payload (file d’attente, validations)
        serializer = CoachDashboardSerializer(instance=data)
        return Response(serializer.data)

class AdminDashboardView(APIView):
    # Remplacez IsAuthenticated par [IsAuthenticated, IsAdmin] après avoir créé IsAdmin
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = {}  # TODO: construire la payload (KPIs, audit)
        serializer = AdminDashboardSerializer(instance=data)
        return Response(serializer.data)