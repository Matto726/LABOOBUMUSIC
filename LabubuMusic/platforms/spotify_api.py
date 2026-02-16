import re
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from py_yt import VideosSearch
import config

class SpotifyMusicAPI:
    def __init__(self):
        self.url_pattern = r"^(https:\/\/open.spotify.com\/)(.*)$"
        self.client_key = config.SPOTIFY_CLIENT_ID
        self.secret_key = config.SPOTIFY_CLIENT_SECRET
        
        if self.client_key and self.secret_key:
            self.auth_manager = SpotifyClientCredentials(self.client_key, self.secret_key)
            self.sp_client = spotipy.Spotify(client_credentials_manager=self.auth_manager)
        else:
            self.sp_client = None

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.url_pattern, link))

    async def track(self, link: str):
        track_data = self.sp_client.track(link)
        query = track_data["name"]
        
        for artist in track_data["artists"]:
            artist_name = f' {artist["name"]}'
            if "Various Artists" not in artist_name:
                query += artist_name
                
        yt_search = VideosSearch(query, limit=1)
        search_res = (await yt_search.next())["result"]
        
        for item in search_res:
            res_data = {
                "title": item["title"],
                "link": item["link"],
                "vidid": item["id"],
                "duration_min": item["duration"],
                "thumb": item["thumbnails"][0]["url"].split("?")[0],
            }
            return res_data, item["id"]

    async def playlist(self, url: str):
        pl_data = self.sp_client.playlist(url)
        pl_id = pl_data["id"]
        track_list = []
        
        for item in pl_data["tracks"]["items"]:
            t_data = item["track"]
            query = t_data["name"]
            for artist in t_data["artists"]:
                artist_name = f' {artist["name"]}'
                if "Various Artists" not in artist_name:
                    query += artist_name
            track_list.append(query)
            
        return track_list, pl_id

    async def album(self, url: str):
        al_data = self.sp_client.album(url)
        al_id = al_data["id"]
        track_list = []
        
        for item in al_data["tracks"]["items"]:
            query = item["name"]
            for artist in item["artists"]:
                artist_name = f' {artist["name"]}'
                if "Various Artists" not in artist_name:
                    query += artist_name
            track_list.append(query)

        return track_list, al_id

    async def artist(self, url: str):
        ar_data = self.sp_client.artist(url)
        ar_id = ar_data["id"]
        track_list = []
        top_tracks = self.sp_client.artist_top_tracks(url)
        
        for item in top_tracks["tracks"]:
            query = item["name"]
            for artist in item["artists"]:
                artist_name = f' {artist["name"]}'
                if "Various Artists" not in artist_name:
                    query += artist_name
            track_list.append(query)

        return track_list, ar_id