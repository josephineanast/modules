import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class ModularEngineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modular_engine"
    verbose_name = 'Modular Engine'
    
    def ready(self):
        """Perform initialization tasks when the app is ready."""
        logger.info(f"{self.verbose_name} app is ready.")
        
        from modular_engine.signals import register_signals
        register_signals()