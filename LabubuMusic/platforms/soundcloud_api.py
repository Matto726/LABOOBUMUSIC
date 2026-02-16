from os import path
from yt_dlp import YoutubeDL
from MattoMusic.utils.formatters import seconds_to_min

class SoundCloudAPI:
    def __init__(self):
        self.dl_options = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 3,
            "nooverwrites": False,
            "continuedl": True,
        }

    async def valid(self, link: str) -> bool:
        return "soundcloud" in link.lower()

    async def download(self, url: str):
        downloader = YoutubeDL(self.dl_options)
        try:
            track_info = downloader.extract_info(url, download=False)
        except Exception:
            return False
            
        file_path = path.join("downloads", f"{track_info['id']}.{track_info['ext']}")
        formatted_duration = seconds_to_min(track_info["duration"])
        
        track_data = {
            "title": track_info["title"],
            "duration_sec": track_info["duration"],
            "duration_min": formatted_duration,
            "uploader": track_info["uploader"],
            "filepath": file_path,
        }
        return track_data, file_path