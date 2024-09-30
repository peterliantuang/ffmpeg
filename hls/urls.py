from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('upload/', views.upload_video, name='upload'),
    path('api/video/<int:video_id>/', views.get_video_url, name='get_video_url'),  # New API endpoint
    path('play/<id>/', views.video_player, name='play'),  # New API endpoint
]
