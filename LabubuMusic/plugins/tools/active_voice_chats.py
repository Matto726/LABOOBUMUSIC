from pyrogram import filters
from pyrogram.types import Message
from unidecode import unidecode

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import (
    get_active_chats,
    get_active_video_chats,
    remove_active_chat,
    remove_active_video_chat,
)

@app.on_message(filters.command(["activevc", "activevoice"]) & SUDOERS)
async def list_active_vc(client, message: Message):
    status_msg = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ʟɪsᴛ...")
    active_sessions = await get_active_chats()
    display_text = ""
    counter = 0
    
    for chat_id in active_sessions:
        try:
            chat_title = (await app.get_chat(chat_id)).title
        except Exception:
            await remove_active_chat(chat_id)
            continue
            
        try:
            chat_data = await app.get_chat(chat_id)
            clean_title = unidecode(chat_title).upper()
            if chat_data.username:
                display_text += f"<b>{counter + 1}.</b> <a href=https://t.me/{chat_data.username}>{clean_title}</a> [<code>{chat_id}</code>]\n"
            else:
                display_text += f"<b>{counter + 1}.</b> {clean_title} [<code>{chat_id}</code>]\n"
            counter += 1
        except Exception:
            continue
            
    if not display_text:
        await status_msg.edit_text(f"» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs ᴏɴ {app.mention}.")
    else:
        await status_msg.edit_text(
            f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛs :</b>\n\n{display_text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command(["activev", "activevideo"]) & SUDOERS)
async def list_active_video(client, message: Message):
    status_msg = await message.reply_text("» ɢᴇᴛᴛɪɴɢ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs ʟɪsᴛ...")
    active_vid_sessions = await get_active_video_chats()
    display_text = ""
    counter = 0
    
    for chat_id in active_vid_sessions:
        try:
            chat_title = (await app.get_chat(chat_id)).title
        except Exception:
            await remove_active_video_chat(chat_id)
            continue
            
        try:
            chat_data = await app.get_chat(chat_id)
            clean_title = unidecode(chat_title).upper()
            if chat_data.username:
                display_text += f"<b>{counter + 1}.</b> <a href=https://t.me/{chat_data.username}>{clean_title}</a> [<code>{chat_id}</code>]\n"
            else:
                display_text += f"<b>{counter + 1}.</b> {clean_title} [<code>{chat_id}</code>]\n"
            counter += 1
        except Exception:
            continue
            
    if not display_text:
        await status_msg.edit_text(f"» ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs ᴏɴ {app.mention}.")
    else:
        await status_msg.edit_text(
            f"<b>» ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ ᴠɪᴅᴇᴏ ᴄʜᴀᴛs :</b>\n\n{display_text}",
            disable_web_page_preview=True,
        )