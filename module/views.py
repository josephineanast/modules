from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Product
from .forms import ProductForm
from modular_engine.class_views.module_manager import ModuleManager
from django.http import Http404

MANAGER_GROUP = 'product_manager'
USER_GROUP = 'product_user'
PUBLIC_GROUP = 'product_public'

class ModuleAccessMixin:
    """Mixin to check if the module is installed."""
    def dispatch(self, request, *args, **kwargs):
        if not ModuleManager.is_module_installed('module'):
            raise Http404("Module not installed")
        return super().dispatch(request, *args, **kwargs)

class ProductListView(ModuleAccessMixin, ListView):
    """List all products - accessible to all users (public, user, manager)."""
    model = Product
    template_name = 'module/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(barcode__icontains=search_query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        
        user = self.request.user
        context['is_manager'] = user.groups.filter(name=MANAGER_GROUP).exists() if user.is_authenticated else False
        context['is_user'] = user.groups.filter(name=USER_GROUP).exists() if user.is_authenticated else False
        
        return context

class ProductDetailView(ModuleAccessMixin, DetailView):
    """View product details - accessible to all roles."""
    model = Product
    template_name = 'module/product_detail.html'

class ProductCreateView(ModuleAccessMixin, LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new product - accessible to user and manager roles."""
    model = Product
    form_class = ProductForm
    template_name = 'module/product_form.html'
    permission_required = 'module.add_product'
    success_url = reverse_lazy('module:product_list')
    
    def get_permission_denied_message(self):
        return "You don't have permission to create products."
    
    def handle_no_permission(self):
        messages.error(self.request, self.get_permission_denied_message())
        return redirect('module:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Product created successfully")
        return super().form_valid(form)

class ProductUpdateView(ModuleAccessMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update a product - accessible to user and manager roles."""
    model = Product
    form_class = ProductForm
    template_name = 'module/product_form.html'
    permission_required = 'module.change_product'
    success_url = reverse_lazy('module:product_list')
    
    def get_permission_denied_message(self):
        return "You don't have permission to update products."
    
    def handle_no_permission(self):
        messages.error(self.request, self.get_permission_denied_message())
        return redirect('module:product_list')

    def form_valid(self, form):
        messages.success(self.request, "Product updated successfully")
        return super().form_valid(form)

class ProductDeleteView(ModuleAccessMixin, LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete a product - accessible only to manager role."""
    model = Product
    template_name = 'module/product_confirm_delete.html'
    permission_required = 'module.delete_product'
    success_url = reverse_lazy('module:product_list')
    
    def get_permission_denied_message(self):
        return "You don't have permission to delete products."
    
    def handle_no_permission(self):
        messages.error(self.request, self.get_permission_denied_message())
        return redirect('module:product_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Product deleted successfully")
        return super().delete(request, *args, **kwargs)