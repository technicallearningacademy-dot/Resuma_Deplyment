"""
Forms for user registration and profile completion.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, Education, Experience, Skill, Certification, Project


class CustomUserCreationForm(UserCreationForm):
    """Registration form with email."""
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-input', 'placeholder': 'Last Name'}))

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email Address'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})


class UserProfileForm(forms.ModelForm):
    """Profile completion form."""
    class Meta:
        model = UserProfile
        fields = ['phone', 'city', 'country', 'linkedin', 'github', 'portfolio', 'summary', 'job_title']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 234 567 8900'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Country'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/in/...'}),
            'github': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/...'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://your-site.com'}),
            'summary': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Brief professional summary...'}),
            'job_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Software Engineer'}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'gpa', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'University / School'}),
            'degree': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Bachelor of Science'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Computer Science'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gpa': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '3.8/4.0'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Key coursework, honors...'}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'title', 'start_date', 'end_date', 'is_current', 'location', 'description', 'achievements']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company Name'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Job Title'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City, Country'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Role description...'}),
            'achievements': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'One achievement per line'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Skill name'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'proficiency': forms.Select(attrs={'class': 'form-input'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuer', 'date_obtained', 'credential_url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Certification Name'}),
            'issuer': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Issuing Organization'}),
            'date_obtained': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'technologies', 'url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Project Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'What did you build?'}),
            'technologies': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Python, Django, React...'}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/...'}),
        }


# Inline Formsets
EducationFormSet = forms.inlineformset_factory(
    UserProfile, Education, form=EducationForm, extra=1, can_delete=True
)
ExperienceFormSet = forms.inlineformset_factory(
    UserProfile, Experience, form=ExperienceForm, extra=1, can_delete=True
)
SkillFormSet = forms.inlineformset_factory(
    UserProfile, Skill, form=SkillForm, extra=3, can_delete=True
)
CertificationFormSet = forms.inlineformset_factory(
    UserProfile, Certification, form=CertificationForm, extra=1, can_delete=True
)
ProjectFormSet = forms.inlineformset_factory(
    UserProfile, Project, form=ProjectForm, extra=1, can_delete=True
)


class ProfileImageForm(forms.ModelForm):
    """Form for uploading profile image."""
    class Meta:
        model = CustomUser
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }


class CVUploadForm(forms.Form):
    """Form for uploading existing CV for AI extraction."""
    cv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.pdf,.docx,.doc'}),
        help_text='Upload your existing CV (PDF or DOCX) for AI data extraction'
    )
