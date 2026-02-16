import asyncio
import logging
from datetime import datetime
from pyrogram.enums import ChatType
from pytgcalls.exceptions import GroupCallNotFound

import config
from MattoMusic import app
from MattoMusic.misc import db
from MattoMusic.core.stream_call import Samar, autoend, counter
from MattoMusic.utils.database import get_client, set_loop, is_active_chat, is_autoend, is_autoleave

async def auto_exit_chats():
    while True:
        await asyncio.sleep(43200)
        from MattoMusic.core.assistant_bot import assistants
        
        is_leave_enabled = await is_autoleave()
        if not is_leave_enabled:
            continue
            
        for session_num in assistants:
            ass_client = await get_client(session_num)
            left_count = 0
            
            try:
                async for dialog in ass_client.get_dialogs():
                    if dialog.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                        allowed_exemptions = [
                            config.LOG_GROUP_ID,
                            -1002169072536,
                            -1002499911479,
                            -1002252855734
                        ]
                        
                        if dialog.chat.id not in allowed_exemptions:
                            if left_count >= 20:
                                continue
                                
                            if not await is_active_chat(dialog.chat.id):
                                try:
                                    await ass_client.leave_chat(dialog.chat.id)
                                    left_count += 1
                                except Exception as err:
                                    logging.error(f"Cannot leave chat {dialog.chat.id}: {err}")
                                    continue
            except Exception as err:
                logging.error(f"Dialog processing error: {err}")

asyncio.create_task(auto_exit_chats())

async def auto_stop_stream():
    global autoend, counter
    
    while True:
        await asyncio.sleep(60)
        
        try:
            is_end_enabled = await is_autoend()
            if not is_end_enabled:
                continue
                
            active_autoends = autoend.copy()
            expired_sessions = []
            no_call_active = False
            
            for c_id in active_autoends:
                try:
                    listener_count = len(await Samar.call_listeners(c_id))
                except GroupCallNotFound:
                    listener_count = 1
                    no_call_active = True
                except Exception:
                    listener_count = 100
                    
                if listener_count == 1:
                    await set_loop(c_id, 0)
                    expired_sessions.append(c_id)
                    
                    try:
                        await db[c_id][0]["mystic"].delete()
                    except Exception:
                        pass
                        
                    try:
                        await Samar.stop_stream(c_id)
                    except Exception:
                        pass
                        
                    try:
                        if not no_call_active:
                            await app.send_message(
                                c_id, 
                                "» ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
                            )
                    except Exception:
                        pass
                        
            for c_id in expired_sessions:
                if c_id in autoend:
                    del autoend[c_id]
                
        except Exception as err:
            logging.info(f"Autoend Error: {err}")

asyncio.create_task(auto_stop_stream())