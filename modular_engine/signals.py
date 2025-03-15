import logging
import json
from django.db.models.signals import post_migrate, pre_migrate
from django.dispatch import receiver
from .class_views.module_registry import registry
from django.utils import timezone
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

def backup_registry():
    """Backup the module registry to a JSON file."""
    try:
        # Get the registry data
        registry_data = {
            "modules": registry.modules,
            "last_updated": timezone.now().isoformat()
        }
        
        # Define the backup file path
        backup_dir = Path(settings.BASE_DIR) / "backups"
        backup_dir.mkdir(exist_ok=True)  # Create the backup directory if it doesn't exist
        backup_file = backup_dir / "module_registry_backup.json"
        
        # Write the registry data to the backup file
        with open(backup_file, "w") as f:
            json.dump(registry_data, f, indent=4)
        
        logger.info(f"Module registry backup saved to {backup_file}")
    except Exception as e:
        logger.error(f"Error backing up module registry: {e}")
        raise


def register_signals():
    """Register all signals for the modular_engine app."""
    post_migrate.connect(handle_post_migrate)
    pre_migrate.connect(handle_pre_migrate)

@receiver(post_migrate)
def handle_post_migrate(sender, **kwargs):
    """Update module registry after migrations are applied"""
    if sender.name == 'modular_engine':
        logger.info("Updating module registry after migrations...")
        try:
            registry.discover_modules()
            logger.info(f"Discovered {len(registry.modules)} modules.")
        except Exception as e:
            logger.error(f"Error updating module registry: {e}")

@receiver(pre_migrate)
def handle_pre_migrate(sender, **kwargs):
    """Perform tasks before migrations are applied"""
    if sender.name == 'modular_engine':
        logger.info("Preparing for migrations...")
        try:
            backup_registry()
            logger.info("Module registry backup completed.")
        except Exception as e:
            logger.error(f"Error backing up module registry: {e}")

def restore_registry():
    """Restore the module registry from a backup file."""
    try:
        backup_file = Path(settings.BACKUP_DIR) / "module_registry_backup.json"
        
        if backup_file.exists():
            with open(backup_file, "r") as f:
                registry_data = json.load(f)
                registry.modules = registry_data.get("modules", {})
                logger.info(f"Module registry restored from {backup_file}")
        else:
            logger.warning("No backup file found to restore.")
    except Exception as e:
        logger.error(f"Error restoring module registry: {e}")
        raise