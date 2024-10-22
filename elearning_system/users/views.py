from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course
from .forms import UserRegistrationForm  # You'll need to create this

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    """View for user's own profile"""
    return view_profile(request, request.user.id)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Handle profile editing
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    return render(request, 'users/edit_profile.html')

@login_required
def update_expertise(request):
    if request.method == 'POST':
        # Handle expertise update
        messages.success(request, 'Expertise updated successfully!')
    return redirect('users:profile')

@login_required
def update_skills(request):
    if request.method == 'POST':
        # Handle skills update
        messages.success(request, 'Skills updated successfully!')
    return redirect('users:profile')

@login_required
def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    courses = Course.objects.filter(instructor=profile_user)
    
    # Calculate total students
    total_students = 0
    for course in courses:
        if hasattr(course, 'enrolled_students'):
            total_students += course.enrolled_students.count()
    
    context = {
        'profile_user': profile_user,
        'is_owner': request.user == profile_user,
        'is_instructor': courses.exists(),
        'courses': courses,
        'total_courses': courses.count(),
        'total_students': total_students,
        'average_rating': 0.0,  # Default value
        'enrolled_courses': Course.objects.filter(enrolled_students=profile_user),
        'completion_rate': '0%',  # Default value
    }
    
    # Add profile-related context if profile exists
    if hasattr(profile_user, 'profile'):
        context.update({
            'bio': profile_user.profile.bio if hasattr(profile_user.profile, 'bio') else '',
            'expertise': profile_user.profile.expertise.all() if hasattr(profile_user.profile, 'expertise') else [],
            'skills': profile_user.profile.skills.all() if hasattr(profile_user.profile, 'skills') else [],
        })
    
    return render(request, 'users/profile.html', context)