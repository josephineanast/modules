from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from modular_engine.models import Module
from .models import Product
from .forms import ProductForm
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
)
from .install import install, upgrade, uninstall, MANAGER_GROUP, USER_GROUP, PUBLIC_GROUP

class InstallTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345', is_staff=True)
        self.non_staff_user = User.objects.create_user(username='nonstaff', password='12345')

    def test_install(self):
        """Test that the install function creates groups and assigns permissions."""
        install()

        # Check that groups were created
        self.assertTrue(Group.objects.filter(name=MANAGER_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=USER_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=PUBLIC_GROUP).exists())

        # Check that permissions were assigned
        manager_group = Group.objects.get(name=MANAGER_GROUP)
        user_group = Group.objects.get(name=USER_GROUP)
        public_group = Group.objects.get(name=PUBLIC_GROUP)

        content_type = ContentType.objects.get_for_model(Product)
        permissions = Permission.objects.filter(content_type=content_type)

        self.assertEqual(manager_group.permissions.count(), 4)  # view, add, change, delete
        self.assertEqual(user_group.permissions.count(), 3)  # view, add, change
        self.assertEqual(public_group.permissions.count(), 1)  # view

        # Check that staff users were added to the manager group
        self.assertTrue(self.user.groups.filter(name=MANAGER_GROUP).exists())
        self.assertFalse(self.non_staff_user.groups.filter(name=MANAGER_GROUP).exists())

    def test_upgrade(self):
        """Test that the upgrade function updates the module."""
        config = {'version': '0.0.0'}
        new_config = upgrade(config)

        # Check that the version was updated
        self.assertEqual(new_config['version'], '1.0.0')

        # Check that the install function was called
        self.assertTrue(Group.objects.filter(name=MANAGER_GROUP).exists())

    def test_uninstall(self):
        """Test that the uninstall function removes groups."""
        install()  # Ensure groups exist
        uninstall()

        # Check that groups were deleted
        self.assertFalse(Group.objects.filter(name=MANAGER_GROUP).exists())
        self.assertFalse(Group.objects.filter(name=USER_GROUP).exists())
        self.assertFalse(Group.objects.filter(name=PUBLIC_GROUP).exists())

class ProductFormTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', barcode='12345', price=10.0, stock=5)

    def test_clean_barcode_unique(self):
        """Test that the barcode field must be unique."""
        form = ProductForm(data={'name': 'New Product', 'barcode': '12345', 'price': 10.0, 'stock': 5})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['barcode'], ['A product with this barcode already exists.'])

    def test_clean_barcode_valid(self):
        """Test that a unique barcode is valid."""
        form = ProductForm(data={'name': 'New Product', 'barcode': '67890', 'price': 10.0, 'stock': 5})
        self.assertTrue(form.is_valid())

class ProductViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.staff_user = User.objects.create_user(username='staffuser', password='12345', is_staff=True)
        self.product = Product.objects.create(name='Test Product', barcode='12345', price=10.0, stock=5)

        # Install the module and set up groups and permissions
        install()

        # Mark the module as installed in the database
        Module.objects.create(
            app_name='module',
            name='Products',
            version='1.0.0',
            description="Manage store's products",
            installed=True,
            installation_date='2023-10-01T00:00:00Z',
        )

    def test_product_list_view(self):
        """Test that the product list view works."""
        request = self.factory.get(reverse('module:product_list'))
        request.user = self.user
        response = ProductListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context_data)

    def test_product_detail_view(self):
        """Test that the product detail view works."""
        request = self.factory.get(reverse('module:product_detail', args=[self.product.pk]))
        request.user = self.user
        response = ProductDetailView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object'], self.product)

    def test_product_create_view_permission(self):
        """Test that only users with the add_product permission can create products."""
        request = self.factory.post(reverse('module:product_create'), {
            'name': 'New Product',
            'barcode': '67890',
            'price': 10.0,
            'stock': 5,
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        response = ProductCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)  # Redirects to product list
        self.assertEqual(messages_storage._queued_messages[0].message, "You don't have permission to create products.")

    def test_product_update_view_permission(self):
        """Test that only users with the change_product permission can update products."""
        request = self.factory.post(reverse('module:product_update', args=[self.product.pk]), {
            'name': 'Updated Product',
            'barcode': '12345',
            'price': 15.0,
            'stock': 10,
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        response = ProductUpdateView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 302)  # Redirects to product list
        self.assertEqual(messages_storage._queued_messages[0].message, "You don't have permission to update products.")

    def test_product_delete_view_permission(self):
        """Test that only users with the delete_product permission can delete products."""
        request = self.factory.post(reverse('module:product_delete', args=[self.product.pk]))
        request.user = self.user
        setattr(request, 'session', 'session')
        messages_storage = FallbackStorage(request)
        setattr(request, '_messages', messages_storage)

        response = ProductDeleteView.as_view()(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 302)  # Redirects to product list
        self.assertEqual(messages_storage._queued_messages[0].message, "You don't have permission to delete products.")