from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assignment, Submission
from courses.models import Course
from .forms import AssignmentForm, SubmissionForm
from users.decorators import instructor_required
from notifications.models import Notification

@login_required
def assignment_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    assignments = Assignment.objects.filter(course=course)
    
    # Get submission status for each assignment
    assignment_status = {}
    for assignment in assignments:
        submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()
        assignment_status[assignment.id] = submission
    
    context = {
        'course': course,
        'assignments': assignments,
        'assignment_status': assignment_status,
    }
    return render(request, 'assignments/assignment_list.html', context)

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()
    
    context = {
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'assignments/assignment_detail.html', context)

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if already submitted
    submission = Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            new_submission = form.save(commit=False)
            new_submission.assignment = assignment
            new_submission.student = request.user
            new_submission.save()
            
            messages.success(request, 'Assignment submitted successfully.')
            return redirect('assignments:assignment_detail', assignment_id=assignment.id)
    else:
        form = SubmissionForm(instance=submission)
    
    context = {
        'assignment': assignment,
        'form': form,
        'submission': submission,
    }
    return render(request, 'assignments/submit_assignment.html', context)

@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(student=request.user).order_by('-submission_date')
    return render(request, 'assignments/my_submissions.html', {'submissions': submissions})

@login_required
@instructor_required
def instructor_assignments(request):
    courses = Course.objects.filter(instructor=request.user)
    assignments = Assignment.objects.filter(course__in=courses)
    return render(request, 'assignments/instructor_assignments.html', {'assignments': assignments})

@login_required
@instructor_required
def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save()
            messages.success(request, 'Assignment created successfully.')
            return redirect('assignments:assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm()
        # Only show courses where the user is an instructor
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)
    
    return render(request, 'assignments/assignment_form.html', {'form': form, 'action': 'Create'})

@login_required
@instructor_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect('assignments:assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)
        form.fields['course'].queryset = Course.objects.filter(instructor=request.user)
    
    return render(request, 'assignments/assignment_form.html', {'form': form, 'action': 'Edit'})

@login_required
@instructor_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=request.user)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully.')
        return redirect('assignments:instructor_assignments')
    
    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment})

@login_required
@instructor_required
def view_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__instructor=request.user)
    submissions = Submission.objects.filter(assignment=assignment)
    return render(request, 'assignments/view_submissions.html', {
        'assignment': assignment,
        'submissions': submissions
    })

@login_required
@instructor_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(
        Submission, 
        id=submission_id, 
        assignment__course__instructor=request.user
    )
    
    if request.method == 'POST':
        grade = request.POST.get('grade')
        feedback = request.POST.get('feedback')
        
        if grade and grade.isdigit():
            submission.grade = int(grade)
            submission.feedback = feedback
            submission.save()
            
            # Create notification for student
            Notification.objects.create(
                recipient=submission.student,
                title=f'Assignment Graded: {submission.assignment.title}',
                message=f'Your submission has been graded. Grade: {grade}%'
            )
            
            messages.success(request, 'Submission graded successfully.')
            return redirect('assignments:view_submissions', assignment_id=submission.assignment.id)
    
    return render(request, 'assignments/grade_submission.html', {'submission': submission})