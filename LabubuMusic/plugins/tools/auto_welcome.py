import asyncio
import time
from logging import getLogger
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated

from MattoMusic import app
from MattoMusic.core.db_setup import mongodb
from MattoMusic.utils.database import get_assistant
from config import OWNER_ID

LOGGER = getLogger(__name__)

welcome_db_collection = mongodb.awelcome

class AutoWelcomeDB:
    @staticmethod
    async def fetch_status(chat_id):
        record = await welcome_db_collection.find_one({"chat_id": chat_id})
        if not record:
            return True
        return record.get("state") == "off"

    @staticmethod
    async def disable_welcome(chat_id):
        await welcome_db_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"state": "off"}},
            upsert=True,
        )

    @staticmethod
    async def enable_welcome(chat_id):
        await welcome_db_collection.delete_one({"chat_id": chat_id})

welcome_manager = AutoWelcomeDB()

user_spam_tracker = {}
command_frequency = {}
MAX_REQUESTS = 2
SPAM_INTERVAL = 5

@app.on_message(filters.command("awelcome") & ~filters.private)
async def toggle_auto_welcome(client, message):
    req_user = message.from_user.id
    now = time.time()
    last_req = user_spam_tracker.get(req_user, 0)

    if now - last_req < SPAM_INTERVAL:
        user_spam_tracker[req_user] = now
        command_frequency[req_user] = command_frequency.get(req_user, 0) + 1
        if command_frequency[req_user] > MAX_REQUESTS:
            warning_msg = await message.reply_text(
                f"{message.from_user.mention} ᴘʟᴇᴀsᴇ ᴅᴏɴᴛ ᴅᴏ sᴘᴀᴍ, ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 5 sᴇᴄ"
            )
            await asyncio.sleep(3)
            await warning_msg.delete()
            return
    else:
        command_frequency[req_user] = 1
        user_spam_tracker[req_user] = now

    cmd_usage = "ᴜsᴀɢᴇ:\n⦿ /awelcome [on|off]"
    if len(message.command) == 1:
        return await message.reply_text(cmd_usage)

    target_chat = message.chat.id
    member_info = await app.get_chat_member(target_chat, message.from_user.id)
    
    if member_info.status in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        action = message.text.split(None, 1)[1].strip().lower()
        is_disabled = await welcome_manager.fetch_status(target_chat)

        if action == "on":
            if not is_disabled:
                await message.reply_text("ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ !")
            else:
                await welcome_manager.enable_welcome(target_chat)
                await message.reply_text(f"ᴇɴᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}")
        elif action == "off":
            if is_disabled:
                await message.reply_text("ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ !")
            else:
                await welcome_manager.disable_welcome(target_chat)
                await message.reply_text(f"ᴅɪsᴀʙʟᴇᴅ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ {message.chat.title}")
        else:
            await message.reply_text(cmd_usage)
    else:
        await message.reply("sᴏʀʀʏ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴀʙʟᴇ ᴀssɪsᴛᴀɴᴛ ᴡᴇʟᴄᴏᴍᴇ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ!")

@app.on_chat_member_updated(filters.group, group=5)
async def welcome_new_members(client, member: ChatMemberUpdated):
    try:
        target_chat = member.chat.id
        chat_title = (await app.get_chat(target_chat)).title
        ass_bot = await get_assistant(target_chat)
        member_count = await app.get_chat_members_count(target_chat)
        
        if await welcome_manager.fetch_status(target_chat):
            return

        joined_user = member.new_chat_member.user if member.new_chat_member else member.from_user

        if member.new_chat_member and not member.old_chat_member:
            if joined_user.id in [OWNER_ID, 7574330905]:
                boss_msg = f"""🌟 <b>𝐓ʜᴇ ᴏᴡɴᴇʀ ʜᴀs ᴀʀʀɪᴠᴇᴅ</b> 🌟\n\n🔥 <b>ʙᴏss</b> {joined_user.mention} <b>ʜᴀs ᴊᴏɪɴᴇᴅ!</b> 🔥\n👑 <b>ᴏᴡɴᴇʀ ɪᴅ:</b> {joined_user.id} ✨\n🎯 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{joined_user.username} 🚀\n👥 <b>ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs:</b> {member_count} 📈\n🏰 <b>ɢʀᴏᴜᴘ:</b> {chat_title} \n\n<b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜɪs ᴋɪɴɢᴅᴏᴍ, ʙᴏss ! 👑✨</b>"""
                await asyncio.sleep(3)
                await ass_bot.send_message(target_chat, text=boss_msg)
            else:
                standard_msg = f"""⛳️ <b>𝐖ᴇʟᴄᴏᴍᴇ 𝐓ᴏ 𝐎ᴜʀ 𝐆ʀᴏᴜᴘ</b> ⛳️\n\n➤ <b>𝐍ᴀᴍᴇ 🖤 ◂⚚▸</b> {joined_user.mention} 💤 ❤️\n➤ <b>𝐔ꜱᴇʀ 𝐈ᴅ 🖤 ◂⚚▸</b> {joined_user.id} ❤️🧿\n➤ <b>𝐔ꜱᴇʀɴᴀᴍᴇ 🖤 ◂⚚▸</b> @{joined_user.username} ❤️🌎\n➤ <b>𝐌ᴇᴍʙᴇʀs 🖤 ◂⚚▸</b> {member_count} ❤️🍂"""
                await asyncio.sleep(3)
                await ass_bot.send_message(target_chat, text=standard_msg)
    except Exception:
        return