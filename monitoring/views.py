from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
import requests
from .models import RainfallData, WeatherData, TideLevelData, FloodRecord
from django.utils import timezone
from datetime import timedelta
import json
from .forms import FloodRecordForm, BARANGAYS
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required

# Set up logging
logger = logging.getLogger(__name__)


def get_flood_risk_level(rainfall_mm):
    """Determine flood risk level based on rainfall."""
    if rainfall_mm > 100:
        return "Critical Risk (>100mm)", "red"
    elif rainfall_mm >= 50:
        return "High Risk (50-100mm)", "orange"
    elif rainfall_mm >= 30:
        return "Moderate Risk (30-50mm)", "yellow"
    else:
        return "Low Risk (<30mm)", "green"
    

def get_tide_risk_level(tide_m):
    """Determine tide risk level based on height."""
    if tide_m > 2.0:
        return "Critical Risk (>2.0m)", "red"
    elif tide_m >= 1.5:
        return "High Risk (1.5-2.0m)", "orange"
    elif tide_m >= 1.0:
        return "Moderate Risk (1.0-1.5m)", "yellow"
    else:
        return "Low Risk (<1.0m)", "green"
    

def get_combined_risk_level(rain_risk, tide_risk):
    """Determine combined risk level based on the higher of rain or tide risk."""
    risk_levels = {"Low Risk": 1, "Moderate Risk": 2, "High Risk": 3, "Critical Risk": 4}
    rain_level = max(risk_levels.get(rain_risk.split('(')[0].strip(), 1), 1)
    tide_level = max(risk_levels.get(tide_risk.split('(')[0].strip(), 1), 1)
    combined_level = max(rain_level, tide_level)
    if combined_level == 4:
        return "Critical Risk", "red"
    elif combined_level == 3:
        return "High Risk", "orange"
    elif combined_level == 2:
        return "Moderate Risk", "yellow"
    else:
        return "Low Risk", "green"
    
@login_required
def monitoring_view(request):
    # Fetch or create initial data
    rainfall_data = RainfallData.objects.last()
    weather_data = WeatherData.objects.last()
    tide_data = TideLevelData.objects.last()

    # Fetch rainfall and weather data from Open-Meteo API
    try:
        api_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': 10.293,  # Cebu City coordinates
            'longitude': 123.903,
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,rain',
            'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,rain',
            'timezone': 'Asia/Manila',
            'forecast_days': 1
        }
        
        logger.info(f"Requesting Open-Meteo API for Cebu City: {api_url}")
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Use current weather data for real-time values
        current = data.get('current', {})
        rainfall_value = current.get('rain', 0)  # Current rain in mm
        temperature = current.get('temperature_2m', 28.5)
        humidity = current.get('relative_humidity_2m', 75)
        wind_speed = current.get('wind_speed_10m', 10)
        
        logger.info(f"API returned - Rain: {rainfall_value}mm, Temp: {temperature}°C, Humidity: {humidity}%, Wind: {wind_speed}km/h")

        # Only create new records if data is older than 3 hours OR doesn't exist
        if not rainfall_data or (timezone.now() - rainfall_data.timestamp).total_seconds() > 10800:
            rainfall_data = RainfallData.objects.create(value_mm=rainfall_value, station_name='Cebu City')
            logger.info(f"Created new rainfall record: {rainfall_value}mm")

        if not weather_data or (timezone.now() - weather_data.timestamp).total_seconds() > 10800:
            weather_data = WeatherData.objects.create(
                temperature_c=temperature,
                humidity_percent=humidity,
                wind_speed_kph=wind_speed,
                station_name='Cebu City'
            )
            logger.info(f"Created new weather record")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Open-Meteo API Error: {e}")
        if not rainfall_data:
            rainfall_data = RainfallData.objects.create(value_mm=0, station_name='Cebu City')
            logger.warning("Created default rainfall record due to API error")
        if not weather_data:
            weather_data = WeatherData.objects.create(
                temperature_c=28.5,
                humidity_percent=75,
                wind_speed_kph=10,
                station_name='Cebu City'
            )
            logger.warning("Created default weather record due to API error")
    except Exception as e:
        logger.error(f"Unexpected error fetching weather data: {e}")

    # Fetch tide data from WorldTides API
    try:
        if not tide_data or (timezone.now() - tide_data.timestamp).total_seconds() > 10800:
            tide_api_url = "https://www.worldtides.info/api/v3"
            params = {
                'heights': '',
                'lat': 10.293,
                'lon': 123.903,
                'key': settings.WORLDTIDES_API_KEY,
                'date': timezone.now().strftime('%Y-%m-%d'),
                'days': 1
            }
            
            logger.info(f"Requesting WorldTides API for Cebu City: {tide_api_url}")
            tide_response = requests.get(tide_api_url, params=params, timeout=10)
            
            if tide_response.status_code == 200:
                tide_data_json = tide_response.json()
                heights = tide_data_json.get('heights', [])
                
                if heights:
                    now_timestamp = timezone.now().timestamp()
                    closest_height = min(heights, key=lambda x: abs(x['dt'] - now_timestamp))
                    tide_value = closest_height.get('height', 0.8)
                    
                    tide_data = TideLevelData.objects.create(height_m=tide_value, station_name='Cebu City')
                    logger.info(f"Created new tide record: {tide_value}m from WorldTides API")
                else:
                    logger.warning("No tide heights in WorldTides API response")
                    
            elif tide_response.status_code == 402:
                logger.error("WorldTides API quota exceeded (402) - Please purchase more credits")
            elif tide_response.status_code == 401:
                logger.error("WorldTides API authentication failed (401) - Check your API key")
            else:
                logger.error(f"WorldTides API error: {tide_response.status_code} - {tide_response.text}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"WorldTides API Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching tide data: {e}")
    
    if not tide_data:
        tide_data = TideLevelData.objects.create(height_m=0.8, station_name='Cebu City')
        logger.warning("Created default tide record")

    # Convert QuerySets to lists of dictionaries for JSON serialization
    rainfall_history = list(RainfallData.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('timestamp').values('timestamp', 'value_mm'))
    
    tide_history = list(TideLevelData.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).order_by('timestamp').values('timestamp', 'height_m'))
    
    # Order by date ascending for proper graph display, and include ID for edit/delete
    flood_records = list(FloodRecord.objects.all().order_by('date')[:20].values(
        'id', 'event', 'date', 'affected_barangays', 'casualties_dead', 'casualties_injured', 'casualties_missing',
        'affected_persons', 'affected_families', 'houses_damaged_partially', 'houses_damaged_totally',
        'damage_infrastructure_php', 'damage_agriculture_php', 'damage_institutions_php',
        'damage_private_commercial_php', 'damage_total_php'
    ))

    # Aggregate data for graphs
    dates = [record['date'].strftime('%Y-%m-%d') for record in flood_records]
    casualties_data = {
        'dead': [record['casualties_dead'] for record in flood_records],
        'injured': [record['casualties_injured'] for record in flood_records],
        'missing': [record['casualties_missing'] for record in flood_records],
    }
    affected_data = {
        'persons': [record['affected_persons'] for record in flood_records],
        'families': [record['affected_families'] for record in flood_records],
    }
    houses_data = {
        'partially': [record['houses_damaged_partially'] for record in flood_records],
        'totally': [record['houses_damaged_totally'] for record in flood_records],
    }
    damage_data = {
        'infrastructure': [float(record['damage_infrastructure_php']) for record in flood_records],
        'agriculture': [float(record['damage_agriculture_php']) for record in flood_records],
        'institutions': [float(record['damage_institutions_php']) for record in flood_records],
        'private_commercial': [float(record['damage_private_commercial_php']) for record in flood_records],
        'total': [float(record['damage_total_php']) for record in flood_records],
    }

    # Prepare rainfall and tide trend data
    rainfall_timestamps = [r['timestamp'].strftime('%Y-%m-%d %H:%M') for r in rainfall_history]
    rainfall_values = [r['value_mm'] for r in rainfall_history]
    tide_timestamps = [t['timestamp'].strftime('%Y-%m-%d %H:%M') for t in tide_history]
    tide_values = [t['height_m'] for t in tide_history]

    # Determine flood risk levels
    rain_risk_level, rain_risk_color = get_flood_risk_level(rainfall_data.value_mm if rainfall_data else 0)
    tide_risk_level, tide_risk_color = get_tide_risk_level(tide_data.height_m if tide_data else 0)
    combined_risk_level, combined_risk_color = get_combined_risk_level(rain_risk_level, tide_risk_level)

    context = {
        'rainfall_data': rainfall_data,
        'weather_data': weather_data,
        'tide_data': tide_data,
        'rainfall_history': rainfall_history,
        'tide_history': tide_history,
        'rain_risk_level': rain_risk_level,
        'rain_risk_color': rain_risk_color,
        'tide_risk_level': tide_risk_level,
        'tide_risk_color': tide_risk_color,
        'combined_risk_level': combined_risk_level,
        'combined_risk_color': combined_risk_color,
        'flood_records': flood_records,
        'graph_dates': dates,
        'casualties_data': casualties_data,
        'affected_data': affected_data,
        'houses_data': houses_data,
        'damage_data': damage_data,
        'rainfall_timestamps': rainfall_timestamps,
        'rainfall_values': rainfall_values,
        'tide_timestamps': tide_timestamps,
        'tide_values': tide_values,
    }
    return render(request, 'monitoring/monitoring.html', context)

@login_required
def fetch_data_api(request):
    """API endpoint for AJAX updates with error handling."""
    try:
        data = {
            'rainfall': RainfallData.objects.last().value_mm if RainfallData.objects.exists() else 0,
            'temperature': WeatherData.objects.last().temperature_c if WeatherData.objects.exists() else 0,
            'tide': TideLevelData.objects.last().height_m if TideLevelData.objects.exists() else 0,
        }
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in fetch_data_api: {e}")
        return JsonResponse({'error': 'Unable to fetch data'}, status=500)

@login_required
def flood_record_form(request):
    """Handle flood record form submission with comprehensive error handling."""
    if request.method == 'POST':
        form = FloodRecordForm(request.POST)
        
        try:
            if form.is_valid():
                flood_record = form.save()
                
                # Log the activity (import at top of file)
                from maps.models import FloodRecordActivity
                FloodRecordActivity.objects.create(
                    user=request.user,
                    action='CREATE',
                    flood_record_id=flood_record.id,
                    event_type=flood_record.event,
                    event_date=flood_record.date,
                    affected_barangays=flood_record.affected_barangays,
                    casualties_dead=flood_record.casualties_dead,
                    casualties_injured=flood_record.casualties_injured,
                    casualties_missing=flood_record.casualties_missing,
                    affected_persons=flood_record.affected_persons,
                    affected_families=flood_record.affected_families,
                    damage_total_php=flood_record.damage_total_php
                )
                
                success_message = f'✅ Flood record for {flood_record.event} on {flood_record.date.strftime("%Y-%m-%d")} has been successfully added!'
                logger.info(f"Flood record created: {flood_record.id} - {flood_record.event}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'redirect_url': reverse('monitoring_view')
                    })
                
                messages.success(request, success_message)
                return redirect('monitoring_view')
            else:
                error_message = '❌ Please correct the errors below and try again.'
                logger.warning(f"Form validation errors: {form.errors}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': form.errors
                    })
                    
                messages.error(request, error_message)
        except Exception as e:
            error_message = f'❌ An unexpected error occurred while saving the record: {str(e)}'
            logger.error(f"Error saving flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
            messages.error(request, error_message)
    else:
        form = FloodRecordForm()
    
    return render(request, 'monitoring/flood_record_form.html', {
        'form': form, 
        'BARANGAYS': BARANGAYS
    })

@login_required
def flood_record_edit(request, record_id):
    """Handle editing of existing flood record."""
    flood_record = get_object_or_404(FloodRecord, id=record_id)
    
    if request.method == 'POST':
        form = FloodRecordForm(request.POST, instance=flood_record)
        
        try:
            if form.is_valid():
                flood_record = form.save()
                success_message = f'✅ Flood record for {flood_record.event} on {flood_record.date.strftime("%Y-%m-%d")} has been successfully updated!'
                logger.info(f"Flood record updated: {flood_record.id} - {flood_record.event}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': success_message,
                        'redirect_url': reverse('monitoring_view')
                    })
                
                messages.success(request, success_message)
                return redirect('monitoring_view')
            else:
                error_message = '❌ Please correct the errors below and try again.'
                logger.warning(f"Form validation errors: {form.errors}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': error_message,
                        'errors': form.errors
                    })
                    
                messages.error(request, error_message)
        except Exception as e:
            error_message = f'❌ An unexpected error occurred while updating the record: {str(e)}'
            logger.error(f"Error updating flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
                
            messages.error(request, error_message)
    else:
        form = FloodRecordForm(instance=flood_record)
    
    return render(request, 'monitoring/flood_record_edit.html', {
        'form': form,
        'BARANGAYS': BARANGAYS,
        'record': flood_record
    })

@login_required
def flood_record_delete(request, record_id):
    """Handle deletion of flood record."""
    flood_record = get_object_or_404(FloodRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            event_name = flood_record.event
            event_date = flood_record.date.strftime("%Y-%m-%d")
            flood_record.delete()
            
            success_message = f'✅ Flood record for {event_name} on {event_date} has been successfully deleted!'
            logger.info(f"Flood record deleted: {record_id} - {event_name}")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'redirect_url': reverse('monitoring_view')
                })
            
            messages.success(request, success_message)
            return redirect('monitoring_view')
        except Exception as e:
            error_message = f'❌ An error occurred while deleting the record: {str(e)}'
            logger.error(f"Error deleting flood record: {e}", exc_info=True)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            
            messages.error(request, error_message)
            return redirect('monitoring_view')
    
    return render(request, 'monitoring/flood_record_delete.html', {
        'record': flood_record
    })