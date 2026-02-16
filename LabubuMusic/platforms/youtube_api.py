import asyncio
import os
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from MattoMusic.utils.formatters import time_to_seconds
import aiohttp
from MattoMusic import LOGGER

try:
    from py_yt import VideosSearch
except ImportError:
    from youtubesearchpython.__future__ import VideosSearch

DOWNLOAD_API_URL = "https://laboobubots.site"

async def fetch_media(link: str, media_type: str) -> str:
    vid_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not vid_id or len(vid_id) < 3:
        return None

    ext = "mp4" if media_type == "video" else "mp3"
    dir_path = "downloads"
    os.makedirs(dir_path, exist_ok=True)
    out_file = os.path.join(dir_path, f"{vid_id}.{ext}")

    if os.path.exists(out_file):
        return out_file

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": vid_id, "type": media_type}
            
            async with session.get(f"{DOWNLOAD_API_URL}/download", params=payload, timeout=7) as api_resp:
                if api_resp.status != 200:
                    return None
                    
                resp_json = await api_resp.json()
                token = resp_json.get("download_token")
                
                if not token:
                    return None
                
                stream_link = f"{DOWNLOAD_API_URL}/stream/{vid_id}?type={media_type}&token={token}"
                timeout_val = 600 if media_type == "video" else 300
                
                async with session.get(stream_link, timeout=timeout_val) as file_req:
                    target_response = file_req
                    
                    if file_req.status == 302:
                        redir = file_req.headers.get('Location')
                        if redir:
                            target_response = await session.get(redir)
                            
                    if target_response.status == 200:
                        with open(out_file, "wb") as disk_file:
                            async for chunk in target_response.content.iter_chunked(16384):
                                disk_file.write(chunk)
                                
                        if os.path.exists(out_file) and os.path.getsize(out_file) > 0:
                            return out_file
                            
        return None
    except Exception:
        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except Exception:
                pass
        return None

async def execute_shell(cmd_str):
    process = await asyncio.create_subprocess_shell(
        cmd_str, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    
    if stderr:
        err_msg = stderr.decode("utf-8")
        if "unavailable videos are hidden" in err_msg.lower():
            return stdout.decode("utf-8")
        return err_msg
    return stdout.decode("utf-8")

class YouTubeCoreAPI:
    def __init__(self):
        self.base_yt = "https://www.youtube.com/watch?v="
        self.yt_pattern = r"(?:youtube\.com|youtu\.be)"
        self.status_url = "https://www.youtube.com/oembed?url="
        self.playlist_base = "https://youtube.com/playlist?list="
        self.escape_reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        target = self.base_yt + link if videoid else link
        return bool(re.search(self.yt_pattern, target))

    async def url(self, msg: Message) -> Union[str, None]:
        msg_list = [msg]
        if msg.reply_to_message:
            msg_list.append(msg.reply_to_message)
            
        for m in msg_list:
            if m.entities:
                for ent in m.entities:
                    if ent.type == MessageEntityType.URL:
                        content = m.text or m.caption
                        return content[ent.offset: ent.offset + ent.length]
            elif m.caption_entities:
                for ent in m.caption_entities:
                    if ent.type == MessageEntityType.TEXT_LINK:
                        return ent.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        yt_search = VideosSearch(target, limit=1)
        res = (await yt_search.next())["result"][0]
        
        dur_min = res["duration"]
        dur_sec = int(time_to_seconds(dur_min)) if dur_min else 0
        return res["title"], dur_min, dur_sec, res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def title(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        res = (await VideosSearch(target, limit=1).next())["result"][0]
        return res["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        res = (await VideosSearch(target, limit=1).next())["result"][0]
        return res["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        res = (await VideosSearch(target, limit=1).next())["result"][0]
        return res["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        try:
            dl_file = await fetch_media(target, "video")
            return (1, dl_file) if dl_file else (0, "Video download failed")
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        target = self.playlist_base + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        cmd_output = await execute_shell(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {target}")
        return [key for key in cmd_output.split("\n") if key]

    async def track(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        res = (await VideosSearch(target, limit=1).next())["result"][0]
        
        return {
            "title": res["title"],
            "link": res["link"],
            "vidid": res["id"],
            "duration_min": res["duration"],
            "thumb": res["thumbnails"][0]["url"].split("?")[0],
        }, res["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        ydl_opts = {"quiet": True}
        available_fmt = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as dl_client:
            info_dict = dl_client.extract_info(target, download=False)
            for fmt in info_dict.get("formats", []):
                if "dash" not in str(fmt.get("format", "")).lower():
                    available_fmt.append({
                        "format": fmt.get("format"),
                        "filesize": fmt.get("filesize"),
                        "format_id": fmt.get("format_id"),
                        "ext": fmt.get("ext"),
                        "format_note": fmt.get("format_note"),
                        "yturl": target,
                    })
                    
        return available_fmt, target

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        target = target.split("&")[0] if "&" in target else target
        
        res = (await VideosSearch(target, limit=10).next()).get("result")[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

    async def download(self, link: str, mystic, video: Union[bool, str] = None, videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None, songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None, title: Union[bool, str] = None):
        target = self.base_yt + link if videoid else link
        try:
            dl_file = await fetch_media(target, "video" if video else "audio")
            return (dl_file, True) if dl_file else (None, False)
        except Exception:
            return None, False