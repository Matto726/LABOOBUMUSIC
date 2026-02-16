import asyncio
from MattoMusic.misc import db
from MattoMusic.utils.database import get_active_chats, is_music_playing

async def track_playback_progress():
    while True:
        await asyncio.sleep(1)
        active_sessions = await get_active_chats()
        
        for c_id in active_sessions:
            if not await is_music_playing(c_id):
                continue
                
            q_data = db.get(c_id)
            if not q_data:
                continue
                
            track_length = int(q_data[0]["seconds"])
            if track_length == 0:
                continue
                
            if db[c_id][0]["played"] >= track_length:
                continue
                
            db[c_id][0]["played"] += 1

asyncio.create_task(track_playback_progress())