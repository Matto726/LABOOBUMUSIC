from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import get_lang, is_maintenance, maintenance_off, maintenance_on
from strings import get_string

@app.on_message(filters.command(["maintenance"]) & SUDOERS)
async def toggle_maintenance(client, message: Message):
    try:
        lang_code = await get_lang(message.chat.id)
        _ = get_string(lang_code)
    except Exception:
        _ = get_string("en")
        
    usage_text = _["maint_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
        
    cmd_state = message.text.split(None, 1)[1].strip().lower()
    
    if cmd_state == "enable":
        if not await is_maintenance():
            await maintenance_on()
            await message.reply_text(_["maint_2"].format(app.mention))
        else:
            await message.reply_text(_["maint_4"])
    elif cmd_state == "disable":
        if await is_maintenance():
            await maintenance_off()
            await message.reply_text(_["maint_3"].format(app.mention))
        else:
            await message.reply_text(_["maint_5"])
    else:
        await message.reply_text(usage_text)