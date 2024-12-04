from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment
from .forms import CourseForm

@login_required
def course_list(request):
    if request.user.is_student():
        courses = Course.objects.filter(students=request.user)
    else:
        courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.user.is_student():
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        return render(request, 'courses/course_detail.html', {
            'course': course,
            'enrollment': enrollment
        })
    return render(request, 'courses/course_detail.html', {'course': course})

@login_required
def student_dashboard(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'courses/student_dashboard.html', {'enrollments': enrollments})

@login_required
def instructor_dashboard(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_dashboard.html', {'courses': courses})
