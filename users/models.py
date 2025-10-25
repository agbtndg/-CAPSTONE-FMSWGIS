from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    DEPARTMENT_CHOICES = [
        ('operations', 'Operations'),
        ('planning', 'Planning'),
        ('logistics', 'Logistics'),
        ('admin', 'Administration'),
        ('other', 'Other'),
    ]
    
    staff_id = models.CharField(max_length=10, unique=True, verbose_name="Staff ID")
    is_approved = models.BooleanField(default=False, verbose_name="Approved")
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='other', verbose_name="Department")
    position = models.CharField(max_length=100, blank=True, verbose_name="Position")
    contact_number = models.CharField(max_length=11, blank=True, verbose_name="Contact Number")
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name="Emergency Contact")
    emergency_number = models.CharField(max_length=11, blank=True, verbose_name="Emergency Contact Number")
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True, verbose_name="Profile Image")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

class UserLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="User")
    action = models.CharField(max_length=100, verbose_name="Action")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['username', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        
    @classmethod
    def get_recent_failures(cls, username, ip_address, minutes=30):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            username=username,
            ip_address=ip_address,
            timestamp__gte=cutoff,
            success=False
        ).count()