from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.assignment_list, name='assignment_list'),
    path('<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('create/<int:course_id>/', views.create_assignment, name='create_assignment'),
] 