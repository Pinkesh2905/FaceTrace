"""
Main URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root URL -> Public Landing Page
    path('', account_views.landing_page, name='home'),
    
    # App URLs
    path('', include('employees.urls')),     # Includes /dashboard/ and /employees/
    path('', include('accounts.urls')),      # Auth: Login, Logout, Company Registration
    path('recognition/', include('recognition.urls')),   # Live Face Recognition
    path('attendance/', include('attendance.urls')),     # Attendance Reports
    # path('cameras/', include('cameras.urls')),           # Camera Management
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin customization
admin.site.site_header = "FaceCognition Platform Admin"
admin.site.site_title = "FaceCognition Admin Portal"
admin.site.index_title = "Welcome to FaceCognition Platform"