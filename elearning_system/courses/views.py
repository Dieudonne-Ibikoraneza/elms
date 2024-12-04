from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
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
    if not request.user.is_instructor():
        raise PermissionDenied
    
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_dashboard.html', {
        'courses': courses
    })

@login_required
def create_course(request):
    if not request.user.is_instructor():
        raise PermissionDenied
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Create Course'
    })

@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.user != course.instructor:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', pk=course.pk)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/course_form.html', {
        'form': form,
        'title': 'Edit Course',
        'course': course
    })

@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.user != course.instructor:
        raise PermissionDenied
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('instructor_dashboard')
    
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def manage_students(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.user != course.instructor:
        raise PermissionDenied
    
    enrollments = course.enrollment_set.all()
    return render(request, 'courses/manage_students.html', {
        'course': course,
        'enrollments': enrollments
    })
