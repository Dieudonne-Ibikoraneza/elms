from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm
from courses.models import Course

@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)
    return render(request, 'assignments/assignment_list.html', {
        'course': course,
        'assignments': assignments
    })

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user.is_student():
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()
        if request.method == 'POST':
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.student = request.user
                submission.assignment = assignment
                submission.save()
                messages.success(request, 'Your submission has been received.')
                return redirect('assignment_detail', assignment_id=assignment.id)
        else:
            form = SubmissionForm()
        return render(request, 'assignments/assignment_detail.html', {
            'assignment': assignment,
            'submission': submission,
            'form': form
        })
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment
    })

@login_required
def create_assignment(request, course_id):
    if not request.user.is_instructor():
        messages.error(request, 'You do not have permission to create assignments.')
        return redirect('course_detail', pk=course_id)
    
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('assignment_list', course_id=course.id)
    else:
        form = AssignmentForm()
    
    return render(request, 'assignments/create_assignment.html', {
        'form': form,
        'course': course
    })
