from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Enter course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'rows': 4,
                'placeholder': 'Enter course description'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'mt-1 block w-full'
            })
        }

class EnrollmentForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.HiddenInput()
    ) 