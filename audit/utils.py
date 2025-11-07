from .models import AuditLog
from django.contrib.auth import get_user_model

User = get_user_model()


def create_audit_log(
    action,
    user=None,
    target_user=None,
    target_model=None,
    target_id=None,
    description='',
    changes=None,
    ip_address=None,
    user_agent=None,
    severity='info'
):
    """
    Créer un log d'audit
    
    Args:
        action (str): Type d'action (voir ACTION_CHOICES dans AuditLog)
        user (User): User qui effectue l'action
        target_user (User): User cible de l'action (optionnel)
        target_model (str): Type de l'objet ciblé (optionnel)
        target_id (str/int): ID de l'objet ciblé (optionnel)
        description (str): Description lisible
        changes (dict): Détails des changements (avant/après)
        ip_address (str): Adresse IP
        user_agent (str): User-Agent du navigateur
        severity (str): 'info', 'warning', ou 'critical'
    
    Returns:
        AuditLog: L'objet log créé
    
    Usage:
        create_audit_log(
            action='user_login',
            user=request.user,
            ip_address=get_client_ip(request),
            description=f"User {request.user.email} logged in"
        )
    """
    return AuditLog.objects.create(
        user=user,
        action=action,
        target_user=target_user,
        target_model=target_model,
        target_id=str(target_id) if target_id else None,
        description=description,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
        severity=severity
    )


def get_client_ip(request):
    """
    Extraire l'IP du client depuis la requête
    
    Args:
        request: Django request object
    
    Returns:
        str: Adresse IP du client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_user_action(request, action, target_user=None, description='', changes=None, severity='info'):
    """
    Helper rapide pour logger une action user avec contexte de la requête
    
    Args:
        request: Django request object
        action (str): Type d'action
        target_user (User): User cible (optionnel)
        description (str): Description
        changes (dict): Changements
        severity (str): Niveau de criticité
    
    Returns:
        AuditLog: L'objet log créé
    """
    return create_audit_log(
        action=action,
        user=request.user if request.user.is_authenticated else None,
        target_user=target_user,
        description=description,
        changes=changes,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity=severity
    )