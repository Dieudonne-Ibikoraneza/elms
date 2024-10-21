from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Course, Category, Enrollment, CourseContent
from .forms import CourseForm, CourseContentForm

@login_required
def course_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category')
    
    courses = Course.objects.all()
    
    if search_query:
        courses = courses.filter(title__icontains=search_query)
    
    if category_id:
        courses = courses.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': None,
    }
    
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_course_instructor = course.instructor == request.user
    is_enrolled = False
    
    if not is_course_instructor:
        # Check if the student is enrolled
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).exists()
    
    context = {
        'course': course,
        'is_course_instructor': is_course_instructor,
        'is_enrolled': is_enrolled,
    }
    
    # Only fetch course content if user is instructor or enrolled student
    if is_course_instructor or is_enrolled:
        context['course_contents'] = course.contents.all().order_by('order')
    
    if is_course_instructor:
        enrolled_students = (Enrollment.objects
            .filter(course=course)
            .select_related('student')
            .order_by('enrolled_at'))
        context['enrolled_students'] = enrolled_students
        context['enrolled_count'] = enrolled_students.count()
    
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        
        # Check if user is not the instructor
        if course.instructor == request.user:
            messages.error(request, "You cannot enroll in your own course.")
            return redirect('courses:detail', course_id=course_id)
            
        # Check if already enrolled
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            Enrollment.objects.create(
                student=request.user,
                course=course
            )
            messages.success(request, f"You have successfully enrolled in {course.title}")
        else:
            messages.info(request, "You are already enrolled in this course")
            
    return redirect('courses:detail', course_id=course_id)

@login_required
def create_course(request):
    # Check if user is an instructor
    if request.user.role != 'instructor':
        messages.error(request, 'Only instructors can create courses.')
        return redirect('courses:list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:detail', course_id=course.id)
    else:
        form = CourseForm()
    
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Create Course'})

@login_required
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    courses = Course.objects.filter(category=category)
    
    context = {
        'category': category,
        'courses': courses,
        'categories': Category.objects.all(),
        'selected_category': category,
    }
    return render(request, 'courses/course_list.html', context)

@staff_member_required
def manage_enrollments(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        if enrollment_id:
            try:
                enrollment = Enrollment.objects.get(id=enrollment_id, course=course)
                student_name = enrollment.student.get_full_name() or enrollment.student.username
                enrollment.delete()
                messages.success(request, f'Successfully removed {student_name} from {course.title}')
            except Enrollment.DoesNotExist:
                messages.error(request, 'Enrollment not found.')
        
        return redirect('manage_enrollments', course_id=course.id)
    
    context = {
        'course': course,
        'enrollments': enrollments,
    }
    return render(request, 'courses/manage_enrollments.html', context)

@staff_member_required
def remove_enrollment(request, course_id, enrollment_id):
    if request.method == 'POST':
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, course_id=course_id)
        student_name = enrollment.student.get_full_name() or enrollment.student.username
        course_title = enrollment.course.title
        enrollment.delete()
        messages.success(request, f'Successfully removed {student_name} from {course_title}')
    
    return redirect('manage_enrollments', course_id=course_id)

@login_required
def manage_course_content(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is the course instructor
    if course.instructor != request.user and not request.user.is_staff:
        raise PermissionDenied
    
    contents = CourseContent.objects.filter(course=course).order_by('order')
    
    if request.method == 'POST':
        form = CourseContentForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            content = form.save(commit=False)
            content.course = course
            content.save()
            messages.success(request, 'Content added successfully!')
            return redirect('courses:manage_content', course_id=course.id)
    else:
        form = CourseContentForm(course=course)
    
    context = {
        'course': course,
        'contents': contents,
        'form': form,
    }
    return render(request, 'courses/manage_course_content.html', context)

@login_required
def delete_course_content(request, course_id, content_id):
    content = get_object_or_404(CourseContent, id=content_id, course_id=course_id)
    
    # Check if user is the course instructor
    if content.course.instructor != request.user and not request.user.is_staff:
        raise PermissionDenied
    
    if request.method == 'POST':
        content.delete()
        messages.success(request, 'Content deleted successfully!')
    
    return redirect('courses:manage_content', course_id=course_id)

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Check if the logged-in user is the course instructor
    if request.user != course.instructor:
        messages.error(request, "You don't have permission to delete this course.")
        return HttpResponseForbidden("You don't have permission to delete this course.")
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" has been deleted successfully.')
        return redirect('courses:list')
    
    return render(request, 'courses/delete_course.html', {
        'course': course
    })

@login_required
def unenroll_course(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        
        # Check if user is not the instructor
        if course.instructor == request.user:
            messages.error(request, "Instructors cannot unenroll from their own courses.")
            return redirect('courses:detail', course_id=course_id)
        
        # Try to find and delete the enrollment
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).first()
        
        if enrollment:
            enrollment.delete()
            messages.success(request, f"You have successfully unenrolled from {course.title}")
        else:
            messages.error(request, "You are not enrolled in this course")
            
    return redirect('courses:detail', course_id=course_id)

def is_staff(user):
    return user.is_authenticated and user.is_staff

def can_create_category(user):
    return user.is_authenticated and (user.is_staff or hasattr(user, 'instructor_profile'))

@login_required
@user_passes_test(can_create_category)
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('courses:list')
    else:
        form = CategoryForm()
    
    return render(request, 'courses/category_form.html', {
        'form': form,
        'title': 'Create Category'
    })

def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'courses/category_list.html', {
        'categories': categories
    })