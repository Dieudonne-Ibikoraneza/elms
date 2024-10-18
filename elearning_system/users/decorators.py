from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def instructor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'instructor':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('users:login')
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'admin':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('users:login')
    return _wrapped_view 