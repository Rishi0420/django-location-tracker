"""
URL configuration for location_tracker_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tracker_app import views as tracker_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # API URLs for /api/
    path('api/', include('tracker_app.urls', namespace='api')),

    # Web Interface URLs
    path('map/', tracker_views.map_view, name='map_view'),
    path('track/', tracker_views.track_device_view, name='track_device'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='tracker_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', tracker_views.register, name='register'),

    # Home Page
    path('', tracker_views.home_view, name='home'),

    path('dashboard/', tracker_views.admin_dashboard_view, name='admin_dashboard'),

    path('', include('pwa.urls')),  # Add this URL at the end for PWA

    path('create-superuser-now-9876543210/',
         tracker_views.create_superuser_temp, name='create_superuser_temp'),
]
