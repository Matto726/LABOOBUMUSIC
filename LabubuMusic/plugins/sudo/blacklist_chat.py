from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import blacklist_chat, blacklisted_chats, whitelist_chat
from MattoMusic.utils.decorators.language import language
from config import BANNED_USERS

@app.on_message(filters.command(["blchat", "blacklistchat"]) & SUDOERS)
@language
async def block_chat(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_1"])
        
    target_chat = int(message.text.strip().split()[1])
    if target_chat in await blacklisted_chats():
        return await message.reply_text(_["black_2"])
        
    is_blacklisted = await blacklist_chat(target_chat)
    if is_blacklisted:
        await message.reply_text(_["black_3"])
    else:
        await message.reply_text(_["black_9"])
        
    try: await app.leave_chat(target_chat)
    except Exception: pass

@app.on_message(filters.command(["whitelistchat", "unblacklistchat", "unblchat"]) & SUDOERS)
@language
async def unblock_chat(client, message: Message, _):
    if len(message.command) != 2:
        return await message.reply_text(_["black_4"])
        
    target_chat = int(message.text.strip().split()[1])
    if target_chat not in await blacklisted_chats():
        return await message.reply_text(_["black_5"])
        
    is_whitelisted = await whitelist_chat(target_chat)
    if is_whitelisted:
        return await message.reply_text(_["black_6"])
    await message.reply_text(_["black_9"])

@app.on_message(filters.command(["blchats", "blacklistedchats"]) & ~BANNED_USERS)
@language
async def list_blocked_chats(client, message: Message, _):
    display_text = _["black_7"]
    tracker = 0
    
    for idx, c_id in enumerate(await blacklisted_chats(), 1):
        try: c_title = (await app.get_chat(c_id)).title
        except Exception: c_title = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        
        tracker = 1
        display_text += f"{idx}. {c_title}[<code>{c_id}</code>]\n"
        
    if tracker == 0:
        await message.reply_text(_["black_8"].format(app.mention))
    else:
        await message.reply_text(display_text)