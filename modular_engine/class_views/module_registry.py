import importlib
from django.apps import apps
from django.conf import settings

class ModuleRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleRegistry, cls).__new__(cls)
            cls._instance.modules = {}
        return cls._instance
    
    def discover_modules(self):
        """Discover all modules with module_info.py files"""
        for app_config in apps.get_app_configs():
            try:
                module_info = importlib.import_module(f"{app_config.name}.module_info")
                if hasattr(module_info, 'MODULE_INFO'):
                    if 'url_prefix' not in module_info.MODULE_INFO:
                        module_info.MODULE_INFO['url_prefix'] = module_info.MODULE_INFO.get('name', "module").lower().replace(' ', '-')
                    self.modules[app_config.name] = module_info.MODULE_INFO
            except ImportError:
                continue
        return self.modules
    
    def get_module_info(self, app_name):
        """Get module info for a specific app"""
        if app_name not in self.modules:
            self.discover_modules()
        return self.modules.get(app_name)
    
    def get_all_modules(self):
        """Get info for all discovered modules"""
        self.discover_modules()
        return self.modules


registry = ModuleRegistry()