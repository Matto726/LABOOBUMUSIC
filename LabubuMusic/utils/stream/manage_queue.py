import asyncio
from typing import Union

from MattoMusic.misc import db
from MattoMusic.utils.formatters import check_duration, seconds_to_min
from config import autoclean, time_to_seconds

async def add_to_queue(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    user_id,
    stream,
    forceplay: Union[bool, str] = None,
):
    formatted_title = title.title()
    try:
        dur_secs = time_to_seconds(duration) - 3
    except Exception:
        dur_secs = 0
        
    queue_item = {
        "title": formatted_title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "user_id": user_id,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": dur_secs,
        "played": 0,
    }
    
    if forceplay:
        existing_q = db.get(chat_id)
        if existing_q:
            existing_q.insert(0, queue_item)
        else:
            db[chat_id] = [queue_item]
    else:
        db.setdefault(chat_id, []).append(queue_item)
        
    autoclean.append(file)


async def add_to_queue_index(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    stream,
    forceplay: Union[bool, str] = None,
):
    if "20.212.146.162" in vidid:
        try:
            dur_secs = await asyncio.get_event_loop().run_in_executor(None, check_duration, vidid)
            duration = seconds_to_min(dur_secs)
        except Exception:
            duration = "ᴜʀʟ sᴛʀᴇᴀᴍ"
            dur_secs = 0
    else:
        dur_secs = 0
        
    queue_item = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": dur_secs,
        "played": 0,
    }
    
    if forceplay:
        existing_q = db.get(chat_id)
        if existing_q:
            existing_q.insert(0, queue_item)
        else:
            db[chat_id] = [queue_item]
    else:
        db.setdefault(chat_id, []).append(queue_item)
        
    autoclean.append(file)