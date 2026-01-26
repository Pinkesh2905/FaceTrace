from django.urls import path
from . import views

urlpatterns = [
    path('live/', views.live_feed_view, name='live_feed'),
    path('api/recognize/', views.recognize_frame, name='recognize_frame_api'),
]