from django.shortcuts import render
import subprocess
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from .models import Video
import os 

def index(request):

    return render(request, 'hls/index.html')

def video_player(request, id):

     try:
        # Retrieve the video instance by ID
        video = Video.objects.get(id=id)

        # Return the HLS playlists in JSON format
        context = {
                'id': id,
                'video':video,
            }
        return render(request, 'hls/play.html', context)
        # return JsonResponse({
        #     'success': True,
        #     'hls_playlists': video.hls_playlists  # This will return the entire JSON structure
        # })

     except Video.DoesNotExist:
        # Return an error response if the video does not exist
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)

       

  

def process_video(video_path, output_dir, video_instance):
    print('--- start processing video ---')
    
    qualities = {
        '240p': {'resolution': '426x240', 'bitrate': '300k'},
        '360p': {'resolution': '640x360', 'bitrate': '600k'},
        '480p': {'resolution': '854x480', 'bitrate': '1200k'},
        '720p': {'resolution': '1280x720', 'bitrate': '2500k'},
    }
    
    hls_playlists = {}
    
    for quality, settings in qualities.items():
        hls_file_path = os.path.join(output_dir, f'playlist_{quality}.m3u8')
        
        # The FFmpeg command to convert video to HLS format
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'scale={settings["resolution"]}',
            '-b:v', settings["bitrate"],
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-f', 'hls',
            hls_file_path
        ]
        
        # Run FFmpeg command and capture output
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode == 0:
            # Save the HLS playlist URL in the hls_playlists dictionary
            hls_playlists[quality] = f'/media/videos/hls/{video_instance.id}/playlist_{quality}.m3u8'  # Using forward slashes
        else:
            print(f'Failed to create playlist for {quality}: {result.stderr.decode()}')
    
    # Update the video instance's hls_playlists field
    video_instance.hls_playlists = hls_playlists
    video_instance.save()


def get_video_url(request, video_id):
    try:
        # Retrieve the video instance by ID
        video = Video.objects.get(id=video_id)

        # Return the HLS playlists in JSON format
        return JsonResponse({
            'success': True,
            'hls_playlists': video.hls_playlists  # This will return the entire JSON structure
        })

    except Video.DoesNotExist:
        # Return an error response if the video does not exist
        return JsonResponse({
            'success': False,
            'error': 'Video not found'
        }, status=404)


def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video_file')
        title = request.POST.get('title')
        
        if video_file:
            # Create a Video instance
            video_instance = Video.objects.create(video_file=video_file, title=title)

            # Define the output directory for HLS files
            output_dir = os.path.join('media', 'videos', 'hls', str(video_instance.id))
            os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

            # Call the process_video function and pass the video_instance
            hls_playlists = process_video(video_instance.video_file.path, output_dir, video_instance)

            return JsonResponse({
                'success': True,
                'hls_playlists': hls_playlists
            })
        else:
            return JsonResponse({'success': False, 'error': 'No video file uploaded'}, status=400)

    return render(request, 'hls/upload.html')  # Your upload template