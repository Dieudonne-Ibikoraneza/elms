from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('create/', views.create_course, name='create'),
    path('<int:course_id>/', views.course_detail, name='detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll'),
    path('<int:course_id>/content/', views.manage_course_content, name='manage_content'),
    path('<int:course_id>/content/<int:content_id>/delete/', views.delete_course_content, name='delete_content'),
    path('category/<int:category_id>/', views.category_detail, name='category'),
    path('<int:course_id>/delete/', views.delete_course, name='delete'),
    path('<int:course_id>/unenroll/', views.unenroll_course, name='unenroll'),
]