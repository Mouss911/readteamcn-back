from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AuditLog, Notification, TokenSet, Membership, Review, KpiEvent
from .serializers import AuditLogSerializer, NotificationSerializer, TokenSetSerializer, MembershipSerializer, ReviewSerializer, KpiEventSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

    @action(detail=False, methods=['get'])
    def export_csv(self, request, *args, **kwargs):
        # Logique d'export CSV (à implémenter)
        return Response({"message": "Export CSV not implemented yet"})

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

    @action(detail=True, methods=['patch'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"})

class TokenSetViewSet(viewsets.ModelViewSet):
    queryset = TokenSet.objects.all()
    serializer_class = TokenSetSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

    @action(detail=False, methods=['post'])
    def invite(self, request, *args, **kwargs):
        # Logique d'invitation (à implémenter)
        return Response({"message": "Invite not implemented yet"})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.decision = 'approved'
        review.save()
        return Response({"status": "approved"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.decision = 'rejected'
        review.notes = request.data.get('notes', '')
        review.save()
        return Response({"status": "rejected"})

class KpiEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = KpiEvent.objects.all()
    serializer_class = KpiEventSerializer
    permission_classes = [permissions.AllowAny]  # Temporairement sans authentification

    @action(detail=False, methods=['get'])
    def top_components(self, request, *args, **kwargs):
        # Logique pour les top composants (à implémenter)
        return Response({"message": "Top components not implemented yet"})