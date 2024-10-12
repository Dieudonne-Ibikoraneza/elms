from django.contrib import admin
from .models import Course, Category, Enrollment, CourseContent

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'progress']
    list_filter = ['course', 'enrolled_at']
    search_fields = ['student__username', 'course__title']

admin.site.register(Course)
admin.site.register(CourseContent)
