# Generated by Django 5.0.12 on 2025-04-18 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thoughtswap', '0008_promptuse_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='is_swapping',
            field=models.BooleanField(default=False),
        ),
    ]
