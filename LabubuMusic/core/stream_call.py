import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError,
)
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, MediumQualityVideo
from pytgcalls.types.stream import StreamAudioEnded

import config
from MattoMusic import LOGGER, YouTube, app
from MattoMusic.misc import db
from MattoMusic.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from MattoMusic.utils.exceptions import AssistantErr
from MattoMusic.utils.formatters import check_duration, seconds_to_min, speed_converter
from MattoMusic.utils.inline.play import stream_markup
from MattoMusic.utils.stream.autoclear import auto_clean
from MattoMusic.utils.thumbnails import gen_thumb
from strings import get_string

autoend = {}
counter = {}

async def clear_chat_data(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class VoiceStreamManager(PyTgCalls):
    def __init__(self):
        self.userbot1 = Client(name="SamarAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1))
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        
        self.userbot2 = Client(name="SamarAss2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2))
        self.two = PyTgCalls(self.userbot2, cache_duration=100)
        
        self.userbot3 = Client(name="SamarAss3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3))
        self.three = PyTgCalls(self.userbot3, cache_duration=100)
        
        self.userbot4 = Client(name="SamarAss4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4))
        self.four = PyTgCalls(self.userbot4, cache_duration=100)
        
        self.userbot5 = Client(name="SamarAss5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5))
        self.five = PyTgCalls(self.userbot5, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        ass_client = await group_assistant(self, chat_id)
        await ass_client.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        ass_client = await group_assistant(self, chat_id)
        await ass_client.resume_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        ass_client = await group_assistant(self, chat_id)
        try:
            await clear_chat_data(chat_id)
            await ass_client.leave_group_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        for idx, session in enumerate([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
            if session:
                try:
                    client = getattr(self, ["one", "two", "three", "four", "five"][idx])
                    await client.leave_group_call(chat_id)
                except:
                    pass
        try:
            await clear_chat_data(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        ass_client = await group_assistant(self, chat_id)
        if str(speed) == "1.0":
            out_file = file_path
        else:
            base_name = os.path.basename(file_path)
            chat_folder = os.path.join(os.getcwd(), "playback", str(speed))
            os.makedirs(chat_folder, exist_ok=True)
            out_file = os.path.join(chat_folder, base_name)
            
            if not os.path.isfile(out_file):
                vs_mapping = {"0.5": 2.0, "0.75": 1.35, "1.5": 0.68, "2.0": 0.5}
                vs = vs_mapping.get(str(speed), 1.0)
                
                cmd = f"ffmpeg -i {file_path} -filter:v setpts={vs}*PTS -filter:a atempo={speed} {out_file}"
                process = await asyncio.create_subprocess_shell(
                    cmd, stdin=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

        dur_seconds = int(await asyncio.get_event_loop().run_in_executor(None, check_duration, out_file))
        played_time, con_seconds = speed_converter(playing[0]["played"], speed)
        formatted_duration = seconds_to_min(dur_seconds)

        if playing[0]["streamtype"] == "video":
            stream = AudioVideoPiped(
                out_file, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(),
                additional_ffmpeg_parameters=f"-ss {played_time} -to {formatted_duration}"
            )
        else:
            stream = AudioPiped(
                out_file, audio_parameters=HighQualityAudio(),
                additional_ffmpeg_parameters=f"-ss {played_time} -to {formatted_duration}"
            )

        if str(db[chat_id][0]["file"]) != str(file_path):
            raise AssistantErr("Umm")
            
        await ass_client.change_stream(chat_id, stream)
        
        exists = (playing[0]).get("old_dur")
        if not exists:
            db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
            db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            
        db[chat_id][0]["played"] = con_seconds
        db[chat_id][0]["dur"] = formatted_duration
        db[chat_id][0]["seconds"] = dur_seconds
        db[chat_id][0]["speed_path"] = out_file
        db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        ass_client = await group_assistant(self, chat_id)
        try:
            db.get(chat_id).pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await ass_client.leave_group_call(chat_id)
        except:
            pass

    async def skip_stream(self, chat_id: int, link: str, video: Union[bool, str] = None, image: Union[bool, str] = None):
        ass_client = await group_assistant(self, chat_id)
        stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        await ass_client.change_stream(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        ass_client = await group_assistant(self, chat_id)
        stream = AudioVideoPiped(file_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}") if mode == "video" else AudioPiped(file_path, audio_parameters=HighQualityAudio(), additional_ffmpeg_parameters=f"-ss {to_seek} -to {duration}")
        await ass_client.change_stream(chat_id, stream)

    async def stream_call(self, link):
        ass_client = await group_assistant(self, config.LOG_GROUP_ID)
        await ass_client.join_group_call(config.LOG_GROUP_ID, AudioVideoPiped(link), stream_type=StreamType().pulse_stream)
        await asyncio.sleep(0.2)
        await ass_client.leave_group_call(config.LOG_GROUP_ID)

    async def join_call(self, chat_id: int, original_chat_id: int, link, video: Union[bool, str] = None, image: Union[bool, str] = None):
        ass_client = await group_assistant(self, chat_id)
        lang_data = await get_lang(chat_id)
        _ = get_string(lang_data)
        
        stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if video else AudioPiped(link, audio_parameters=HighQualityAudio())
        
        try:
            await ass_client.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except AlreadyJoinedError:
            raise AssistantErr(_["call_9"])
        except TelegramServerError:
            raise AssistantErr(_["call_10"])
            
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
            
        if await is_autoend():
            counter[chat_id] = {}
            user_count = len(await ass_client.get_participants(chat_id))
            if user_count == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        chat_db = db.get(chat_id)
        current_loop = await get_loop(chat_id)
        
        try:
            if not current_loop:
                popped_item = chat_db.pop(0)
            else:
                current_loop -= 1
                await set_loop(chat_id, current_loop)
                popped_item = None
                
            await auto_clean(popped_item)
            
            if not chat_db:
                await clear_chat_data(chat_id)
                return await client.leave_group_call(chat_id)
        except:
            try:
                await clear_chat_data(chat_id)
                return await client.leave_group_call(chat_id)
            except:
                return

        queued_file = chat_db[0]["file"]
        lang_data = await get_lang(chat_id)
        _ = get_string(lang_data)
        title = (chat_db[0]["title"]).title()
        user_by = chat_db[0]["by"]
        origin_chat_id = chat_db[0]["chat_id"]
        s_type = chat_db[0]["streamtype"]
        vid_id = chat_db[0]["vidid"]
        
        db[chat_id][0]["played"] = 0
        old_dur_exists = (chat_db[0]).get("old_dur")
        
        if old_dur_exists:
            db[chat_id][0]["dur"] = old_dur_exists
            db[chat_id][0]["seconds"] = chat_db[0]["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
            
        is_video = True if str(s_type) == "video" else False

        if "live_" in queued_file:
            n, link = await YouTube.video(vid_id, True)
            if n == 0:
                return await app.send_message(origin_chat_id, text=_["call_6"])
                
            stream = AudioVideoPiped(link, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if is_video else AudioPiped(link, audio_parameters=HighQualityAudio())
            
            try:
                await client.change_stream(chat_id, stream)
            except Exception:
                return await app.send_message(origin_chat_id, text=_["call_6"])
                
            img = await gen_thumb(vid_id)
            btn = stream_markup(_, chat_id)
            run_msg = await app.send_photo(
                chat_id=origin_chat_id, photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vid_id}", title[:23], chat_db[0]["dur"], user_by),
                reply_markup=InlineKeyboardMarkup(btn)
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"

        elif "vid_" in queued_file:
            temp_msg = await app.send_message(origin_chat_id, _["call_7"])
            try:
                f_path, direct = await YouTube.download(vid_id, temp_msg, videoid=True, video=is_video)
            except:
                return await temp_msg.edit_text(_["call_6"], disable_web_page_preview=True)
                
            stream = AudioVideoPiped(f_path, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if is_video else AudioPiped(f_path, audio_parameters=HighQualityAudio())
            
            try:
                await client.change_stream(chat_id, stream)
            except:
                return await app.send_message(origin_chat_id, text=_["call_6"])
                
            img = await gen_thumb(vid_id)
            btn = stream_markup(_, chat_id)
            await temp_msg.delete()
            run_msg = await app.send_photo(
                chat_id=origin_chat_id, photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vid_id}", title[:23], chat_db[0]["dur"], user_by),
                reply_markup=InlineKeyboardMarkup(btn)
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "stream"

        elif "index_" in queued_file:
            stream = AudioVideoPiped(vid_id, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if is_video else AudioPiped(vid_id, audio_parameters=HighQualityAudio())
            
            try:
                await client.change_stream(chat_id, stream)
            except:
                return await app.send_message(origin_chat_id, text=_["call_6"])
                
            btn = stream_markup(_, chat_id)
            run_msg = await app.send_photo(
                chat_id=origin_chat_id, photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user_by),
                reply_markup=InlineKeyboardMarkup(btn)
            )
            db[chat_id][0]["mystic"] = run_msg
            db[chat_id][0]["markup"] = "tg"
        else:
            stream = AudioVideoPiped(queued_file, audio_parameters=HighQualityAudio(), video_parameters=MediumQualityVideo()) if is_video else AudioPiped(queued_file, audio_parameters=HighQualityAudio())
            
            try:
                await client.change_stream(chat_id, stream)
            except:
                return await app.send_message(origin_chat_id, text=_["call_6"])
                
            if vid_id == "telegram":
                btn = stream_markup(_, chat_id)
                photo_url = config.TELEGRAM_AUDIO_URL if str(s_type) == "audio" else config.TELEGRAM_VIDEO_URL
                run_msg = await app.send_photo(
                    chat_id=origin_chat_id, photo=photo_url,
                    caption=_["stream_1"].format(config.SUPPORT_GROUP, title[:23], chat_db[0]["dur"], user_by),
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "tg"
            elif vid_id == "soundcloud":
                btn = stream_markup(_, chat_id)
                run_msg = await app.send_photo(
                    chat_id=origin_chat_id, photo=config.SOUNCLOUD_IMG_URL,
                    caption=_["stream_1"].format(config.SUPPORT_GROUP, title[:23], chat_db[0]["dur"], user_by),
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "tg"
            else:
                img = await gen_thumb(vid_id)
                btn = stream_markup(_, chat_id)
                run_msg = await app.send_photo(
                    chat_id=origin_chat_id, photo=img,
                    caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{vid_id}", title[:23], chat_db[0]["dur"], user_by),
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                db[chat_id][0]["mystic"] = run_msg
                db[chat_id][0]["markup"] = "stream"

    async def ping(self):
        ping_list = []
        if config.STRING1: ping_list.append(await self.one.ping)
        if config.STRING2: ping_list.append(await self.two.ping)
        if config.STRING3: ping_list.append(await self.three.ping)
        if config.STRING4: ping_list.append(await self.four.ping)
        if config.STRING5: ping_list.append(await self.five.ping)
        return str(round(sum(ping_list) / len(ping_list), 3))

    async def start(self):
        LOGGER(__name__).info("Initializing PyTgCalls Client...\n")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.two.on_kicked()
        @self.three.on_kicked()
        @self.four.on_kicked()
        @self.five.on_kicked()
        @self.one.on_closed_voice_chat()
        @self.two.on_closed_voice_chat()
        @self.three.on_closed_voice_chat()
        @self.four.on_closed_voice_chat()
        @self.five.on_closed_voice_chat()
        @self.one.on_left()
        @self.two.on_left()
        @self.three.on_left()
        @self.four.on_left()
        @self.five.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        @self.two.on_stream_end()
        @self.three.on_stream_end()
        @self.four.on_stream_end()
        @self.five.on_stream_end()
        async def stream_end_handler1(client, update: Update):
            if isinstance(update, StreamAudioEnded):
                await self.change_stream(client, update.chat_id)

Samar = VoiceStreamManager()