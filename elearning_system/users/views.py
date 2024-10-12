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
from django.db.models import Count

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

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
    profile_user = get_object_or_404(User, id=user_id)
    profile = getattr(profile_user, 'profile', None)  # Get profile if it exists
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_owner': request.user == profile_user,
        'is_instructor': profile_user.role == 'instructor' or profile_user.is_instructor,
    }
    
    if context['is_instructor']:
        instructor_courses = profile_user.courses.all()
        total_students = sum(course.enrolled_students.count() for course in instructor_courses)
        
        # Calculate average rating (if you have a rating system)
        total_ratings = 0
        rated_courses = 0
        for course in instructor_courses:
            if hasattr(course, 'average_rating') and course.average_rating:
                total_ratings += course.average_rating
                rated_courses += 1
        
        avg_rating = round(total_ratings / rated_courses, 1) if rated_courses > 0 else 0
        
        context.update({
            'total_courses': instructor_courses.count(),
            'total_students': total_students,
            'average_rating': avg_rating,
            'instructor_courses': instructor_courses,
        })
    else:
        # Student specific stats
        enrollments = Enrollment.objects.filter(student=profile_user)
        completed_courses = enrollments.filter(progress=100).count()
        total_enrolled = enrollments.count()
        
        # Calculate completion rate
        completion_rate = (completed_courses / total_enrolled * 100) if total_enrolled > 0 else 0
        
        context.update({
            'enrolled_courses': enrollments,
            'completed_courses_count': completed_courses,
            'completion_rate': round(completion_rate, 1),
            'total_courses': total_enrolled
        })
    
    return render(request, 'users/profile.html', context)

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