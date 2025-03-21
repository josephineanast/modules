# Generated by Django 5.1.7 on 2025-03-08 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Module",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("app_name", models.CharField(max_length=100, unique=True)),
                ("version", models.CharField(max_length=20)),
                ("description", models.TextField(blank=True)),
                ("installed", models.BooleanField(default=False)),
                ("installation_date", models.DateTimeField(blank=True, null=True)),
                ("last_update", models.DateTimeField(auto_now=True)),
                ("config", models.JSONField(default=dict)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
