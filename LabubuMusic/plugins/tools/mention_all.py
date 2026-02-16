import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from MattoMusic import app

ACTIVE_TAG_SESSIONS = []
EMOJI_SETS = [
    "🦋🦋🦋🦋🦋", "🧚🌸🧋🍬🫖", "🥀🌷🌹🌺💐", "🌸🌿💮🌱🌵", "❤️💚💙💜🖤",
    "💓💕💞💗💖", "🌸💐🌺🌹🦋", "🍔🦪🍛🍲🥗", "🍎🍓🍒🍑🌶️", "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡", "🍨🧉🍺☕🍻", "🥪🥧🍦🍥🍚", "🫖☕🍹🍷🥛", "☕🧃🍩🍦🍙",
    "🍃🍂☘️🍀🍁", "💖💝🤎💜💙", "📱💻🖥️💻🖲️", "🐹🐔🐰🐭🐦", "🐍🐢🦎🐊🐙",
    "🐟🐠🐡🐬🦈", "🐛🦋🐌🐙🐞", "🐈🐕🐩🐕‍🦺🐈‍⬛", "🦆🦅🕊️🦢🦜", "☀️🌝🌞🌞☀️"
]

@app.on_message(filters.command(["tagall", "all", "mentionall", "mention"], prefixes=["/", "@"]) & filters.group)
async def tag_everyone(client, message):
    chat_id = message.chat.id
    requester = message.from_user.id
    
    member_status = await client.get_chat_member(chat_id, requester)
    if member_status.status not in ["administrator", "creator"]:
        return await message.reply_text("🚫 **Only admins can use this command!**")

    if chat_id in ACTIVE_TAG_SESSIONS:
        return await message.reply_text("⚠️ **A tagging process is already active in this group.**")

    ACTIVE_TAG_SESSIONS.append(chat_id)
    
    custom_msg = ""
    if message.reply_to_message:
        custom_msg = message.reply_to_message.text or message.reply_to_message.caption or ""
    elif len(message.command) > 1:
        custom_msg = message.text.split(None, 1)[1]

    members_cache = []
    async for member in client.get_chat_members(chat_id):
        if not member.user.is_bot and not member.user.is_deleted:
            members_cache.append(member.user)

    if not members_cache:
        ACTIVE_TAG_SESSIONS.remove(chat_id)
        return await message.reply_text("❌ **No valid users found to tag.**")

    batch_size = 5
    tagged_count = 0
    
    while members_cache and chat_id in ACTIVE_TAG_SESSIONS:
        batch = members_cache[:batch_size]
        members_cache = members_cache[batch_size:]
        
        tag_string = f"{custom_msg}\n\n" if custom_msg else ""
        current_emoji = random.choice(EMOJI_SETS)
        
        for i, user in enumerate(batch):
            emoji_char = current_emoji[i] if i < len(current_emoji) else "✨"
            tag_string += f"{emoji_char} [{user.first_name}](tg://user?id={user.id})\n"
            tagged_count += 1
            
        try:
            await client.send_message(chat_id, tag_string, disable_web_page_preview=True)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
        except Exception:
            continue

    if chat_id in ACTIVE_TAG_SESSIONS:
        ACTIVE_TAG_SESSIONS.remove(chat_id)
        await message.reply_text(f"✅ **Tagging complete! Successfully tagged {tagged_count} users.**")


@app.on_message(filters.command(["admintag", "adminmention", "admins"], prefixes=["/", "@"]) & filters.group)
async def tag_administrators(client, message):
    chat_id = message.chat.id
    requester = message.from_user.id
    
    status = await client.get_chat_member(chat_id, requester)
    if status.status not in ["administrator", "creator"]:
        return await message.reply_text("🚫 **Only admins can use this command!**")

    if chat_id in ACTIVE_TAG_SESSIONS:
        return await message.reply_text("⚠️ **A tagging process is already running.**")

    ACTIVE_TAG_SESSIONS.append(chat_id)
    
    custom_msg = ""
    if message.reply_to_message:
        custom_msg = message.reply_to_message.text or message.reply_to_message.caption or ""
    elif len(message.command) > 1:
        custom_msg = message.text.split(None, 1)[1]

    admins = []
    async for admin in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
        if not admin.user.is_bot and not admin.user.is_deleted:
            admins.append(admin.user)

    if not admins:
        ACTIVE_TAG_SESSIONS.remove(chat_id)
        return await message.reply_text("❌ **No human admins found.**")

    batch_size = 5
    tagged_count = 0
    
    while admins and chat_id in ACTIVE_TAG_SESSIONS:
        batch = admins[:batch_size]
        admins = admins[batch_size:]
        
        tag_string = f"{custom_msg}\n\n" if custom_msg else ""
        current_emoji = random.choice(EMOJI_SETS)
        
        for i, admin_user in enumerate(batch):
            emoji_char = current_emoji[i] if i < len(current_emoji) else "👑"
            tag_string += f"{emoji_char} [{admin_user.first_name}](tg://user?id={admin_user.id})\n"
            tagged_count += 1
            
        try:
            await client.send_message(chat_id, tag_string, disable_web_page_preview=True)
            await asyncio.sleep(2)
        except FloodWait as e:
            await asyncio.sleep(e.value + 1)
        except Exception:
            continue

    if chat_id in ACTIVE_TAG_SESSIONS:
        ACTIVE_TAG_SESSIONS.remove(chat_id)
        await message.reply_text(f"✅ **Tagging complete! Successfully tagged {tagged_count} admins.**")


@app.on_message(filters.command(["stopmention", "cancel", "offmention", "mentionoff", "cancelall"], prefixes=["/", "@"]) & filters.group)
async def abort_tagging(client, message):
    chat_id = message.chat.id
    requester = message.from_user.id
    
    status = await client.get_chat_member(chat_id, requester)
    if status.status not in ["administrator", "creator"]:
        return await message.reply_text("🚫 **Only admins can use this command.**")

    if chat_id in ACTIVE_TAG_SESSIONS:  
        try:  
            ACTIVE_TAG_SESSIONS.remove(chat_id)  
        except Exception:  
            pass  
        return await message.reply_text("🛑 **Tagging process successfully stopped!**")  
    else:  
        return await message.reply_text("⚠️ **No tagging process is currently running!**")

__MODULE__ = "Tᴀɢᴀʟʟ"
__HELP__ = """
/tagall or @tagall [text] or [reply] - Tag all users in your group with random emojis.
/admintag or @admintag [text] or [reply] - Tag all admins in your group.
/cancelall or @cancelall - Stop any running tagging process.
"""