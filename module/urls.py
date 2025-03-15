from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)

app_name = 'module' 

urlpatterns = [
    # List all products
    path('', ProductListView.as_view(), name='product_list'),
    
    # Product detail view
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Create a new product
    path('create/', ProductCreateView.as_view(), name='product_create'),
    
    # Update a product
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    
    # Delete a product
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
]