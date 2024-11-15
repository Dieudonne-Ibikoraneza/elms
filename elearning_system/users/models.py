from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

class CustomUser(AbstractUser):
    STUDENT = 'student'
    INSTRUCTOR = 'instructor'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (INSTRUCTOR, 'Instructor'),
        (ADMIN, 'Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT,
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

def profile_image_path(instance, filename):
    # Get the file extension
    ext = filename.split('.')[-1]
    # Create filename as user_id.extension
    filename = f'{instance.user.id}.{ext}'
    return os.path.join('profile_images', filename)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=profile_image_path, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def save(self, *args, **kwargs):
        # Delete old avatar file when updating
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.avatar and self.avatar != old_profile.avatar:
                    old_profile.avatar.delete(save=False)
            except Profile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Get or create profile for existing users
        Profile.objects.get_or_create(user=instance)