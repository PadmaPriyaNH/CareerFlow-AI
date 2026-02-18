from django import forms
from .models import InterviewSession

class InterviewSetupForm(forms.ModelForm):
    class Meta:
        model = InterviewSession
        fields = ['job_description', 'role_title', 'resume']
        widgets = {
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Paste the job description here...'
            }),
            'role_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python Developer, Data Scientist'
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx'
            })
        }