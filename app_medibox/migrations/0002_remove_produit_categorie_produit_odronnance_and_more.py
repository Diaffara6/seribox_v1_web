# Generated by Django 4.1.5 on 2023-09-07 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_medibox', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produit',
            name='categorie',
        ),
        migrations.AddField(
            model_name='produit',
            name='odronnance',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Categorie',
        ),
    ]
