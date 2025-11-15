from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Form for regular user registration.
    Staff ID is automatically generated upon user creation.
    Includes date of birth validation (18-80 years old).
    """
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'position', 'contact_number', 'date_of_birth',
            'password1', 'password2'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_date_of_birth(self):
        """Validate date of birth: must be 18-80 years old, no future dates."""
        from datetime import date
        
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            
            # Check if date is in the future
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")
            
            # Calculate age (accurate method considering leap years)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check minimum age (18)
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
            
            # Check maximum age (80)
            if age > 80:
                raise forms.ValidationError("Age must not exceed 80 years.")
        
        return dob

class AdminRegistrationForm(UserCreationForm):
    """
    Form for admin registration with secure registration key.
    Staff ID is automatically generated upon user creation.
    Includes date of birth validation (18-80 years old).
    """
    registration_key = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the secure registration key provided by the system administrator."
    )
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'position', 'contact_number', 'date_of_birth',
            'password1', 'password2'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_registration_key(self):
        key = self.cleaned_data.get('registration_key')
        if key != getattr(settings, 'ADMIN_REGISTRATION_KEY', None):
            raise forms.ValidationError("Invalid registration key. Please contact the system administrator.")
        return key
    
    def clean_date_of_birth(self):
        """Validate date of birth: must be 18-80 years old, no future dates."""
        from datetime import date
        
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            
            # Check if date is in the future
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")
            
            # Calculate age (accurate method considering leap years)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check minimum age (18)
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
            
            # Check maximum age (80)
            if age > 80:
                raise forms.ValidationError("Age must not exceed 80 years.")
        
        return dob

class ProfileEditForm(UserChangeForm):
    """
    Form for editing user profile information.
    Excludes password field and provides validation for contact numbers and profile image.
    """
    password = None  # Remove password field from form
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email',
            'position', 'contact_number',
            'emergency_contact', 'emergency_number',
            'bio', 'date_of_birth', 'profile_image'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
    
    def clean_contact_number(self):
        """Validate contact number is exactly 11 digits."""
        num = self.cleaned_data.get('contact_number')
        if num and len(num) != 11:
            raise forms.ValidationError("Contact number must be exactly 11 digits.")
        return num
    
    def clean_emergency_number(self):
        """Validate emergency contact number is exactly 11 digits."""
        num = self.cleaned_data.get('emergency_number')
        if num and len(num) != 11:
            raise forms.ValidationError("Emergency contact number must be exactly 11 digits.")
        return num
    
    def clean_date_of_birth(self):
        """Validate date of birth: must be 18-80 years old, no future dates."""
        from datetime import date
        
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            
            # Check if date is in the future
            if dob > today:
                raise forms.ValidationError("Date of birth cannot be in the future.")
            
            # Calculate age (accurate method considering leap years)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Check minimum age (18)
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old.")
            
            # Check maximum age (80)
            if age > 80:
                raise forms.ValidationError("Age must not exceed 80 years.")
        
        return dob
    
    def clean_profile_image(self):
        """Validate profile image file type and size."""
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size must be less than 5MB.")
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            import os
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(f"Invalid file type. Allowed types: {', '.join(valid_extensions)}")
        
        return image