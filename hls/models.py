from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    hls_playlists = models.JSONField(default=dict)  # Storing multiple playlists
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when video was uploaded
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when video was last updated

    def __str__(self):
        return self.title

    def get_hls_url(self):
        """
        Returns the HLS playlist URL if available, otherwise returns None.
        """
        if self.hls_playlist:
            return self.hls_playlist.url
        return None