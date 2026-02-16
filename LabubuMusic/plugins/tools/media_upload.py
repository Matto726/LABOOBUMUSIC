import os
import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from MattoMusic import app

def process_upload(file_loc):
    endpoint = "https://catbox.moe/user/api.php"
    payload = {"reqtype": "fileupload", "json": "true"}
    upload_file = {"fileToUpload": open(file_loc, "rb")}
    
    req_response = requests.post(endpoint, data=payload, files=upload_file)

    if req_response.status_code == 200:
        return True, req_response.text.strip()
    return False, f"Error: {req_response.status_code} - {req_response.text}"


@app.on_message(filters.command(["tgm", "tgt", "telegraph"]))
async def create_telegraph_link(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ, ᴠɪᴅᴇᴏ ᴏʀ ᴀɴɪᴍᴀᴛɪᴏɴ ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛ.")

    target_media = message.reply_to_message
    if not target_media.media:
        return await message.reply_text("❌ Iɴᴠᴀʟɪᴅ ᴍᴇᴅɪᴀ ғᴏʀᴍᴀᴛ.")

    status_loader = await message.reply_text("⏳ Uᴘʟᴏᴀᴅɪɴɢ ᴍᴇᴅɪᴀ ᴛᴏ sᴇʀᴠᴇʀ...")

    try:
        downloaded_path = await target_media.download()
        if not downloaded_path:
            return await status_loader.edit_text("❌ Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴍᴇᴅɪᴀ.")

        try:
            success, generated_url = process_upload(downloaded_path)
            if success:
                await status_loader.edit_text(
                    f"🌐 | <a href='{generated_url}'>👉 Yᴏᴜʀ Lɪɴᴋ Tᴀᴘ Hᴇʀᴇ 👈</a>",
                    disable_web_page_preview=False,
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🌍 Vɪᴇᴡ ɪɴ Bʀᴏᴡsᴇʀ", url=generated_url)]])
                )
            else:
                await status_loader.edit_text(f"⚠️ Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:\\n{generated_url}")

            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)

        except Exception as err:
            await status_loader.edit_text(f"❌ Fɪʟᴇ ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ\\n\\nRᴇᴀsᴏɴ: `{err}`")
            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)
    except Exception:
        pass

__HELP__ = """
**Mᴇᴅɪᴀ Uᴘʟᴏᴀᴅ ᴄᴏᴍᴍᴀɴᴅs:**
- `/tgm` | `/tgt` | `/telegraph`: Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇᴅɪᴀ ғɪʟᴇ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ.
"""
__MODULE__ = "Uᴘʟᴏᴀᴅᴇʀ"