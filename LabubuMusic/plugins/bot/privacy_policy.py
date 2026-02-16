from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from MattoMusic import app
import config

PRIVACY_TEXT = f"""
🔒 **Privacy Policy for {app.mention} !**

Your privacy is important to us. To learn more about how we collect, use, and protect your data, please review our Privacy Policy here: [Privacy Policy]({config.PRIVACY_LINK}).

If you have any questions or concerns, feel free to reach out to our [support team](https://t.me/laboobusupportbot).
"""

@app.on_message(filters.command("privacy"))
async def display_privacy(client, message: Message):
    btn_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("View Privacy Policy", url=config.SUPPORT_GROUP)]]
    )
    
    await message.reply_text(
        PRIVACY_TEXT, 
        reply_markup=btn_markup, 
        parse_mode=ParseMode.MARKDOWN, 
        disable_web_page_preview=True
    )