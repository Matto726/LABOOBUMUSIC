import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from MattoMusic import app
from MattoMusic.core.stream_call import Samar
from MattoMusic.misc import db
from MattoMusic.utils.database import get_assistant, get_authuser_names, get_cmode
from MattoMusic.utils.decorators import ActualAdminCB, language
from MattoMusic.utils.formatters import alpha_to_int
from config import BANNED_USERS, adminlist, lyrical

reload_tracker = {}

@app.on_message(filters.command(["admincache", "reload", "refresh"]) & filters.group & ~BANNED_USERS)
@language
async def refresh_admin_list(client, message: Message, _):
    chat_id = message.chat.id
    if chat_id not in reload_tracker:
        reload_tracker[chat_id] = True
    else:
        return await message.reply_text("⏳ **Aʟʀᴇᴀᴅʏ ʀᴇғʀᴇsʜɪɴɢ... ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ.**")

    try:
        adminlist[chat_id] = []
        async for member in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.privileges.can_manage_video_chats:
                adminlist[chat_id].append(member.user.id)
                
        auth_users = await get_authuser_names(chat_id)
        for auth_user in auth_users:
            u_id = await alpha_to_int(auth_user)
            adminlist[chat_id].append(u_id)
            
        await message.reply_text(_["admin_13"])
    except Exception as err:
        await message.reply_text(f"❌ **Eʀʀᴏʀ:** {err}")
    finally:
        reload_tracker.pop(chat_id, None)


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def dismiss_menu(client, query: CallbackQuery):
    try:
        await query.message.delete()
        notice = await query.message.reply_text(f"🗑️ Cʟᴏsᴇᴅ ʙʏ : {query.from_user.mention}")
        await asyncio.sleep(2)
        await notice.delete()
    except Exception:
        pass


@app.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def abort_active_download(client, query: CallbackQuery, _):
    msg_id = query.message.id
    dl_task = lyrical.get(msg_id)
    
    if not dl_task:
        return await query.answer(_["tg_4"], show_alert=True)
        
    if dl_task.done() or dl_task.cancelled():
        return await query.answer(_["tg_5"], show_alert=True)
        
    try:
        dl_task.cancel()
        lyrical.pop(msg_id, None)
        await query.answer(_["tg_6"], show_alert=True)
        await query.edit_message_text(_["tg_7"].format(query.from_user.mention))
    except Exception:
        await query.answer(_["tg_8"], show_alert=True)