from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='map_view'),
    path('report/', views.report_view, name='report_view'),
    path('certificate/form/', views.certificate_form_view, name='certificate_form_view'),
    path('certificate/', views.certificate_view, name='certificate_view'),
    path('save-assessment/', views.save_assessment, name='save_assessment'),
    path('my-activity/', views.my_activity, name='my_activity'),
    path('all-activities/', views.all_activities, name='all_activities'),
]