from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.utils.database import set_cmode
from MattoMusic.utils.decorators.admins import AdminActual
from config import BANNED_USERS

@app.on_message(filters.command(["channelplay"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def handle_channel_play(client, message: Message, _):
    if len(message.command) < 2:
        return await message.reply_text(_["cplay_1"].format(message.chat.title))
        
    cmd_query = message.text.split(None, 2)[1].lower().strip()
    
    if cmd_query == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text(_["cplay_7"])
        
    elif cmd_query == "linked":
        current_chat = await app.get_chat(message.chat.id)
        if current_chat.linked_chat:
            linked_id = current_chat.linked_chat.id
            await set_cmode(message.chat.id, linked_id)
            return await message.reply_text(_["cplay_3"].format(current_chat.linked_chat.title, linked_id))
        else:
            return await message.reply_text(_["cplay_2"])
            
    else:
        try:
            target_chat = await app.get_chat(cmd_query)
        except Exception:
            return await message.reply_text(_["cplay_4"])
            
        if target_chat.type != ChatType.CHANNEL:
            return await message.reply_text(_["cplay_5"])
            
        owner_username = None
        owner_id = None
        try:
            async for member in app.get_chat_members(target_chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if member.status == ChatMemberStatus.OWNER:
                    owner_username = member.user.username
                    owner_id = member.user.id
        except Exception:
            return await message.reply_text(_["cplay_4"])
            
        if owner_id != message.from_user.id:
            return await message.reply_text(_["cplay_6"].format(target_chat.title, owner_username))
            
        await set_cmode(message.chat.id, target_chat.id)
        return await message.reply_text(_["cplay_3"].format(target_chat.title, target_chat.id))