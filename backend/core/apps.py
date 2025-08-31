# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # ленивое подключение, чтобы избежать круговых импортов
        from . import signals
        signals.connect_signals()
