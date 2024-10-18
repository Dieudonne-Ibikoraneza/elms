from django.contrib import admin
from .models import Course, CourseContent, Enrollment

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__username', 'course__title')

admin.site.register(Course)
admin.site.register(CourseContent)
admin.site.register(Enrollment, EnrollmentAdmin)
