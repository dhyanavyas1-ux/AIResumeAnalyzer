from django import forms
from django.core.validators import FileExtensionValidator
from .models import Resume

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

class ResumeForm(forms.ModelForm):
    file = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'docx']),
        ],
        help_text='Allowed formats: PDF, DOCX (max 5MB).'
    )

    class Meta:
        model = Resume
        fields = ['file', 'job_description']

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file and uploaded_file.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('The file is too large. Maximum upload size is 5MB.')
        return uploaded_file