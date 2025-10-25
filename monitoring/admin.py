from django.contrib import admin
from .models import RainfallData, WeatherData, TideLevelData, FloodRecord

admin.site.register(RainfallData)
admin.site.register(WeatherData)
admin.site.register(TideLevelData)
admin.site.register(FloodRecord)