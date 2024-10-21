from django.core.management import call_command
from django.apps import apps

def reset_migrations():
    # Order matters - reset dependent apps first
    apps_to_reset = [
        'notifications',
        'assignments',
        'courses'
    ]
    
    for app_name in apps_to_reset:
        print(f"Resetting migrations for {app_name}...")
        call_command('migrate', app_name, 'zero', verbosity=1, interactive=False)

if __name__ == '__main__':
    reset_migrations() 