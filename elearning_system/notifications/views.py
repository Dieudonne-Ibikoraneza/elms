from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    return render(request, 'notifications/notification_list.html', 
                 {'notifications': notifications})

@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    notification.read = True
    notification.save()
    
    return render(request, 'notifications/notification_detail.html', 
                 {'notification': notification})

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    notification.read = True
    notification.save()
    
    return redirect('notifications:notification_list')

@login_required
def mark_all_read(request):
    Notification.objects.filter(
        recipient=request.user, 
        read=False
    ).update(read=True)
    
    messages.success(request, 'All notifications marked as read.')
    return redirect('notifications:notification_list')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('notifications:notification_list')

@login_required
def delete_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications deleted.')
    return redirect('notifications:notification_list')