from django.db import models
from users.models import User

class Notification(models.Model):
    PROGRESS_UPDATE = 'progress_update'
    NEW_ASSIGNMENT = 'new_assignment'
    GRADE_POSTED = 'grade_posted'
    
    NOTIFICATION_TYPES = [
        (PROGRESS_UPDATE, 'Progress Update'),
        (NEW_ASSIGNMENT, 'New Assignment'),
        (GRADE_POSTED, 'Grade Posted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
