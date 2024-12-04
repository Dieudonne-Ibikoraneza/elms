from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/instructor/', views.instructor_dashboard, name='instructor_dashboard'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:pk>/manage-students/', views.manage_students, name='manage_students'),
] 