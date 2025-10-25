from django.contrib import admin
from .models import Barangay, FloodSusceptibility, AssessmentRecord, ReportRecord, CertificateRecord

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'parent_id']
    search_fields = ['name', 'id']

@admin.register(FloodSusceptibility)
class FloodSusceptibilityAdmin(admin.ModelAdmin):
    list_display = ['lgu', 'haz_code', 'haz_desc', 'haz_area_ha']
    list_filter = ['haz_code', 'lgu']
    search_fields = ['lgu', 'haz_desc']

@admin.register(AssessmentRecord)
class AssessmentRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'barangay', 'flood_risk_code', 'timestamp']
    list_filter = ['flood_risk_code', 'timestamp', 'user']
    search_fields = ['user__username', 'barangay', 'user__staff_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

@admin.register(ReportRecord)
class ReportRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'barangay', 'flood_risk_code', 'timestamp']
    list_filter = ['flood_risk_code', 'timestamp', 'user']
    search_fields = ['user__username', 'barangay', 'user__staff_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'assessment')

@admin.register(CertificateRecord)
class CertificateRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'establishment_name', 'owner_name', 'barangay', 'timestamp']
    list_filter = ['timestamp', 'user', 'zone_status']
    search_fields = ['user__username', 'establishment_name', 'owner_name', 'barangay', 'user__staff_id']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'assessment')