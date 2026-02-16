import re
from typing import Union
import aiohttp
from bs4 import BeautifulSoup
from py_yt import VideosSearch

class RessoMusicAPI:
    def __init__(self):
        self.url_pattern = r"^(https:\/\/m.resso.com\/)(.*)$"
        self.base_url = "https://m.resso.com/"

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
        title_text = ""
        desc_text = ""
        
        for meta_tag in soup.find_all("meta"):
            if meta_tag.get("property") == "og:title":
                title_text = meta_tag.get("content", "")
            if meta_tag.get("property") == "og:description":
                raw_desc = meta_tag.get("content", "")
                try:
                    desc_text = raw_desc.split("·")[0]
                except Exception:
                    desc_text = raw_desc
                    
        if not desc_text:
            return None
            
        yt_search = VideosSearch(title_text, limit=1)
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