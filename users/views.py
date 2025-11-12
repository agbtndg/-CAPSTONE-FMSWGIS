from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .forms import CustomUserCreationForm, AdminRegistrationForm, ProfileEditForm
from .models import CustomUser, UserLog, LoginAttempt
from .validators import PasswordStrengthValidator
from monitoring.views import get_flood_risk_level, get_tide_risk_level, get_combined_risk_level

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_approved = False
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
@staff_member_required
def approve_users(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)
        
        if action == 'approve':
            if not user.is_superuser:  # Prevent modifying superuser status
                user.is_active = True
                user.is_approved = True
                user.save()
                UserLog.objects.create(
                    user=request.user,
                    action=f"Approved user {user.username}"
                )
                messages.success(request, f"User {user.username} has been approved.")
        
        elif action == 'delete':
            if user.is_superuser:
                messages.error(request, "Cannot delete superuser accounts.")
            else:
                username = user.username
                user.delete()
                UserLog.objects.create(
                    user=request.user,
                    action=f"Deleted user {username}"
                )
                messages.success(request, f"User {username} has been deleted.")
        
        return redirect('approve_users')
    
    # Get all users except superusers for the list
    users = CustomUser.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'users/approve_users.html', {'users': users})

def user_login(request):
    if request.user.is_authenticated:  # Check if already logged in—redirect to dashboard
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
        
        # Check for too many failed attempts
        failed_attempts = LoginAttempt.get_recent_failures(username, ip_address)
        if failed_attempts >= 5:  # Limit to 5 attempts per 30 minutes
            messages.error(request, "Too many failed login attempts. Please try again later.")
            return render(request, 'users/login.html', {'error': 'Too many failed attempts'})
        
        user = authenticate(request, username=username, password=password)
        login_successful = False
        
        if user is not None and user.is_active and user.is_approved:
            login(request, user)
            UserLog.objects.create(user=user, action="Logged in")
            login_successful = True
            messages.success(request, f"Welcome back, {user.username}!")
            
            # Clear failed attempts on successful login
            LoginAttempt.objects.filter(username=username, ip_address=ip_address).delete()
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials or account not approved.")
        
        # Log the attempt
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            success=login_successful
        )
        
        return render(request, 'users/login.html', {
            'error': 'Invalid login or user not approved',
            'admin_exists': CustomUser.objects.filter(is_superuser=True).exists()
        })
    return render(request, 'users/login.html', {
        'admin_exists': CustomUser.objects.filter(is_superuser=True).exists()
    })

def user_logout(request):
    if request.user.is_authenticated:
        UserLog.objects.create(user=request.user, action="Logged out")
    logout(request)
    return redirect('login')

def admin_register(request):
    if CustomUser.objects.filter(is_superuser=True).exists():
        messages.error(request, "Admin registration is disabled. An admin account already exists.")
        return redirect('login')
        
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserLog.objects.create(
                    user=user,
                    action="Created admin account"
                )
                messages.success(request, "Admin account created successfully. You can now log in.")
                return redirect('login')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'users/admin_register.html', {'form': form})
@login_required
def home(request):
    context = {
        'pending_approvals': CustomUser.objects.filter(is_active=False, is_approved=False).count(),
        'recent_logs': UserLog.objects.all().order_by('-timestamp')[:5],
        'total_users': CustomUser.objects.filter(is_active=True).count()
    }
    
    # Get latest monitoring data
    from monitoring.models import RainfallData, WeatherData, TideLevelData, FloodRecord
    
    
    rainfall_data = RainfallData.objects.last()
    weather_data = WeatherData.objects.last()
    tide_data = TideLevelData.objects.last()
    recent_floods = FloodRecord.objects.all().order_by('-date')[:3]
    
    if rainfall_data:
        rain_risk_level, rain_risk_color = get_flood_risk_level(rainfall_data.value_mm)
        context['rain_risk'] = {'level': rain_risk_level, 'color': rain_risk_color}
        
    if tide_data:
        tide_risk_level, tide_risk_color = get_tide_risk_level(tide_data.height_m)
        context['tide_risk'] = {'level': tide_risk_level, 'color': tide_risk_color}
        
    if rainfall_data and tide_data:
        combined_risk_level, combined_risk_color = get_combined_risk_level(rain_risk_level, tide_risk_level)
        context['combined_risk'] = {'level': combined_risk_level, 'color': combined_risk_color}
    
    context.update({
        'weather_data': weather_data,
        'recent_floods': recent_floods
    })
    
    return render(request, 'users/home.html', context)

@login_required
@staff_member_required
def user_logs(request):
    logs = UserLog.objects.all().order_by('-timestamp')[:10]  # Last 10 logs
    return render(request, 'users/user_logs.html', {'logs': logs})

@login_required
def view_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            UserLog.objects.create(user=user, action="Updated profile")
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
        else:
            # Errors will be available in form.errors for template display if needed
            messages.error(request, 'Error updating profile. Please check the form.')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})