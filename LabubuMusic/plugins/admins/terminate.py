from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.core.stream_call import Samar
from MattoMusic.utils.database import set_loop
from MattoMusic.utils.decorators import AdminRightsCheck
from MattoMusic.utils.inline import close_markup
from config import BANNED_USERS

@app.on_message(filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def terminate_playback(cli, message: Message, _, chat_id):
    if len(message.command) != 1:
        return
        
    await Samar.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention), reply_markup=close_markup(_)
    )