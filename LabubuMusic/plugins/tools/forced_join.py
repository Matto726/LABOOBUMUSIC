import asyncio
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import CallbackQuery, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from config import MONGO_DB_URI

fsub_client = MongoClient(MONGO_DB_URI)
forced_join_db = fsub_client.status_db.status

@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def enable_forced_join(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        member_info = await client.get_chat_member(chat_id, user_id)
        if member_info.status not in ["administrator", "creator"] and user_id not in SUDOERS:
            return await message.reply_text("🚫 **ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!**")
            
        if len(message.command) < 2:
            return await message.reply_text("⚠️ **ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ!**")
            
        target_channel = message.command[1]
        
        try:
            channel_info = await client.get_chat(target_channel)
            channel_id = channel_info.id
            channel_username = channel_info.username
        except Exception:
            return await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ᴏʀ ɪ ᴀᴍ ɴᴏᴛ ᴀᴅᴅᴇᴅ ᴛʜᴇʀᴇ.**")
            
        forced_join_db.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True
        )
        await message.reply_text(f"✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ {channel_info.title}!**")
        
    except Exception as err:
        await message.reply_text(f"❌ **ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:** {err}")

@app.on_message(filters.group, group=30)
async def monitor_fsub_compliance(client: Client, message: Message):
    if not message.from_user:
        return
        
    chat_id = message.chat.id
    db_record = forced_join_db.find_one({"chat_id": chat_id})
    
    if not db_record:
        return
        
    channel_id = db_record.get("channel_id")
    channel_username = db_record.get("channel_username")
    
    try:
        await client.get_chat_member(channel_id, message.from_user.id)
    except UserNotParticipant:
        inv_url = f"https://t.me/{channel_username}" if channel_username else await app.export_chat_invite_link(channel_id)
            
        try:
            await message.delete()
        except Exception:
            pass
            
        warn_msg = await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=f"**👋 ʜᴇʟʟᴏ {message.from_user.mention},**\n\n**ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({inv_url}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=inv_url)]]),
        )
        await asyncio.sleep(60)
        try:
            await warn_msg.delete()
        except Exception:
            pass
    except ChatAdminRequired:
        forced_join_db.delete_one({"chat_id": chat_id})
        await message.reply_text("**🚫 I'ᴍ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ғᴏʀᴄᴇᴅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ. ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**")