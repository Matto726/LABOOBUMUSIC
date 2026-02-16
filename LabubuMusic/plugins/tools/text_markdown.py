from pyrogram.enums import ChatType, ParseMode
from pyrogram.filters import command
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from MattoMusic import app
from MattoMusic.utils.functions import MARKDOWN

@app.on_message(command("markdownhelp"))
async def show_markdown_guide(client, message: Message):
    btn_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Cʟɪᴄᴋ Hᴇʀᴇ ᴛᴏ ᴠɪᴇᴡ", url=f"http://t.me/{app.username}?start=mkdwn_help")]]
    )
    
    if message.chat.type != ChatType.PRIVATE:
        await message.reply("📝 **Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴍᴀʀᴋᴅᴏᴡɴ ᴜsᴀɢᴇ sʏɴᴛᴀx ɪɴ ʏᴏᴜʀ ᴘʀɪᴠᴀᴛᴇ ᴍᴇssᴀɢᴇs!**", reply_markup=btn_markup)
    else:
        await message.reply(MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True)