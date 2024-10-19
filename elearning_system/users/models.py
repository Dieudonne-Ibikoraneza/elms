from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
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
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    expertise = models.ManyToManyField(Expertise, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"