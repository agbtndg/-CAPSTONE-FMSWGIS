from django.core.serializers import serialize
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Barangay, FloodSusceptibility, AssessmentRecord, ReportRecord, CertificateRecord
from datetime import datetime

@login_required
def map_view(request):
    barangays = serialize('geojson', Barangay.objects.all(), geometry_field='geometry', fields=('id', 'name', 'parent_id', 'geometry'))
    flood_areas = serialize('geojson', FloodSusceptibility.objects.all(), geometry_field='geometry', fields=('lgu', 'psgc_lgu', 'haz_class', 'haz_code', 'haz_area_ha', 'geometry'))
    barangay_names = Barangay.objects.values_list('name', flat=True).order_by('name')
    return render(request, 'maps/map.html', {
        'barangays_json': barangays,
        'flood_areas_json': flood_areas,
        'barangay_names': barangay_names
    })

@login_required
def report_view(request):
    # Get parameters from URL
    barangay = request.GET.get('barangay', 'Unknown')
    latitude = request.GET.get('lat', '0.000000')
    longitude = request.GET.get('lon', '0.000000')
    risk_code = request.GET.get('risk', 'Unknown')
    
    # Risk assessment and recommendation mapping
    risk_data = {
        'LF': {
            'label': 'Low Susceptibility; less than 0.5 meters flood height and/or less than 1 day flooding',
            'class': 'risk-low',
            'assessment': 'Low Susceptibility; less than 0.5 meters flood height and/or less than 1 day flooding',
            'recommendation': 'Areas with low susceptibility to floods are likely to experience flood heights of less than 0.5 meters and/or flood duration of less than 1 day. These include low hills and gentle slopes that have sparse to moderate drainage density.\n\nThe implementation of appropriate mitigation measures as deemed necessary by project engineers and LGU building officials is recommended for areas that are susceptible to various flood depths. Site-specific studies including the assessment for other types of hazards should also be conducted to address potential foundation problems.'
        },
        'MF': {
            'label': 'Moderate Susceptibility; 0.5 to 1 meter flood height and/or 1 to 3 days flooding',
            'class': 'risk-moderate',
            'assessment': 'Moderate Susceptibility; 0.5 to 1 meter flood height and/or 1 to 3 days flooding',
            'recommendation': 'Areas with moderate susceptibility to floods are likely to experience flood heights of 0.5 meters up to 1 meter and/or flood duration of 1 to 3 days. These are subject to widespread inundation during prolonged and extensive heavy rainfall or extreme weather conditions. Fluvial terraces, alluvial fans, and infilled valleys are also moderately subjected to flooding.\n\nThe implementation of appropriate mitigation measures as deemed necessary by project engineers and LGU building officials is recommended for areas that are susceptible to various flood depths. Site-specific studies including the assessment for other types of hazards should also be conducted to address potential foundation problems.'
        },
        'HF': {
            'label': 'High Susceptibility; 1 to 2 meters flood height and/or more than 3 days flooding',
            'class': 'risk-high',
            'assessment': 'High Susceptibility; 1 to 2 meters flood height and/or more than 3 days flooding',
            'recommendation': 'Areas with high susceptibility to floods are likely to experience flood heights of 1 meter up to 2 meters and/or flood duration of more than 3 days. Sites including active river channels, abandoned river channels, and areas along riverbanks, are immediately flooded during heavy rains of several hours and are prone to flash floods. These may be considered not suitable for permanent habitation but may be developed for alternative uses subject to the implementation of appropriate mitigation measures after conducting site-specific geotechnical studies as deemed necessary by project engineers and LGU building officials.\n\nThe implementation of appropriate mitigation measures as deemed necessary by project engineers and LGU building officials is recommended for areas that are susceptible to various flood depths. Site-specific studies including the assessment for other types of hazards should also be conducted to address potential foundation problems.'
        },
        'VHF': {
            'label': 'Very High Susceptibility; more than 2 meters flood height and/or more than 3 days flooding',
            'class': 'risk-very-high',
            'assessment': 'Very High Susceptibility; more than 2 meters flood height and/or more than 3 days flooding',
            'recommendation': 'Areas with very high susceptibility to floods are likely to experience flood heights of greater than 2 meters and/or flood duration of more than 3 days. These include active river channels, abandoned river channels, and areas along riverbanks, which are immediately flooded during heavy rains of several hours and are prone to flash floods. These are considered critical geohazard areas and are not suitable for development. It is recommended that these be declared as "No Habitation/No Build Zones" by the LGU, and that affected households/communities be relocated.\n\nThe implementation of appropriate mitigation measures as deemed necessary by project engineers and LGU building officials is recommended for areas that are susceptible to various flood depths. Site-specific studies including the assessment for other types of hazards should also be conducted to address potential foundation problems.'
        }
    }
    
    # Get the appropriate risk data or use default
    current_risk = risk_data.get(risk_code, {
        'label': 'Unknown Risk Level',
        'class': '',
        'assessment': 'No risk data available',
        'recommendation': 'Please conduct a proper assessment.'
    })
    
    # Save report generation record
    ReportRecord.objects.create(
        user=request.user,
        barangay=barangay,
        latitude=latitude,
        longitude=longitude,
        flood_risk_code=risk_code,
        flood_risk_label=current_risk['label']
    )
    
    # Format current date
    current_date = datetime.now().strftime('%d %B %Y, %I:%M %p')
    
    context = {
        'barangay': barangay,
        'latitude': latitude,
        'longitude': longitude,
        'risk_code': risk_code,
        'risk_label': current_risk['label'],
        'risk_class': current_risk['class'],
        'assessment_text': current_risk['assessment'],
        'recommendation_text': current_risk['recommendation'],
        'current_date': current_date,
    }
    
    return render(request, 'maps/report.html', context)

@login_required
def certificate_form_view(request):
    # Get parameters from URL
    barangay = request.GET.get('barangay', 'Unknown')
    latitude = request.GET.get('lat', '0.000000')
    longitude = request.GET.get('lon', '0.000000')
    risk_code = request.GET.get('risk', 'Unknown')
    
    # Map risk codes to full susceptibility text
    risk_mapping = {
        'LF': 'LOW FLOOD SUSCEPTIBILITY',
        'MF': 'MODERATE FLOOD SUSCEPTIBILITY',
        'HF': 'HIGH FLOOD SUSCEPTIBILITY',
        'VHF': 'VERY HIGH FLOOD SUSCEPTIBILITY'
    }
    
    # Map risk codes to zone status
    zone_mapping = {
        'LF': 'SAFE ZONE',
        'MF': 'CONTROLLED ZONE',
        'HF': 'CRITICAL ZONE',
        'VHF': 'NO HABITATION/BUILD ZONE'
    }
    
    flood_susceptibility = risk_mapping.get(risk_code, 'UNKNOWN FLOOD SUSCEPTIBILITY')
    zone_status = zone_mapping.get(risk_code, '')
    
    # Generate current date with proper suffix
    from datetime import datetime
    today = datetime.now()
    day = today.day
    
    # Add suffix to day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    issue_date = f"{day}{suffix} of {today.strftime('%B %Y')}"
    
    context = {
        'barangay': barangay,
        'latitude': latitude,
        'longitude': longitude,
        'risk_code': risk_code,
        'flood_susceptibility': flood_susceptibility,
        'zone_status': zone_status,
        'issue_date': issue_date,
    }
    
    return render(request, 'maps/certificate_form.html', context)

@login_required
def certificate_view(request):
    if request.method == 'POST':
        # Get form data
        establishment_name = request.POST.get('establishment_name', '')
        owner_name = request.POST.get('owner_name', '')
        location = request.POST.get('location', '')
        barangay = request.POST.get('barangay', 'Unknown')
        zone_status = request.POST.get('zone_status', '')
        issue_date = request.POST.get('issue_date', '')
        signatory_name = request.POST.get('signatory_name', '')
        signatory_title = request.POST.get('signatory_title', '')
        signatory_subtitle = request.POST.get('signatory_subtitle', '')
        
        # Get assessment data from hidden fields
        latitude = request.POST.get('latitude', '0.000000')
        longitude = request.POST.get('longitude', '0.000000')
        flood_susceptibility = request.POST.get('flood_susceptibility', 'Unknown')
        risk_code = request.POST.get('risk_code', 'Unknown')
        
        # Save certificate generation record
        CertificateRecord.objects.create(
            user=request.user,
            establishment_name=establishment_name,
            owner_name=owner_name,
            location=location,
            barangay=barangay,
            latitude=latitude,
            longitude=longitude,
            flood_susceptibility=flood_susceptibility,
            zone_status=zone_status,
            issue_date=issue_date
        )
        
        context = {
            'establishment_name': establishment_name,
            'owner_name': owner_name,
            'location': location,
            'barangay': barangay.upper(),
            'flood_susceptibility': flood_susceptibility,
            'zone_status': zone_status,
            'issue_date': issue_date,
            'signatory_name': signatory_name,
            'signatory_title': signatory_title,
            'signatory_subtitle': signatory_subtitle,
        }
        
        return render(request, 'maps/certificate.html', context)
    
    # If not POST, redirect to form
    return redirect('map_view')

# New view for saving assessments via AJAX
@login_required
def save_assessment(request):
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    
    if request.method == 'POST':
        barangay = request.POST.get('barangay', 'Unknown')
        latitude = request.POST.get('latitude', '0.000000')
        longitude = request.POST.get('longitude', '0.000000')
        flood_risk_code = request.POST.get('flood_risk_code', 'Unknown')
        
        # Map risk codes to descriptions
        risk_descriptions = {
            'LF': 'Low Flood Susceptibility',
            'MF': 'Moderate Flood Susceptibility',
            'HF': 'High Flood Susceptibility',
            'VHF': 'Very High Flood Susceptibility'
        }
        
        flood_risk_description = risk_descriptions.get(flood_risk_code, 'Unknown')
        
        # Save assessment record
        assessment = AssessmentRecord.objects.create(
            user=request.user,
            barangay=barangay,
            latitude=latitude,
            longitude=longitude,
            flood_risk_code=flood_risk_code,
            flood_risk_description=flood_risk_description
        )
        
        return JsonResponse({
            'success': True,
            'assessment_id': assessment.id,
            'message': 'Assessment saved successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# View for staff to see their own activity history
@login_required
def my_activity(request):
    assessments = AssessmentRecord.objects.filter(user=request.user)
    reports = ReportRecord.objects.filter(user=request.user)
    certificates = CertificateRecord.objects.filter(user=request.user)
    
    context = {
        'assessments': assessments,
        'reports': reports,
        'certificates': certificates,
        'total_assessments': assessments.count(),
        'total_reports': reports.count(),
        'total_certificates': certificates.count(),
    }
    
    return render(request, 'maps/my_activity.html', context)

# View for admin to see all staff activities
@login_required
def all_activities(request):
    from django.contrib.admin.views.decorators import staff_member_required
    from django.core.exceptions import PermissionDenied
    
    if not request.user.is_staff:
        raise PermissionDenied
    
    assessments = AssessmentRecord.objects.all().select_related('user')
    reports = ReportRecord.objects.all().select_related('user')
    certificates = CertificateRecord.objects.all().select_related('user')
    
    # Get filter parameters
    filter_user = request.GET.get('user', None)
    filter_date = request.GET.get('date', None)
    
    if filter_user:
        assessments = assessments.filter(user__id=filter_user)
        reports = reports.filter(user__id=filter_user)
        certificates = certificates.filter(user__id=filter_user)
    
    if filter_date:
        assessments = assessments.filter(timestamp__date=filter_date)
        reports = reports.filter(timestamp__date=filter_date)
        certificates = certificates.filter(timestamp__date=filter_date)
    
    # Get all users for filter dropdown
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'assessments': assessments,
        'reports': reports,
        'certificates': certificates,
        'users': users,
        'filter_user': filter_user,
        'filter_date': filter_date,
        'total_assessments': assessments.count(),
        'total_reports': reports.count(),
        'total_certificates': certificates.count(),
    }
    
    return render(request, 'maps/all_activities.html', context)