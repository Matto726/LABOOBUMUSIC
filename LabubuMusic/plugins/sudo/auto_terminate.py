from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import (
    autoend_off, autoend_on, autoleave_off, 
    autoleave_on, is_autoend, is_autoleave
)

@app.on_message(filters.command("autoend") & SUDOERS)
async def toggle_autoend(client, message: Message):
    current_state = await is_autoend()
    usage_text = f"<b>ᴇxᴀᴍᴘʟᴇ :</b>\n\n/autoend [ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ]\n\n Current state : {current_state}"
    
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
        
    cmd_state = message.text.split(None, 1)[1].strip().lower()
    
    if cmd_state in ["enable", "on", "yes"]:
        await autoend_on()
        await message.reply_text(
            "» ᴀᴜᴛᴏ ᴇɴᴅ sᴛʀᴇᴀᴍ ᴇɴᴀʙʟᴇᴅ.\n\nᴀssɪsᴛᴀɴᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇᴀᴠᴇ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴀғᴛᴇʀ ғᴇᴡ ᴍɪɴs ᴡʜᴇɴ ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ."
        )
    elif cmd_state in ["disable", "off", "no"]:
        await autoend_off()
        await message.reply_text("» ᴀᴜᴛᴏ ᴇɴᴅ sᴛʀᴇᴀᴍ ᴅɪsᴀʙʟᴇᴅ.")
    else:
        await message.reply_text(usage_text)

@app.on_message(filters.command("autoleave") & SUDOERS)
async def toggle_autoleave(client, message: Message):
    current_state = await is_autoleave()
    usage_text = f"<b>ᴇxᴀᴍᴘʟᴇ :</b>\n\n/autoleave [ᴇɴᴀʙʟᴇ | ᴅɪsᴀʙʟᴇ]\n\n Current state : {current_state}"
    
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
        
    cmd_state = message.text.split(None, 1)[1].strip().lower()
    
    if cmd_state in ["enable", "on", "yes"]:
        await autoleave_on()
        await message.reply_text(
            "» ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ ᴄʜᴀᴛ ᴇɴᴀʙʟᴇᴅ.\n\nᴀssɪsᴛᴀɴᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇᴀᴠᴇ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴀғᴛᴇʀ ғᴇᴡ ᴍɪɴs ᴡʜᴇɴ ɴᴏ ᴏɴᴇ ɪs ʟɪsᴛᴇɴɪɴɢ."
        )
    elif cmd_state in ["disable", "off", "no"]:
        await autoleave_off()
        await message.reply_text("» ᴀᴜᴛᴏ ʟᴇᴀᴠᴇ ᴄʜᴀᴛ ᴅɪsᴀʙʟᴇᴅ.")
    else:
        await message.reply_text(usage_text)