# Generated by Django 4.2.5 on 2023-09-13 21:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_medecin', '0003_medecin'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='utilisateur',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
