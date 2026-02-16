import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from py_yt import VideosSearch

class AppleMusicAPI:
    def __init__(self):
        self.url_pattern = r"^(https:\/\/music.apple.com\/)(.*)$"
        self.base_url = "https://music.apple.com/in/playlist/"

    async def valid(self, link: str) -> bool:
        return bool(re.search(self.url_pattern, link))

    async def track(self, url: str, playid: Union[bool, str] = None):
        target_url = self.base_url + url if playid else url
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url) as resp:
                if resp.status != 200:
                    return False
                page_html = await resp.text()
                
        soup = BeautifulSoup(page_html, "html.parser")
        search_query = None
        
        for meta_tag in soup.find_all("meta"):
            if meta_tag.get("property") == "og:title":
                search_query = meta_tag.get("content")
                
        if not search_query:
            return False
            
        yt_search = VideosSearch(search_query, limit=1)
        search_data = (await yt_search.next())["result"]
        
        for item in search_data:
            track_data = {
                "title": item["title"],
                "link": item["link"],
                "vidid": item["id"],
                "duration_min": item["duration"],
                "thumb": item["thumbnails"][0]["url"].split("?")[0],
            }
            return track_data, item["id"]

    async def playlist(self, url: str, playid: Union[bool, str] = None):
        target_url = self.base_url + url if playid else url
        p_id = target_url.split("playlist/")[1]
        
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url) as resp:
                if resp.status != 200:
                    return False
                page_html = await resp.text()
                
        soup = BeautifulSoup(page_html, "html.parser")
        song_tags = soup.find_all("meta", attrs={"property": "music:song"})
        
        extracted_songs = []
        for tag in song_tags:
            try:
                formatted_name = (((tag["content"]).split("album/")[1]).split("/")[0]).replace("-", " ")
            except IndexError:
                formatted_name = ((tag["content"]).split("album/")[1]).split("/")[0]
            extracted_songs.append(formatted_name)
            
        return extracted_songs, p_id