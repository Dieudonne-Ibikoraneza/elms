from django.core.management.base import BaseCommand
from courses.models import Category

class Command(BaseCommand):
    help = 'Creates initial course categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Programming',
                'description': 'Courses related to computer programming and software development'
            },
            {
                'name': 'Data Science',
                'description': 'Courses covering data analysis, machine learning, and statistics'
            },
            {
                'name': 'Business',
                'description': 'Courses in business management, entrepreneurship, and marketing'
            },
            {
                'name': 'Design',
                'description': 'Courses in graphic design, UI/UX, and digital art'
            },
            {
                'name': 'Languages',
                'description': 'Language learning courses for various international languages'
            },
            {
                'name': 'Mathematics',
                'description': 'Courses covering various mathematics topics'
            }
        ]

        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category "{category.name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category "{category.name}" already exists')
                ) 