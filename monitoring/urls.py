from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitoring_view, name='monitoring_view'),
    path('api/data/', views.fetch_data_api, name='fetch_data'),
    path('api/trends/', views.fetch_trends_api, name='fetch_trends'),
    path('flood-record/', views.flood_record_form, name='flood_record_form'),
    path('flood-record/edit/<int:record_id>/', views.flood_record_edit, name='flood_record_edit'),
    path('flood-record/delete/<int:record_id>/', views.flood_record_delete, name='flood_record_delete'),
    
]