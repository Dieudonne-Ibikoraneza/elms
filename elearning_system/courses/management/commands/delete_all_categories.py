from django.core.management.base import BaseCommand
from courses.models import Category

class Command(BaseCommand):
    help = 'Deletes all course categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete without confirmation',
        )

    def handle(self, *args, **kwargs):
        force = kwargs.get('force')
        category_count = Category.objects.count()

        if category_count == 0:
            self.stdout.write(
                self.style.WARNING('No categories found to delete.')
            )
            return

        if not force:
            confirm = input(f'\nYou are about to delete {category_count} categories. '
                          f'This will also affect related courses.\n'
                          f'Are you sure you want to continue? [y/N]: ')
            if confirm.lower() != 'y':
                self.stdout.write(
                    self.style.WARNING('Operation cancelled.')
                )
                return

        try:
            Category.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {category_count} categories.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting categories: {str(e)}')
            ) 