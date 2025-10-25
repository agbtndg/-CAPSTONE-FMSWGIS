from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
import re

class PasswordStrengthValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one number.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            raise ValueError("Password must contain at least one special character.")
        
    def get_help_text(self):
        return "Your password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."

class StaffIDValidator:
    def __call__(self, value):
        if not re.match(r'^[A-Z]{2}\d{4}$', value):
            raise ValueError("Staff ID must be in format: 2 uppercase letters followed by 4 digits (e.g., AB1234)")
        return value