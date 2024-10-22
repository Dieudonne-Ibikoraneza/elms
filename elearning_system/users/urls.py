from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Profile views - order matters!
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/me/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    
    # Skills and expertise
    path('skills/update/', views.update_skills, name='update_skills'),
    path('expertise/update/', views.update_expertise, name='update_expertise'),
]