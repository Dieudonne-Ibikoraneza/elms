from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # Student URLs
    path('course/<int:course_id>/assignments/', views.assignment_list, name='assignment_list'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
    
    # Instructor URLs
    path('instructor/assignments/', views.instructor_assignments, name='instructor_assignments'),
    path('instructor/assignment/create/', views.create_assignment, name='create_assignment'),
    path('instructor/assignment/<int:assignment_id>/edit/', views.edit_assignment, name='edit_assignment'),
    path('instructor/assignment/<int:assignment_id>/delete/', views.delete_assignment, name='delete_assignment'),
    path('instructor/assignment/<int:assignment_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('instructor/submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]