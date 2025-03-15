"""
URL configuration for hashmicro_modules project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from modular_engine.class_views.module_registry import registry
from module.module_info import MODULE_INFO

urlpatterns = [
    path('', RedirectView.as_view(url='/engine/login/', permanent=False), name='root_redirect'),
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path("engine/", include('modular_engine.urls')),
    path(f"module/{MODULE_INFO['url_prefix']}/", include('module.urls')),
]
