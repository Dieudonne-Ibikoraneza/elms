from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from courses.models import Course
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm  # You'll need to create this
from django.http import JsonResponse

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
def view_profile(request, user_id=None):
    if user_id is None:
        # Viewing own profile
        profile_user = request.user
    else:
        # Viewing someone else's profile
        profile_user = get_object_or_404(get_user_model(), id=user_id)
    
    is_owner = profile_user == request.user
    is_instructor = profile_user.is_instructor

    # Get courses if user is instructor
    if is_instructor:
        instructor_courses = Course.objects.filter(instructor=profile_user)
    else:
        instructor_courses = None

    context = {
        'profile_user': profile_user,
        'is_owner': is_owner,
        'is_instructor': is_instructor,
        'instructor_courses': instructor_courses,
    }
    
    return render(request, 'users/view_profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Handle AJAX profile picture update
            if 'profile_picture' in request.FILES:
                profile = request.user.profile
                if profile.profile_picture:
                    profile.profile_picture.delete()
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Profile picture updated successfully',
                    'image_url': profile.profile_picture.url
                })
            return JsonResponse({
                'success': False,
                'message': 'No image file received'
            })

        # Handle regular form submission
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'users/edit_profile.html', context)

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