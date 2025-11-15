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
    """
    Handle user registration with auto-generated staff ID.
    
    Staff ID Format: YEAR + sequential 4-digit number (e.g., 20250001)
    The user account is created as inactive pending admin approval.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered registration form or redirect to login
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.is_approved = False
            
            # Auto-generate staff ID
            from datetime import datetime
            current_year = datetime.now().year
            
            # Get the last staff ID for this year
            last_user = CustomUser.objects.filter(
                staff_id__startswith=str(current_year)
            ).order_by('-staff_id').first()
            
            if last_user and last_user.staff_id:
                # Extract the sequential number and increment
                try:
                    last_number = int(last_user.staff_id[-4:])
                    new_number = last_number + 1
                except (ValueError, TypeError):
                    new_number = 1
            else:
                new_number = 1
            
            # Format: YEAR + 4-digit number (e.g., 20250001)
            user.staff_id = f"{current_year}{new_number:04d}"
            
            user.save()
            messages.success(request, f'Account created successfully! Your Staff ID is {user.staff_id}. Please wait for admin approval.')
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
    """
    Handle admin registration with auto-generated staff ID.
    
    Only allows registration if no admin exists yet.
    Admin accounts are automatically approved and activated.
    
    Args:
        request: HttpRequest object
        
    Returns:
        HttpResponse: Rendered registration form or redirect
    """
    if CustomUser.objects.filter(is_superuser=True).exists():
        messages.error(request, "Admin registration is disabled. An admin account already exists.")
        return redirect('login')
        
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                
                # Auto-generate staff ID for admin
                from datetime import datetime
                current_year = datetime.now().year
                
                # Get the last staff ID for this year
                last_user = CustomUser.objects.filter(
                    staff_id__startswith=str(current_year)
                ).order_by('-staff_id').first()
                
                if last_user and last_user.staff_id:
                    try:
                        last_number = int(last_user.staff_id[-4:])
                        new_number = last_number + 1
                    except (ValueError, TypeError):
                        new_number = 1
                else:
                    new_number = 1
                
                # Format: YEAR + 4-digit number (e.g., 20250001)
                user.staff_id = f"{current_year}{new_number:04d}"
                
                # Set admin privileges
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.is_approved = True
                
                user.save()
                
                UserLog.objects.create(
                    user=user,
                    action=f"Created admin account with Staff ID: {user.staff_id}"
                )
                messages.success(request, f"Admin account created successfully! Your Staff ID is {user.staff_id}. You can now log in.")
                return redirect('login')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'users/admin_register.html', {'form': form})
@login_required
def home(request):
    context = {
        'pending_approvals': CustomUser.objects.filter(is_active=False, is_approved=False).count(),
        'recent_logs': UserLog.objects.all().order_by('-timestamp')[:5],
        'total_users': CustomUser.objects.filter(is_active=True).count(),
        'user_logs': UserLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
    }

    # Admin summary cards context
    if request.user.is_staff:
        # Total activities: count of all UserLog, FloodRecordActivity, AssessmentRecord, ReportRecord, CertificateRecord
        from maps.models import FloodRecordActivity, AssessmentRecord, ReportRecord, CertificateRecord
        total_activities = (
            UserLog.objects.count() +
            FloodRecordActivity.objects.count() +
            AssessmentRecord.objects.count() +
            ReportRecord.objects.count() +
            CertificateRecord.objects.count()
        )
        # Most active user: user with most UserLog entries
        from django.db.models import Count
        most_active = UserLog.objects.values('user__username').annotate(activity_count=Count('id')).order_by('-activity_count').first()
        most_active_user = None
        if most_active:
            most_active_user = type('MostActiveUser', (), {})()
            most_active_user.username = most_active['user__username']
            most_active_user.activity_count = most_active['activity_count']

        # Recent activity highlights: last 5 from all activity models, sorted by timestamp/date
        recent_activity_highlights = []
        # UserLog
        for log in UserLog.objects.all().order_by('-timestamp')[:5]:
            log.type = 'UserLog'
            recent_activity_highlights.append(log)
        # FloodRecordActivity
        for flood in FloodRecordActivity.objects.all().order_by('-timestamp')[:5]:
            flood.type = 'FloodRecordActivity'
            flood.description = f"{flood.get_action_display()} flood record for {flood.event_type} by {flood.user.username}"
            flood.date = flood.timestamp
            recent_activity_highlights.append(flood)
        # AssessmentRecord
        for assess in AssessmentRecord.objects.all().order_by('-timestamp')[:5]:
            assess.type = 'AssessmentRecord'
            assess.summary = f"Assessment for {assess.barangay} by {assess.user.username}"
            assess.date = assess.timestamp
            recent_activity_highlights.append(assess)
        # ReportRecord
        for report in ReportRecord.objects.all().order_by('-timestamp')[:5]:
            report.type = 'ReportRecord'
            report.summary = f"Report for {report.barangay} by {report.user.username}"
            report.date = report.timestamp
            recent_activity_highlights.append(report)
        # CertificateRecord
        for cert in CertificateRecord.objects.all().order_by('-timestamp')[:5]:
            cert.type = 'CertificateRecord'
            cert.summary = f"Certificate for {cert.establishment_name} by {cert.user.username}"
            cert.date = cert.timestamp
            recent_activity_highlights.append(cert)
        # Sort all by date/timestamp descending
        recent_activity_highlights.sort(key=lambda x: getattr(x, 'timestamp', getattr(x, 'date', None)), reverse=True)
        context['total_activities'] = total_activities
        context['most_active_user'] = most_active_user
        context['recent_activity_highlights'] = recent_activity_highlights[:5]
    
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
        'rainfall_data': rainfall_data,
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
    """
    View and edit user profile.
    Handles profile information updates including profile image uploads.
    """
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            UserLog.objects.create(user=user, action="Updated profile")
            messages.success(request, 'Profile updated successfully!')
            return redirect('view_profile')
        else:
            # Keep form errors and data for modal to reopen
            messages.error(request, 'Error updating profile. Please check the form and try again.')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})