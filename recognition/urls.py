"""
Recognition URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    path('live/', views.live_feed_view, name='live_feed'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('refresh_encodings/', views.refresh_encodings, name='refresh_encodings'),
]