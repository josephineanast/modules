from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views


app_name = 'modular_engine'
urlpatterns = [
    path('modules/', ModuleListView.as_view(), name='module_list'),
    path('modules/install/<str:app_name>/', InstallModuleView.as_view(), name='install_module'),
    path('modules/uninstall/<str:app_name>/', UninstallModuleView.as_view(), name='uninstall_module'),
    path('modules/upgrade/<str:app_name>/', UpgradeModuleView.as_view(), name='upgrade_module'),
    path('login/', auth_views.LoginView.as_view(template_name='modular_engine/login.html'), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='/engine/login/'), name='logout'),
    path('signup/', signup, name='signup'),
    path('users/', user_management, name='user_management'),
    path('users/<int:user_id>/assign-role/', assign_user_role, name='assign_user_role'),
]