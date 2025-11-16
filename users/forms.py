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
        placeholders = {
            'first_name': 'Enter your first name',
            'last_name': 'Enter your last name',
            'username': 'Choose a username',
            'email': 'Enter your email address',
            'position': 'Select your position',
            'contact_number': '11-digit mobile number',
            'date_of_birth': 'YYYY-MM-DD',
            'password1': 'Create a password',
            'password2': 'Confirm your password',
        }
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if name in placeholders:
                # Remove leading/trailing spaces just in case
                field.widget.attrs['placeholder'] = placeholders[name].strip()
        
        # Make email required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['contact_number'].required = True
        self.fields['date_of_birth'].required = True
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("This email address is already registered. Please use a different email.")
        return email.lower() if email else email
    
    def clean_username(self):
        """Validate username uniqueness and format."""
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists (case-insensitive)
            if CustomUser.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError("This username is already taken. Please choose a different username.")
            # Validate username format (alphanumeric and underscores only)
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username
    
    def clean_contact_number(self):
        """Validate contact number is exactly 11 digits."""
        num = self.cleaned_data.get('contact_number')
        if num:
            # Remove any whitespace
            num = num.strip()
            # Check if it's exactly 11 digits
            if not num.isdigit() or len(num) != 11:
                raise forms.ValidationError("Contact number must be exactly 11 digits.")
            # Check if it starts with 09 (Philippine mobile format)
            if not num.startswith('09'):
                raise forms.ValidationError("Contact number must start with '09'.")
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
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter registration key'
        }),
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
        
        placeholders = {
            'first_name': 'Enter your first name',
            'last_name': 'Enter your last name',
            'username': 'Choose a username',
            'email': 'Enter your email address',
            'position': 'Select your position',
            'contact_number': '09xxxxxxxxx',
            'date_of_birth': 'YYYY-MM-DD',
            'registration_key': 'Enter registration key',
            'password1': 'Create a password',
            'password2': 'Confirm your password',
        }
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]
        
        # Make email and other fields required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['contact_number'].required = True
        self.fields['date_of_birth'].required = True
    
    def clean_registration_key(self):
        key = self.cleaned_data.get('registration_key')
        if key != getattr(settings, 'ADMIN_REGISTRATION_KEY', None):
            raise forms.ValidationError("Invalid registration key. Please contact the system administrator.")
        return key
    
    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("This email address is already registered. Please use a different email.")
        return email.lower() if email else email
    
    def clean_username(self):
        """Validate username uniqueness and format."""
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists (case-insensitive)
            if CustomUser.objects.filter(username__iexact=username).exists():
                raise forms.ValidationError("This username is already taken. Please choose a different username.")
            # Validate username format (alphanumeric and underscores only)
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        return username
    
    def clean_contact_number(self):
        """Validate contact number is exactly 11 digits."""
        num = self.cleaned_data.get('contact_number')
        if num:
            # Remove any whitespace
            num = num.strip()
            # Check if it's exactly 11 digits
            if not num.isdigit() or len(num) != 11:
                raise forms.ValidationError("Contact number must be exactly 11 digits.")
            # Check if it starts with 09 (Philippine mobile format)
            if not num.startswith('09'):
                raise forms.ValidationError("Contact number must start with '09'.")
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