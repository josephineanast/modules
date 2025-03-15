from django.db import connection, transaction
from django.apps import apps
from django.utils import timezone
from django.core.management import call_command
import importlib
from ..models import Module
from .module_registry import registry
import logging

logger = logging.getLogger(__name__)

class ModuleManager:
    @staticmethod
    def install_module(app_name):
        """Install a module by app name"""
        module_info = registry.get_module_info(app_name)
        if not module_info:
            raise ValueError(f"Module {app_name} not found")
        
        with transaction.atomic():
            module, created = Module.objects.get_or_create(
                app_name=app_name,
                defaults={
                    'name': module_info.get('name', app_name),
                    'version': module_info.get('version', '0.1.0'),
                    'description': module_info.get('description', ''),
                    'installed': True,
                    'installation_date': timezone.now(),
                }
            )
            
            if not created:
                module.installed = True
                module.installation_date = timezone.now()
                module.save()
            
            call_command('migrate', app_name)
            
            try:
                install_module = importlib.import_module(f"{app_name}.install")
                if hasattr(install_module, 'install'):
                    install_module.install()
            except (ImportError, AttributeError):
                pass
                
        return module
            
    @staticmethod
    def uninstall_module(app_name):
        """Uninstall a module by app name"""
        try:
            module = Module.objects.get(app_name=app_name, installed=True)
        except Module.DoesNotExist:
            raise ValueError(f"Module {app_name} is not installed")
        
        with transaction.atomic():
            try:
                uninstall_module = importlib.import_module(f"{app_name}.install")
                if hasattr(uninstall_module, 'uninstall'):
                    uninstall_module.uninstall()
            except (ImportError, AttributeError) as e:
                logger.warning(f"No install method found for {app_name}: {e}")
            
            module.installed = False
            module.save()
            
        return module
    
    @staticmethod
    def upgrade_module(app_name):
        """Upgrade a module by app name"""
        try:
            module = Module.objects.get(app_name=app_name, installed=True)
        except Module.DoesNotExist:
            raise ValueError(f"Module {app_name} is not installed")
        
        module_info = registry.get_module_info(app_name)
        if not module_info:
            raise ValueError(f"Module info for {app_name} not found")
        
        with transaction.atomic():
            current_version = module.version
            new_version = module_info.get('version', module.version)
            
            logger.info(f"Upgrading module {app_name} from {current_version} to {new_version}")
            
            call_command('migrate', app_name)
            
            try:
                upgrade_module = importlib.import_module(f"{app_name}.install")
                if hasattr(upgrade_module, 'upgrade'):
                    updated_config = upgrade_module.upgrade(module.config)
                    if updated_config:
                        module.config = updated_config
            except (ImportError, AttributeError) as e:
                logger.warning(f"Error during upgrade of {app_name}: {e}")
            
            module.version = new_version
            module.save()
                
        return module
    
    @staticmethod
    def is_module_installed(app_name):
        """Check if a module is installed"""
        try:
            return Module.objects.get(app_name=app_name).installed
        except Module.DoesNotExist:
            return False