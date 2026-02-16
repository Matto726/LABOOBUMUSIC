from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import add_gban_user, remove_gban_user
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.extraction import extract_user
from config import BANNED_USERS

@app.on_message(filters.command(["block"]) & SUDOERS)
@language
async def ban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    if target_user.id in BANNED_USERS:
        return await message.reply_text(_["block_1"].format(target_user.mention))
        
    await add_gban_user(target_user.id)
    BANNED_USERS.add(target_user.id)
    await message.reply_text(_["block_2"].format(target_user.mention))

@app.on_message(filters.command(["unblock"]) & SUDOERS)
@language
async def unban_user(client, message: Message, _):
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])
        
    target_user = await extract_user(message)
    if target_user.id not in BANNED_USERS:
        return await message.reply_text(_["block_3"].format(target_user.mention))
        
    await remove_gban_user(target_user.id)
    BANNED_USERS.remove(target_user.id)
    await message.reply_text(_["block_4"].format(target_user.mention))

@app.on_message(filters.command(["blocked", "blockedusers", "blusers"]) & SUDOERS)
@language
async def list_banned_users(client, message: Message, _):
    if not BANNED_USERS:
        return await message.reply_text(_["block_5"])
        
    loading_msg = await message.reply_text(_["block_6"])
    display_text = _["block_7"]
    tracker = 0
    
    for u_id in BANNED_USERS:
        try:
            u_data = await app.get_users(u_id)
            u_mention = u_data.first_name if not u_data.mention else u_data.mention
            tracker += 1
        except Exception: continue
        display_text += f"{tracker}➤ {u_mention}\n"
        
    if tracker == 0: return await loading_msg.edit_text(_["block_5"])
    else: return await loading_msg.edit_text(display_text)