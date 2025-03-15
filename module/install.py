import logging
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db import connection

logger = logging.getLogger(__name__)

MANAGER_GROUP = 'product_manager'
USER_GROUP = 'product_user'
PUBLIC_GROUP = 'product_public'

def assign_permissions(group, permissions):
    """Helper function to assign permissions to a group."""
    for permission in permissions:
        group.permissions.add(permission)

def install():
    """Set up user roles and permissions when the module is installed."""
    from .models import Product
    
    with transaction.atomic():
        manager_group, _ = Group.objects.get_or_create(name=MANAGER_GROUP)
        user_group, _ = Group.objects.get_or_create(name=USER_GROUP)
        public_group, _ = Group.objects.get_or_create(name=PUBLIC_GROUP)
        
        content_type = ContentType.objects.get_for_model(Product)
        
        permissions = {
            'view': Permission.objects.get(content_type=content_type, codename='view_product'),
            'add': Permission.objects.get(content_type=content_type, codename='add_product'),
            'change': Permission.objects.get(content_type=content_type, codename='change_product'),
            'delete': Permission.objects.get(content_type=content_type, codename='delete_product'),
        }
        
        assign_permissions(manager_group, permissions.values())
        
        assign_permissions(user_group, [permissions['view'], permissions['add'], permissions['change']])
        
        assign_permissions(public_group, [permissions['view']])
        
        for user in User.objects.filter(is_staff=True):
            user.groups.add(manager_group)
        
        logger.info("Module installed successfully with roles and permissions.")

def upgrade(config):
    """Handle updates when the module is upgraded."""
    logger.info("Upgrading module...")
    
    from .module_info import MODULE_INFO
    current_version = MODULE_INFO.get('version', '1.0.0')
    old_version = config.get('version', '0.0.0')
    
    with transaction.atomic():
        install()
        
        if old_version < '1.1.0' and current_version >= '1.1.0':
            logger.info("Adding 'description' field to Product model")
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE module_product ADD COLUMN description TEXT NULL"
                )
        
        if old_version < '1.2.0' and current_version >= '1.2.0':
            logger.info("Adding 'category' field to Product model")
            with connection.cursor() as cursor:
                cursor.execute(
                    "ALTER TABLE module_product ADD COLUMN category VARCHAR(100) NULL"
                )
                
        config['version'] = current_version
        
        logger.info(f"Module upgraded from {old_version} to {current_version}")
    
    return config

def uninstall():
    """Clean up when the module is uninstalled."""
    with transaction.atomic():
        for group_name in [MANAGER_GROUP, USER_GROUP, PUBLIC_GROUP]:
            try:
                group = Group.objects.get(name=group_name)
                group.delete()
                logger.info(f"Deleted group: {group_name}")
            except Group.DoesNotExist:
                logger.warning(f"Group {group_name} does not exist.")
        
        logger.info("Module uninstalled successfully.")