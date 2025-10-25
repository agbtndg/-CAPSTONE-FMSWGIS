from django.db import models

class RainfallData(models.Model):
    value_mm = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class WeatherData(models.Model):
    temperature_c = models.FloatField(default=28.5)
    humidity_percent = models.IntegerField(default=75)
    wind_speed_kph = models.FloatField(default=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class TideLevelData(models.Model):
    height_m = models.FloatField(default=0.8)
    timestamp = models.DateTimeField(auto_now_add=True)
    station_name = models.CharField(max_length=100, default='Silay City')

class FloodRecord(models.Model):
    event = models.CharField(max_length=200)
    date = models.DateTimeField()
    affected_barangays = models.CharField(max_length=500)
    casualties_dead = models.IntegerField(default=0)
    casualties_injured = models.IntegerField(default=0)
    casualties_missing = models.IntegerField(default=0)
    affected_persons = models.IntegerField(default=0)
    affected_families = models.IntegerField(default=0)
    houses_damaged_partially = models.IntegerField(default=0)
    houses_damaged_totally = models.IntegerField(default=0)
    damage_infrastructure_php = models.FloatField(default=0)
    damage_agriculture_php = models.FloatField(default=0)
    damage_institutions_php = models.FloatField(default=0)
    damage_private_commercial_php = models.FloatField(default=0)
    damage_total_php = models.FloatField(default=0)

    def __str__(self):
        return f"{self.event} - {self.date}"