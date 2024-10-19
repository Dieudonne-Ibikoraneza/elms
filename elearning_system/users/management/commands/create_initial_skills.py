from django.core.management.base import BaseCommand
from users.models import Skill

class Command(BaseCommand):
    help = 'Creates initial skills data'

    def handle(self, *args, **kwargs):
        skills = [
            'Python Programming',
            'JavaScript',
            'HTML/CSS',
            'React',
            'Django',
            'Database Management',
            'Git Version Control',
            'Web Development',
            'Data Analysis',
            'Problem Solving',
            'Agile Methodologies',
            'API Development',
            'Software Testing',
            'UI/UX Design',
            'Mobile Development'
        ]
        
        for skill_name in skills:
            Skill.objects.get_or_create(name=skill_name)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(skills)} skills')) 