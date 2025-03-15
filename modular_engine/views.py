from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Module
from .class_views.module_registry import registry
from .class_views.module_manager import ModuleManager
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test

class IsAdminMixin(UserPassesTestMixin):
    """Mixin to ensure the user is an admin"""
    def test_func(self):
        return self.request.user.is_authenticated 

class ModuleListView(LoginRequiredMixin, IsAdminMixin, View):
    """List all available and installed modules"""
    def get(self, request):
        available_modules = registry.get_all_modules()
        installed_modules = {m.app_name: m for m in Module.objects.all()}
        
        modules_data = []
        for app_name, module_info in available_modules.items():
            module_data = {
                'app_name': app_name,
                'name': module_info.get('name', app_name),
                'description': module_info.get('description', ''),
                'version': module_info.get('version', '0.1.0'),
                'installed': False,
                'db_record': None
            }
            
            if app_name in installed_modules:
                module_data['installed'] = installed_modules[app_name].installed
                module_data['db_record'] = installed_modules[app_name]
                
            modules_data.append(module_data)
        
        return render(request, 'modular_engine/modular_list.html', {
            'modules': modules_data
        })

class InstallModuleView(LoginRequiredMixin, IsAdminMixin, View):
    """Install a module"""
    def post(self, request, app_name):
        try:
            ModuleManager.install_module(app_name)
            messages.success(request, f"Module '{app_name}' installed successfully")
            module_info = registry.get_module_info(app_name)
            if module_info and 'url_prefix' in module_info:
                url_prefix = module_info['url_prefix']
                return redirect(reverse(f"{app_name}:product_list"))
        except Exception as e:
            messages.error(request, f"Error installing module: {str(e)}")
        return redirect('modular_engine:module_list')

class UninstallModuleView(LoginRequiredMixin, IsAdminMixin, View):
    """Uninstall a module"""
    def post(self, request, app_name):
        try:
            ModuleManager.uninstall_module(app_name)
            messages.success(request, f"Module '{app_name}' uninstalled successfully")
        except Exception as e:
            messages.error(request, f"Error uninstalling module: {str(e)}")
        return redirect('modular_engine:module_list')

class UpgradeModuleView(LoginRequiredMixin, IsAdminMixin, View):
    """Upgrade a module"""
    def post(self, request, app_name):
        try:
            ModuleManager.upgrade_module(app_name)
            messages.success(request, f"Module '{app_name}' upgraded successfully")
        except Exception as e:
            messages.error(request, f"Error upgrading module: {str(e)}")
        return redirect('modular_engine:module_list')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            return redirect('modular_engine:module_list')
    return render(request, 'modular_engine/signup.html')


@login_required  
def user_management(request):
    """View for managing users and their roles"""
    users = User.objects.all().prefetch_related('groups')
    groups = Group.objects.all()
    
    return render(request, 'modular_engine/user_management.html', {
        'users': users,
        'groups': groups
    })

@login_required  
def assign_user_role(request, user_id):
    """Assign a role/group to a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        group_id = request.POST.get('group_id')
        
        user.groups.clear()
        
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            user.groups.add(group)
            messages.success(request, f"User {user.username} assigned to {group.name} role")
        else:
            messages.success(request, f"User {user.username} removed from all roles")
            
    return redirect('modular_engine:user_management')