from django.db import models
from django.db.models import JSONField

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    app_name = models.CharField(max_length=100, unique=True)
    version = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    installed = models.BooleanField(default=False)
    installation_date = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    config = JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} ({self.version})"
    
    class Meta:
        ordering = ['name']