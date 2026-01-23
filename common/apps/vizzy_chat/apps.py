"""
Vizzy Chat Application Configuration
"""
from django.apps import AppConfig


class VizzyChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vizzy_chat'
    verbose_name = 'Vizzy AI Chat'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.vizzy_chat.signals  # noqa
        except ImportError:
            pass
