import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
import asyncio

from MattoMusic import app
from MattoMusic.misc import SUDOERS

@app.on_message(filters.command("leave") & SUDOERS)
async def force_leave_group(client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɢʀᴏᴜᴘ ɪᴅ. ᴜsᴇ ʟɪᴋᴇ: /leave chat_id.")
    try:
        target_chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ.")

    try:
        target_chat = await client.get_chat(target_chat_id)
        await client.leave_chat(target_chat_id)
        await message.reply_text(f"✅ sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ: **{target_chat.title}**")
    except Exception as e:
        await message.reply_text(f"❌ ғᴀɪʟᴇᴅ ᴛᴏ ʟᴇᴀᴠᴇ ᴛʜᴇ ɢʀᴏᴜᴘ.\n\n**ʀᴇᴀsᴏɴ:** {str(e)}")

@app.on_message(filters.command("link") & SUDOERS)
async def extract_group_link(client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ɢʀᴏᴜᴘ ɪᴅ. ᴜsᴇ ʟɪᴋᴇ: /link chat_id.")
        
    try:
        target_chat_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")

    try:
        target_chat = await client.get_chat(target_chat_id)
        gen_invite = target_chat.invite_link
        
        if not gen_invite:
            gen_invite = await client.export_chat_invite_link(target_chat_id)
            
        data_dump = {
            "ᴛɪᴛʟᴇ": target_chat.title,
            "ɪᴅ": target_chat.id,
            "ᴜsᴇʀɴᴀᴍᴇ": target_chat.username,
            "ᴍᴇᴍʙᴇʀs_ᴄᴏᴜɴᴛ": target_chat.members_count,
            "ᴅᴇsᴄʀɪᴘᴛɪᴏɴ": target_chat.description,
            "ɪɴᴠɪᴛᴇ_ʟɪɴᴋ": gen_invite,
        }

        output_doc = f"group_info_{target_chat.id}.txt"
        with open(output_doc, "w", encoding="utf-8") as dump_file:
            for k, v in data_dump.items():
                dump_file.write(f"{k}: {v}\n")

        await client.send_document(
            chat_id=message.chat.id,
            document=output_doc,
            caption=f"ʜᴇʀᴇ ɪs ᴛʜᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏʀ\n{target_chat.title}\n\nExᴛʀᴀᴄᴛᴇᴅ ʙʏ @{app.username}",
        )
        os.remove(output_doc)
    except Exception as err:
        await message.reply(f"❌ ᴇʀʀᴏʀ ᴇxᴛʀᴀᴄᴛɪɴɢ ʟɪɴᴋ: {str(err)}")