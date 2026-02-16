from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from MattoMusic import app
from MattoMusic.utils.database import get_playmode, get_playtype, is_nonadmin_chat
from MattoMusic.utils.decorators import language
from MattoMusic.utils.inline.settings import playmode_users_markup
from config import BANNED_USERS

@app.on_message(filters.command(["playmode", "mode"]) & filters.group & ~BANNED_USERS)
@language
async def display_playmode_settings(client, message: Message, _):
    current_playmode = await get_playmode(message.chat.id)
    is_direct_mode = True if current_playmode == "Direct" else None
    
    is_regular_chat = await is_nonadmin_chat(message.chat.id)
    is_group_mode = True if not is_regular_chat else None
    
    current_playtype = await get_playtype(message.chat.id)
    is_everyone_allowed = None if current_playtype == "Everyone" else True
    
    btn_markup = playmode_users_markup(_, is_direct_mode, is_group_mode, is_everyone_allowed)
    
    await message.reply_text(
        _["play_22"].format(message.chat.title),
        reply_markup=InlineKeyboardMarkup(btn_markup),
    )