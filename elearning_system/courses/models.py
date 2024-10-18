from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    enrolled_students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_courses', blank=True)
    
    def __str__(self):
        return self.title

    def get_enrolled_students_count(self):
        return self.enrollments.count()

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.mp4', '.webm', '.zip']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

class CourseContent(models.Model):
    CONTENT_TYPES = (
        ('document', 'Document'),
        ('video', 'Video'),
        ('assignment', 'Assignment'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='contents')
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    file = models.FileField(
        upload_to='course_contents/',
        validators=[validate_file_extension]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="The order in which this content appears in the course"
    )

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def filename(self):
        return os.path.basename(self.file.name)

    def get_file_type(self):
        """Return the file extension"""
        name = self.file.name.lower()
        if name.endswith('.pdf'):
            return 'pdf'
        elif name.endswith(('.mp4', '.webm')):
            return 'video'
        return 'other'

    def can_preview(self):
        """Check if the file can be previewed in browser"""
        return self.get_file_type() in ['pdf', 'video']