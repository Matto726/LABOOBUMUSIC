import asyncio
import os
import time
from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from MattoMusic import app
from MattoMusic.utils.formatters import (
    check_duration,
    convert_bytes,
    get_readable_time,
    seconds_to_min,
)

class TelegramCoreAPI:
    def __init__(self):
        self.max_chars = 4096
        self.delay = 5

    async def send_split_text(self, message, text_content):
        chunks = [text_content[i : i + self.max_chars] for i in range(0, len(text_content), self.max_chars)]
        
        for index, chunk in enumerate(chunks):
            if index <= 2:
                await message.reply_text(chunk, disable_web_page_preview=True)
        return True

    async def get_link(self, message):
        return message.link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            f_name = file.file_name
            if not f_name:
                f_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        except Exception:
            f_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        return f_name

    async def get_duration(self, file, file_path=None):
        try:
            return seconds_to_min(file.duration)
        except Exception:
            if file_path:
                try:
                    dur_seconds = await asyncio.get_event_loop().run_in_executor(None, check_duration, file_path)
                    return seconds_to_min(dur_seconds)
                except Exception:
                    pass
            return "Unknown"

    async def get_filepath(self, audio: Union[bool, str] = None, video: Union[bool, str] = None):
        f_name = ""
        if audio:
            try:
                ext = audio.file_name.split(".")[-1] if not isinstance(audio, Voice) else "ogg"
                f_name = f"{audio.file_unique_id}.{ext}"
            except Exception:
                f_name = f"{audio.file_unique_id}.ogg"
                
        if video:
            try:
                ext = video.file_name.split(".")[-1]
                f_name = f"{video.file_unique_id}.{ext}"
            except Exception:
                f_name = f"{video.file_unique_id}.mp4"
                
        return os.path.join(os.path.realpath("downloads"), f_name)

    async def download(self, string_data, message, mystic_msg, file_path):
        low_thresholds = [0, 8, 17, 38, 64, 77, 96]
        high_thresholds = [5, 10, 20, 40, 66, 80, 99]
        trackers = [5, 10, 20, 40, 66, 80, 99]
        speed_tracker = {}
        
        if os.path.exists(file_path):
            return True

        async def execute_download():
            async def report_progress(current_bytes, total_bytes):
                if current_bytes == total_bytes:
                    return
                    
                elapsed_time = time.time() - speed_tracker.get(message.id, time.time())
                cancel_btn = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="stop_downloading")]])
                
                pct_raw = (current_bytes * 100) / total_bytes
                pct_str = str(round(pct_raw, 2))
                
                speed = current_bytes / elapsed_time if elapsed_time > 0 else 0
                eta_secs = int((total_bytes - current_bytes) / speed) if speed > 0 else 0
                eta_str = get_readable_time(eta_secs) or "0 sᴇᴄᴏɴᴅs"
                
                fmt_total = convert_bytes(total_bytes)
                fmt_current = convert_bytes(current_bytes)
                fmt_speed = convert_bytes(speed)
                pct_int = int((pct_str.split("."))[0])
                
                for i in range(7):
                    if int(low_thresholds[i]) < pct_int <= int(high_thresholds[i]):
                        if int(high_thresholds[i]) == trackers[i]:
                            try:
                                await mystic_msg.edit_text(
                                    text=string_data["tg_1"].format(
                                        app.mention, fmt_total, fmt_current, pct_str[:5], fmt_speed, eta_str
                                    ),
                                    reply_markup=cancel_btn,
                                )
                                trackers[i] = 100
                            except Exception:
                                pass

            speed_tracker[message.id] = time.time()
            try:
                await app.download_media(message.reply_to_message, file_name=file_path, progress=report_progress)
                time_taken = get_readable_time(int(time.time() - speed_tracker[message.id])) or "0 sᴇᴄᴏɴᴅs"
                await mystic_msg.edit_text(string_data["tg_2"].format(time_taken))
            except Exception:
                await mystic_msg.edit_text(string_data["tg_3"])

        dl_task = asyncio.create_task(execute_download())
        config.lyrical[mystic_msg.id] = dl_task
        await dl_task
        
        if not config.lyrical.get(mystic_msg.id):
            return False
        config.lyrical.pop(mystic_msg.id)
        return True