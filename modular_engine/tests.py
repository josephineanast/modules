from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse
from .class_views.module_manager import ModuleManager
from .class_views.module_registry import registry
from .views import ModuleListView, InstallModuleView, UninstallModuleView, UpgradeModuleView
class ModuleManagerTests(TestCase):
    def setUp(self):
        self.app_name = 'module'  
        self.module_info = registry.get_module_info(self.app_name)
        if not self.module_info:
            raise ValueError(f"Module info for {self.app_name} not found")

    def test_install_module(self):
        module = ModuleManager.install_module(self.app_name)
        self.assertEqual(module.app_name, self.app_name)
        self.assertEqual(module.name, self.module_info.get('name', self.app_name))
        self.assertEqual(module.version, self.module_info.get('version', '0.1.0'))
        self.assertEqual(module.description, self.module_info.get('description', ''))
        self.assertTrue(module.installed)

    def test_uninstall_module(self):
        ModuleManager.install_module(self.app_name)
        module = ModuleManager.uninstall_module(self.app_name)
        self.assertFalse(module.installed)

    def test_upgrade_module(self):
        ModuleManager.install_module(self.app_name)
        new_version = '2.0.0'
        registry.modules[self.app_name]['version'] = new_version  
        module = ModuleManager.upgrade_module(self.app_name)
        self.assertEqual(module.version, new_version)

    def test_is_module_installed(self):
        self.assertFalse(ModuleManager.is_module_installed(self.app_name))
        ModuleManager.install_module(self.app_name)
        self.assertTrue(ModuleManager.is_module_installed(self.app_name))

class ModuleRegistryTests(TestCase):
    def setUp(self):
        self.app_name = 'module' 
        self.module_info = registry.get_module_info(self.app_name)
        if not self.module_info:
            raise ValueError(f"Module info for {self.app_name} not found")

    def test_discover_modules(self):
        registry.modules = {}
        modules = registry.discover_modules()
        self.assertIn(self.app_name, modules) 

    def test_get_module_info(self):
        module_info = registry.get_module_info(self.app_name)
        self.assertEqual(module_info, self.module_info)

    def test_get_all_modules(self):
        modules = registry.get_all_modules()
        self.assertIn(self.app_name, modules)

class ModuleListViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)

    def test_module_list_view(self):
        request = self.factory.get(reverse('modular_engine:module_list'))
        request.user = self.user
        response = ModuleListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

class InstallModuleViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)

    def test_install_module_view(self):
        request = self.factory.post(reverse('modular_engine:install_module', args=['test_app']))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = InstallModuleView.as_view()(request, app_name='test_app')
        self.assertEqual(response.status_code, 302)

class UninstallModuleViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)

        self.module = ModuleManager.install_module('module')

    def test_uninstall_module_view(self):
        request = self.factory.post(reverse('modular_engine:uninstall_module', args=['module']))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = UninstallModuleView.as_view()(request, app_name='module')
        self.assertEqual(response.status_code, 302)

class UpgradeModuleViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)

        self.module = ModuleManager.install_module('module')

    def test_upgrade_module_view(self):
        request = self.factory.post(reverse('modular_engine:upgrade_module', args=['module']))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = UpgradeModuleView.as_view()(request, app_name='module')
        self.assertEqual(response.status_code, 302)

class SignupViewTests(TestCase):
    def test_signup_view(self):
        response = self.client.post(reverse('modular_engine:signup'), {
            'username': 'newuser',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(response.status_code, 302)

class UserManagementViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='admin')
        self.user.groups.add(self.group)

    def test_user_management_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('modular_engine:user_management'))
        self.assertEqual(response.status_code, 200)

    def test_assign_user_role_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('modular_engine:assign_user_role', args=[self.user.id]), {
            'group_id': self.group.id,
        })
        self.assertEqual(response.status_code, 302)