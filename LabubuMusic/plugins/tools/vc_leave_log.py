import asyncio
import random
from pyrogram import filters
from pyrogram.types import Message
from MattoMusic import app
from MattoMusic.utils.database import get_assistant

def format_small_caps(text: str) -> str:
    mapping = {
        "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ғ", "g": "ɢ",
        "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
        "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "s", "t": "ᴛ", "u": "ᴜ",
        "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ"
    }
    return "".join(mapping.get(char.lower(), char) for char in text)

async def remove_msg_delayed(msg: Message, delay_secs: int):
    try:
        await asyncio.sleep(delay_secs)
        await msg.delete()
    except Exception:
        pass

@app.on_message(filters.video_chat_members_invited)
async def monitor_vc_invites(client, message: Message):
    try:
        inviter = message.from_user
        invited_users = message.video_chat_members_invited.users
        inviter_name = inviter.first_name or "Someone"
        inviter_mention = f'<a href="tg://user?id={inviter.id}">{format_small_caps(inviter_name)}</a>'
        
        invited_mentions = ", ".join(
            [f'<a href="tg://user?id={u.id}">{format_small_caps(u.first_name or "User")}</a>' for u in invited_users]
        )
        
        invite_msg = (
            f"📨 {inviter_mention} <b>ᴊᴜsᴛ ɪɴᴠɪᴛᴇᴅ</b> {invited_mentions} <b>ᴛᴏ ᴛʜᴇ ᴠᴄ! ᴊᴏɪɴ ɪɴ ᴀɴᴅ ʜᴀᴠᴇ ғᴜɴ ɢᴜʏs! 🎈</b>"
        )
        
        dispatched_msg = await message.reply_text(invite_msg)
        asyncio.create_task(remove_msg_delayed(dispatched_msg, 10))
    except Exception:
        pass

@app.on_message(filters.video_chat_ended)
async def monitor_vc_ended(client, message: Message):
    try:
        chat_id = message.chat.id
        ass_client = await get_assistant(chat_id)
        bot_user = await ass_client.get_me()
        
        end_msgs = [
            f"🚫 <b>ᴛʜᴇ ᴠᴄ ʜᴀs ʙᴇᴇɴ ᴄʟᴏsᴇᴅ – ᴛʜᴀɴᴋs ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ ᴡʜᴏ ᴊᴏɪɴᴇᴅ! 🌟</b>",
            f"🛑 <b>ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ. ᴄᴀᴛᴄʜ ʏᴏᴜ ᴀʟʟ ɴᴇxᴛ ᴛɪᴍᴇ! 👋</b>",
        ]
        
        selected_msg = random.choice(end_msgs)
        dispatched_msg = await app.send_message(chat_id, selected_msg)
        asyncio.create_task(remove_msg_delayed(dispatched_msg, 15))
    except Exception:
        pass