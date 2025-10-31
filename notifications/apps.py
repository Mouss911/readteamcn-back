# apps.py
from django.apps import AppConfig
import importlib

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        importlib.import_module('notifications.signals')  # Chargement propre