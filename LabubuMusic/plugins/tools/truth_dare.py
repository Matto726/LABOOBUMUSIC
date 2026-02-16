import requests
from pyrogram import filters
from MattoMusic import app

TRUTH_ENDPOINT = "https://api.truthordarebot.xyz/v1/truth"
DARE_ENDPOINT = "https://api.truthordarebot.xyz/v1/dare"

@app.on_message(filters.command("truth"))
def fetch_truth(client, message):
    try:
        api_res = requests.get(TRUTH_ENDPOINT)
        if api_res.status_code == 200:
            question_data = api_res.json()["question"]
            message.reply_text(f"🗣️ **Tʀᴜᴛʜ Qᴜᴇsᴛɪᴏɴ:**\n\n{question_data}")
        else:
            message.reply_text("❌ Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
    except Exception:
        message.reply_text("⚠️ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴀ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ.")

@app.on_message(filters.command("dare"))
def fetch_dare(client, message):
    try:
        api_res = requests.get(DARE_ENDPOINT)
        if api_res.status_code == 200:
            question_data = api_res.json()["question"]
            message.reply_text(f"🔥 **Dᴀʀᴇ Cʜᴀʟʟᴇɴɢᴇ:**\n\n{question_data}")
        else:
            message.reply_text("❌ Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀ ᴅᴀʀᴇ ᴄʜᴀʟʟᴇɴɢᴇ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
    except Exception:
        message.reply_text("⚠️ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ғᴇᴛᴄʜɪɴɢ ᴀ ᴅᴀʀᴇ ᴄʜᴀʟʟᴇɴɢᴇ.")

__HELP__ = """
**ᴛʀᴜᴛʜ ᴏʀ ᴅᴀʀᴇ:**
- `/truth`: Gᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ᴛʀᴜᴛʜ ǫᴜᴇsᴛɪᴏɴ.
- `/dare`: Gᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ᴅᴀʀᴇ ᴄʜᴀʟʟᴇɴɢᴇ.
"""
__MODULE__ = "Tʀᴜᴛʜ/Dᴀʀᴇ"