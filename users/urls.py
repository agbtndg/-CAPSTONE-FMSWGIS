from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('approve/', views.approve_users, name='approve_users'),
    path('logout/', views.user_logout, name='logout'),
    path('logs/', views.user_logs, name='user_logs'),
    path('profile/', views.view_profile, name='view_profile'),
]