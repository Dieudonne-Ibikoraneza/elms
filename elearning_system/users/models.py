from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    def __str__(self):
        return self.username

def profile_image_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    # Create filename as user_id.extension
    filename = f'{instance.user.id}.{ext}'
    return os.path.join('profile_images', filename)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

# Signal to create profile
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()