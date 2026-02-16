import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils import get_readable_time
from MattoMusic.utils.database import (
    add_banned_user, get_banned_count, get_banned_users,
    get_served_chats, is_banned_user, remove_banned_user,
)
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.extraction import extract_user
from config import BANNED_USERS

@app.on_message(filters.command(["gban", "globalban"]) & SUDOERS)
@language
async def gban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    if target_user.id == message.from_user.id: return await message.reply_text(_["gban_1"])
    elif target_user.id == app.id: return await message.reply_text(_["gban_2"])
    elif target_user.id in SUDOERS: return await message.reply_text(_["gban_3"])
    
    if await is_banned_user(target_user.id):
        return await message.reply_text(_["gban_4"].format(target_user.mention))
        
    if target_user.id not in BANNED_USERS: BANNED_USERS.add(target_user.id)
    
    active_chats = [int(ch["chat_id"]) for ch in await get_served_chats()]
    eta_time = get_readable_time(len(active_chats))
    
    loading_msg = await message.reply_text(_["gban_5"].format(target_user.mention, eta_time))
    chat_bans = 0
    
    for c_id in active_chats:
        try:
            await app.ban_chat_member(c_id, target_user.id)
            chat_bans += 1
        except FloodWait as err: await asyncio.sleep(int(err.value))
        except Exception: continue
            
    await add_banned_user(target_user.id)
    await message.reply_text(
        _["gban_6"].format(app.mention, message.chat.title, message.chat.id, target_user.mention, target_user.id, message.from_user.mention, chat_bans)
    )
    await loading_msg.delete()

@app.on_message(filters.command(["ungban"]) & SUDOERS)
@language
async def ungban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    if not await is_banned_user(target_user.id):
        return await message.reply_text(_["gban_7"].format(target_user.mention))
        
    if target_user.id in BANNED_USERS: BANNED_USERS.remove(target_user.id)
    
    active_chats = [int(ch["chat_id"]) for ch in await get_served_chats()]
    eta_time = get_readable_time(len(active_chats))
    
    loading_msg = await message.reply_text(_["gban_8"].format(target_user.mention, eta_time))
    chat_unbans = 0
    
    for c_id in active_chats:
        try:
            await app.unban_chat_member(c_id, target_user.id)
            chat_unbans += 1
        except FloodWait as err: await asyncio.sleep(int(err.value))
        except Exception: continue
            
    await remove_banned_user(target_user.id)
    await message.reply_text(_["gban_9"].format(target_user.mention, chat_unbans))
    await loading_msg.delete()

@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & SUDOERS)
@language
async def list_gbanned_users(client, message: Message, _):
    if await get_banned_count() == 0:
        return await message.reply_text(_["gban_10"])
        
    loading_msg = await message.reply_text(_["gban_11"])
    display_text = _["gban_12"]
    tracker = 0
    
    for u_id in await get_banned_users():
        tracker += 1
        try:
            u_data = await app.get_users(u_id)
            u_mention = u_data.first_name if not u_data.mention else u_data.mention
            display_text += f"{tracker}➤ {u_mention}\n"
        except Exception:
            display_text += f"{tracker}➤ {u_id}\n"
            continue
            
    if tracker == 0: return await loading_msg.edit_text(_["gban_10"])
    else: return await loading_msg.edit_text(display_text)