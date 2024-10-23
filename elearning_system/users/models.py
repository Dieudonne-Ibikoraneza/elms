from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import os

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk:
            # If this is an update, not a create
            orig = CustomUser.objects.get(pk=self.pk)
            if orig.username != self.username:
                # Username hasn't changed
                self.username = orig.username
        if self.role == 'instructor':
            self.is_instructor = True
            self.is_student = False
        else:
            self.is_student = True
            self.is_instructor = False
        super().save(*args, **kwargs)

class Expertise(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Expertise"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField('users.CustomUser', on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # If there's an existing profile picture and we're updating with a new one
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.profile_picture and self.profile_picture and old_profile.profile_picture != self.profile_picture:
                    # Delete the old image file
                    if os.path.isfile(old_profile.profile_picture.path):
                        os.remove(old_profile.profile_picture.path)
            except Profile.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class InstructorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Instructor: {self.user.username}"

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student: {self.user.username}"