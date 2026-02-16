from pyrogram import filters

from MattoMusic import app
from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import add_off, add_on
from MattoMusic.utils.decorators.language import language

@app.on_message(filters.command(["logger"]) & SUDOERS)
@language
async def toggle_logger(client, message, _):
    usage_text = _["log_1"]
    if len(message.command) != 2:
        return await message.reply_text(usage_text)
        
    cmd_state = message.text.split(None, 1)[1].strip().lower()
    
    if cmd_state == "enable":
        await add_on(2)
        await message.reply_text(_["log_2"])
    elif cmd_state == "disable":
        await add_off(2)
        await message.reply_text(_["log_3"])
    else:
        await message.reply_text(usage_text)

@app.on_message(filters.command(["cookies"]) & SUDOERS)
@language
async def fetch_cookies(client, message, _):
    await message.reply_document("cookies/logs.csv")
    await message.reply_text("Please check given file to cookies file choosing logs...")