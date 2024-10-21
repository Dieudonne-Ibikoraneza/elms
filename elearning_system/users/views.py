from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm, InstructorProfileForm, StudentProfileForm
from django.contrib.auth import login
from courses.models import Enrollment
from django.contrib.auth import get_user_model
from .models import Profile
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from django.db.models import Count
from django.db import transaction
import logging
from .models import Skill
from .forms import SkillsUpdateForm
from django.urls import reverse
from courses.models import Course

User = get_user_model()

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    logger.info(f"User created successfully: {user.username}")
                    messages.success(request, 'Registration successful! You can now log in.')
                    return redirect('users:login')
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, f'Registration error: {str(e)}')
                return redirect('users:register')
        else:
            logger.error(f"Form validation errors: {form.errors}")
            messages.error(request, f'Form validation errors: {form.errors}')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(Profile, user=profile_user)
    
    context = {
        'profile': user_profile,
        'profile_user': profile_user,
        'is_owner': request.user == profile_user,
        'skills': user_profile.skills.all().select_related(),  # Optimize query
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
    profile_user = get_object_or_404(User, id=user_id)
    is_owner = request.user == profile_user
    is_instructor = profile_user.role == 'instructor'
    
    context = {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_instructor': is_instructor,
    }
    
    if is_owner:
        if is_instructor:
            context['expertise_form'] = InstructorProfileForm(instance=profile_user.profile)
        else:
            context['skills_form'] = StudentProfileForm(instance=profile_user.profile)
    
    return render(request, 'users/profile.html', context)

@login_required
def update_expertise(request):
    if request.method == 'POST' and request.user.is_instructor:
        form = InstructorProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expertise updated successfully!')
    return redirect('users:profile', user_id=request.user.id)

@login_required
def update_skills(request):
    if request.method == 'POST':
        form = SkillsUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            messages.success(request, 'Your skills have been updated successfully!')
            # Redirect to the profile view with the user's ID
            return redirect(reverse('users:profile', kwargs={'user_id': request.user.id}))
    else:
        form = SkillsUpdateForm(instance=request.user.profile)
    
    context = {
        'form': form,
        'all_skills': Skill.objects.all()
    }
    return render(request, 'users/update_skills.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile', user_id=request.user.id)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

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

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    viewer_is_instructor = hasattr(request.user, 'instructor_profile')
    is_own_profile = request.user == profile_user
    
    context = {
        'profile_user': profile_user,
        'viewer_is_instructor': viewer_is_instructor,
        'is_own_profile': is_own_profile,
    }

    # If viewing an instructor's profile
    if hasattr(profile_user, 'instructor_profile'):
        courses = Course.objects.filter(instructor=profile_user)
        public_courses = courses.filter(status='published')
        
        context.update({
            'is_instructor': True,
            'courses': public_courses,
            'courses_count': public_courses.count(),
        })
        
        # Only show student count to the profile owner
        if is_own_profile:
            context['students_count'] = Enrollment.objects.filter(
                course__instructor=profile_user
            ).count()
    
    # If viewing a student's profile
    elif hasattr(profile_user, 'student_profile'):
        enrolled_courses = Course.objects.filter(enrollments__student=profile_user)
        if is_own_profile or viewer_is_instructor:
            context['enrolled_courses'] = enrolled_courses
            context['courses_count'] = enrolled_courses.count()
        
        context['is_student'] = True

    return render(request, 'users/view_profile.html', context)