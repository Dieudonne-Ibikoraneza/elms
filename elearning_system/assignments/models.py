from django.db import models
from courses.models import Course
from users.models import CustomUser

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_points = models.IntegerField()

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    submitted_file = models.FileField(upload_to='submissions/')
    submission_date = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)