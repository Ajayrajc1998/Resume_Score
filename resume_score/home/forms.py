from django import forms
from .models import Resume

class SkillEditForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'skills']