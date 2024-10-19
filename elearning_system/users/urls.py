from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('update-expertise/', views.update_expertise, name='update_expertise'),
    path('update-skills/', views.update_skills, name='update_skills'),
    path('profile/', views.profile, name='profile'),
    path('skills/update/', views.update_skills, name='update_skills'),
]