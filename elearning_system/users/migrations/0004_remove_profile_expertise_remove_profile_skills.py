# Generated by Django 5.1.3 on 2024-11-23 15:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_remove_profile_avatar_profile_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='expertise',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='skills',
        ),
    ]
