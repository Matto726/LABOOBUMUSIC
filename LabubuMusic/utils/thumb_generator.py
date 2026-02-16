import os
import aiohttp
import aiofiles
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from py_yt import VideosSearch
from MattoMusic import app

CACHE_FOLDER = Path("cache")
CACHE_FOLDER.mkdir(exist_ok=True)

async def fetch_image(url: str, filepath: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f_data = await resp.read()
                async with aiofiles.open(filepath, mode="wb") as img_file:
                    await img_file.write(f_data)

def adjust_text(draw_obj, text_str, font_obj, max_w):
    words_list = text_str.split()
    compiled_lines = []
    curr_line = ""
    
    for w in words_list:
        test_line = f"{curr_line} {w}".strip()
        test_w = draw_obj.textlength(test_line, font=font_obj)
        if test_w <= max_w:
            curr_line = test_line
        else:
            compiled_lines.append(curr_line)
            curr_line = w
            
    if curr_line:
        compiled_lines.append(curr_line)
    return compiled_lines

async def gen_thumb(vid_id: str):
    cache_path = CACHE_FOLDER / f"{vid_id}.png"
    if cache_path.is_file():
        return str(cache_path)
        
    try:
        yt_search = VideosSearch(f"https://youtube.com/watch?v={vid_id}", limit=1)
        res_data = (await yt_search.next())["result"][0]
        
        t_title = res_data.get("title", "Unknown Title")
        t_duration = res_data.get("duration", "Unknown")
        t_channel = res_data.get("channel", {}).get("name", "Unknown Channel")
        t_views = res_data.get("viewCount", {}).get("short", "Unknown Views")
        t_thumb_url = res_data["thumbnails"][0]["url"].split("?")[0]
        
        raw_thumb_path = CACHE_FOLDER / f"raw_{vid_id}.png"
        await fetch_image(t_thumb_url, str(raw_thumb_path))
        
        background = Image.open(str(raw_thumb_path)).convert("RGBA")
        background = background.resize((1280, 720))
        
        draw = ImageDraw.Draw(background)
        
        try:
            font_title = ImageFont.truetype("MattoMusic/assets/font3.ttf", 60)
            font_meta = ImageFont.truetype("MattoMusic/assets/font2.ttf", 40)
        except Exception:
            font_title = ImageFont.load_default()
            font_meta = ImageFont.load_default()
            
        draw.rectangle([(0, 500), (1280, 720)], fill=(0, 0, 0, 180))
        
        title_lines = adjust_text(draw, t_title, font_title, 1200)
        y_pos = 520
        for line in title_lines[:1]: 
            draw.text((40, y_pos), line, fill="white", font=font_title)
            
        draw.text((40, 620), f"{t_channel}  |  {t_views}  |  {t_duration}", fill="lightgray", font=font_meta)
        
        background.save(str(cache_path))
        
        try:
            os.remove(str(raw_thumb_path))
        except Exception:
            pass
            
        return str(cache_path)
    except Exception as e:
        return "MattoMusic/assets/ShrutiBots.jpg"