from django import forms
from django.core.exceptions import ValidationError
from .models import Course, CourseContent

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CourseContentForm(forms.ModelForm):
    class Meta:
        model = CourseContent
        fields = ['title', 'content_type', 'file', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter content title'
            }),
            'content_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter content description'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Enter display order (must be unique)'
            })
        }
    
    def __init__(self, *args, course=None, **kwargs):
        self.course = course
        super().__init__(*args, **kwargs)
        
        if self.course:
            # Get existing orders in this course
            existing_orders = CourseContent.objects.filter(
                course=self.course
            ).values_list('order', flat=True)
            
            # Add help text showing available orders
            if existing_orders:
                next_available = max(existing_orders) + 1
                self.fields['order'].help_text = f'Next available order number: {next_available}'
            else:
                self.fields['order'].help_text = 'Start with 0 for the first content'

    def clean_order(self):
        order = self.cleaned_data.get('order')
        
        if self.course:
            # Check if this order already exists in this course
            exists = CourseContent.objects.filter(
                course=self.course,
                order=order
            ).exists()
            
            if exists:
                raise ValidationError(
                    f'Content with order {order} already exists. Please choose a different order number.'
                )
        
        return order

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        file = cleaned_data.get('file')
        
        if file:
            extension = file.name.split('.')[-1].lower()
            allowed_extensions = {
                'document': ['pdf', 'doc', 'docx', 'ppt', 'pptx'],
                'video': ['mp4', 'webm'],
                'assignment': ['pdf', 'doc', 'docx', 'zip']
            }
            
            if content_type in allowed_extensions:
                if extension not in allowed_extensions[content_type]:
                    raise forms.ValidationError(
                        f'Invalid file type for {content_type}. Allowed types: '
                        f'{", ".join(allowed_extensions[content_type])}'
                    )
        
        return cleaned_data 