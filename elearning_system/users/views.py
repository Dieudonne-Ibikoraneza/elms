from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import login
from courses.models import Enrollment
from django.contrib.auth import get_user_model
from .models import Profile
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.conf import settings
import os

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'users/profile.html', context)

@login_required
def student_dashboard(request):
    if request.user.role == 'instructor':
        return redirect('users:instructor_dashboard')
    
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course', 'course__instructor').order_by('-enrolled_at')
    
    context = {
        'enrollments': enrollments,
        'recent_activities': [],  # You can implement activity tracking later
    }
    return render(request, 'users/student_dashboard.html', context)

@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return redirect('users:student_dashboard')
    
    courses = request.user.courses_taught.all()
    
    context = {
        'courses': courses,
    }
    return render(request, 'users/instructor_dashboard.html', context)

@login_required
def profile_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {
        'profile_user': user,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    # Ensure profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, 
                                       request.FILES, 
                                       instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile', user_id=request.user.id)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            profile = request.user.profile
            avatar = request.FILES['avatar']
            
            # Validate file size (e.g., max 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('File size too large. Max size is 5MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError('Unsupported file type.')
            
            # Delete old avatar if it exists
            if profile.avatar:
                profile.avatar.delete(save=False)
            
            profile.avatar = avatar
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile picture updated successfully!'
            })
            
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while updating the profile picture.'
            }, status=500)
            
    return JsonResponse({
        'success': False,
        'message': 'Invalid request'
    }, status=400)