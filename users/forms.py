from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'staff_id', 'department', 'position',
            'contact_number', 'password1', 'password2'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class AdminRegistrationForm(UserCreationForm):
    registration_key = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the secure registration key provided by the system administrator."
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'staff_id', 'department', 'position',
            'contact_number', 'password1', 'password2'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_registration_key(self):
        key = self.cleaned_data.get('registration_key')
        if key != getattr(settings, 'ADMIN_REGISTRATION_KEY', None):
            raise forms.ValidationError("Invalid registration key. Please contact the system administrator.")
        return key

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.is_approved = True
        if commit:
            user.save()
        return user

class ProfileEditForm(UserChangeForm):
    password = None  # Remove password field from form
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email',
            'department', 'position', 'contact_number',
            'emergency_contact', 'emergency_number',
            'bio', 'date_of_birth', 'profile_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs['class'] = 'form-control'

    def clean_contact_number(self):
        num = self.cleaned_data.get('contact_number')
        if num and len(num) != 11:
            raise forms.ValidationError("Contact number must be exactly 11 characters.")
        return num

    def clean_emergency_number(self):
        num = self.cleaned_data.get('emergency_number')
        if num and len(num) != 11:
            raise forms.ValidationError("Emergency contact number must be exactly 11 characters.")
        return num