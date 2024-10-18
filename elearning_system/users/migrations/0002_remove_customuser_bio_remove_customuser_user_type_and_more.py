# Generated by Django 5.1.3 on 2024-11-12 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='user_type',
        ),
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Admin')], default='student', max_length=20),
        ),
    ]