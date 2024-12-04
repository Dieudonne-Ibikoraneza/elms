from .models import Notification

def create_notification(user, notification_type, title, message):
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message
    )

def notify_assignment_created(assignment):
    for student in assignment.course.students.all():
        create_notification(
            user=student,
            notification_type=Notification.NEW_ASSIGNMENT,
            title=f'New Assignment: {assignment.title}',
            message=f'A new assignment has been posted in {assignment.course.title}'
        )

def notify_grade_posted(submission):
    create_notification(
        user=submission.student,
        notification_type=Notification.GRADE_POSTED,
        title=f'Grade Posted: {submission.assignment.title}',
        message=f'Your grade for {submission.assignment.title} has been posted'
    ) 