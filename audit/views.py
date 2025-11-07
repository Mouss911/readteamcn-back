from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer
from users.permissions import IsAdmin

User = get_user_model()


class AuditLogPagination(PageNumberPagination):
    """Pagination pour les logs d'audit"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


@api_view(['GET'])
@permission_classes([IsAdmin])
def list_audit_logs(request):
    """
    Liste tous les logs d'audit avec filtres
    
    Query params:
        - action: Filtrer par type d'action
        - user_id: Filtrer par user qui a fait l'action
        - target_user_id: Filtrer par user ciblé
        - severity: Filtrer par niveau de criticité (info/warning/critical)
        - date_from: Date de début (format: YYYY-MM-DD)
        - date_to: Date de fin (format: YYYY-MM-DD)
        - search: Recherche dans la description
        - page: Numéro de page
        - page_size: Nombre d'éléments par page (défaut: 50, max: 200)
    """
    logs = AuditLog.objects.all()
    
    # Filtres
    action = request.query_params.get('action')
    if action:
        logs = logs.filter(action=action)
    
    user_id = request.query_params.get('user_id')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    target_user_id = request.query_params.get('target_user_id')
    if target_user_id:
        logs = logs.filter(target_user_id=target_user_id)
    
    severity = request.query_params.get('severity')
    if severity:
        logs = logs.filter(severity=severity)
    
    # Filtre par date
    date_from = request.query_params.get('date_from')
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            logs = logs.filter(timestamp__gte=date_from)
        except ValueError:
            pass
    
    date_to = request.query_params.get('date_to')
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Inclure toute la journée
            date_to = date_to.replace(hour=23, minute=59, second=59)
            logs = logs.filter(timestamp__lte=date_to)
        except ValueError:
            pass
    
    # Recherche dans la description
    search = request.query_params.get('search')
    if search:
        logs = logs.filter(description__icontains=search)
    
    # Pagination
    paginator = AuditLogPagination()
    page = paginator.paginate_queryset(logs, request)
    
    if page is not None:
        serializer = AuditLogListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = AuditLogListSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def audit_log_detail(request, log_id):
    """
    Détails d'un log d'audit spécifique
    """
    try:
        log = AuditLog.objects.get(id=log_id)
    except AuditLog.DoesNotExist:
        return Response(
            {'detail': 'Log introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = AuditLogSerializer(log)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def audit_stats(request):
    """
    Statistiques des logs d'audit
    
    Retourne:
        - Total des logs
        - Logs par action
        - Logs par sévérité
        - Logs des dernières 24h
        - Logs de la dernière semaine
    """
    total_logs = AuditLog.objects.count()
    
    # Logs par action
    logs_by_action = {}
    for action, label in AuditLog.ACTION_CHOICES:
        count = AuditLog.objects.filter(action=action).count()
        if count > 0:
            logs_by_action[action] = {
                'label': label,
                'count': count
            }
    
    # Logs par sévérité
    logs_by_severity = {
        'info': AuditLog.objects.filter(severity='info').count(),
        'warning': AuditLog.objects.filter(severity='warning').count(),
        'critical': AuditLog.objects.filter(severity='critical').count(),
    }
    
    # Logs récents
    now = timezone.now()
    last_24h = AuditLog.objects.filter(timestamp__gte=now - timedelta(hours=24)).count()
    last_7days = AuditLog.objects.filter(timestamp__gte=now - timedelta(days=7)).count()
    last_30days = AuditLog.objects.filter(timestamp__gte=now - timedelta(days=30)).count()
    
    return Response({
        'total_logs': total_logs,
        'logs_by_action': logs_by_action,
        'logs_by_severity': logs_by_severity,
        'recent_logs': {
            'last_24h': last_24h,
            'last_7days': last_7days,
            'last_30days': last_30days
        }
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def user_activity(request, user_id):
    """
    Historique d'activité d'un user spécifique
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'User introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Logs où le user a fait l'action
    logs_as_actor = AuditLog.objects.filter(user=user)
    
    # Logs où le user est la cible
    logs_as_target = AuditLog.objects.filter(target_user=user)
    
    # Combiner et trier
    all_logs = (logs_as_actor | logs_as_target).distinct().order_by('-timestamp')
    
    # Pagination
    paginator = AuditLogPagination()
    page = paginator.paginate_queryset(all_logs, request)
    
    if page is not None:
        serializer = AuditLogListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = AuditLogListSerializer(all_logs, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdmin])
def cleanup_old_logs(request):
    """
    Supprimer les logs plus vieux que X jours
    
    Query params:
        - days: Nombre de jours (défaut: 90)
    """
    days = int(request.query_params.get('days', 90))
    
    if days < 30:
        return Response(
            {'detail': 'Impossible de supprimer des logs de moins de 30 jours'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()[0]
    
    return Response({
        'message': f'{deleted_count} logs supprimés (plus vieux que {days} jours)',
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date
    })