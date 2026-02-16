import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import LOG_GROUP_ID
from MattoMusic import app
from MattoMusic.utils.database import add_served_chat, get_assistant, delete_served_chat

WELCOME_IMG = "https://files.catbox.moe/ajobub.jpg"
LEAVE_IMG_LIST = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]

@app.on_message(filters.new_chat_members, group=-10)
async def monitor_new_joins(client, message: Message):
    try:
        ass_client = await get_assistant(message.chat.id)
        current_chat = message.chat
        
        for member in message.new_chat_members:
            if member.id == app.id:
                member_count = await app.get_chat_members_count(current_chat.id)
                chat_username = current_chat.username or "Private Group"
                
                inv_link = ""
                try:
                    if not current_chat.username:
                        fetched_link = await app.export_chat_invite_link(current_chat.id)
                        inv_link = f"\nGroup Link: {fetched_link}" if fetched_link else ""
                except Exception:
                    pass
                
                log_text = (
                    f"Music Bot Added In A New Group\n\n"
                    f"Chat Name: {current_chat.title}\n"
                    f"Chat ID: {current_chat.id}\n"
                    f"Chat Username: @{chat_username}\n"
                    f"Group Members: {member_count}\n"
                    f"Added By: {message.from_user.mention}"
                    f"{inv_link}"
                )
                
                btn_markup = []
                if message.from_user.id:
                    btn_markup.append([InlineKeyboardButton("Added By", url=f"tg://openmessage?user_id={message.from_user.id}")])
                
                await app.send_photo(
                    LOG_GROUP_ID,
                    photo=WELCOME_IMG,
                    caption=log_text,
                    reply_markup=InlineKeyboardMarkup(btn_markup) if btn_markup else None
                )
                
                await add_served_chat(current_chat.id)
                if current_chat.username:
                    await ass_client.join_chat(f"@{current_chat.username}")

    except Exception as err:
        print(f"Join Watcher Error: {err}")


@app.on_message(filters.left_chat_member, group=-12)
async def monitor_leaves(client, message: Message):
    try:
        ass_client = await get_assistant(message.chat.id)
        left_member = message.left_chat_member
        
        if left_member and left_member.id == (await app.get_me()).id:
            kicked_by = message.from_user.mention if message.from_user else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
            c_title = message.chat.title
            c_id = message.chat.id
            
            leave_msg = (
                f"✫ <b><u>#𝐋ᴇғᴛ_𝐆ʀᴏᴜᴘ</u></b> ✫\n\n"
                f"𝐂ʜᴀᴛ 𝐓ɪᴛʟᴇ : {c_title}\n\n"
                f"𝐂ʜᴀᴛ 𝐈ᴅ : {c_id}\n\n"
                f"𝐑ᴇᴍᴏᴠᴇᴅ 𝐁ʏ : {kicked_by}\n\n"
                f"𝐁ᴏᴛ : @{app.username}"
            )
            
            await app.send_photo(LOG_GROUP_ID, photo=random.choice(LEAVE_IMG_LIST), caption=leave_msg)
            await delete_served_chat(c_id)
            await ass_client.leave_chat(c_id)
    except Exception:
        pass