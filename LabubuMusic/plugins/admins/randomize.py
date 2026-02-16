import random
from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import db
from MattoMusic.utils.decorators import AdminRightsCheck
from MattoMusic.utils.inline import close_markup
from config import BANNED_USERS

@app.on_message(filters.command(["shuffle", "cshuffle"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def shuffle_queue(client, message: Message, _, chat_id):
    queue_data = db.get(chat_id)
    if not queue_data:
        return await message.reply_text(_["queue_2"])
        
    try:
        current_track = queue_data.pop(0)
    except Exception:
        return await message.reply_text(_["admin_15"], reply_markup=close_markup(_))
        
    if not queue_data:
        queue_data.insert(0, current_track)
        return await message.reply_text(_["admin_15"], reply_markup=close_markup(_))
        
    random.shuffle(queue_data)
    queue_data.insert(0, current_track)
    
    await message.reply_text(
        _["admin_16"].format(message.from_user.mention), reply_markup=close_markup(_)
    )