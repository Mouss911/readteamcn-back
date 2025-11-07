from django.urls import path
from . import views

urlpatterns = [
    # Liste et filtres
    path('logs/', views.list_audit_logs, name='audit-logs-list'),
    path('logs/<uuid:log_id>/', views.audit_log_detail, name='audit-log-detail'),
    
    # Statistiques
    path('stats/', views.audit_stats, name='audit-stats'),
    
    # Activité d'un user
    path('user/<int:user_id>/activity/', views.user_activity, name='user-activity'),
    
    # Nettoyage
    path('cleanup/', views.cleanup_old_logs, name='audit-cleanup'),
]