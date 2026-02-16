import io
from gtts import gTTS
from pyrogram import filters
from MattoMusic import app

@app.on_message(filters.command("tts"))
async def convert_text_to_audio(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴛᴏ sᴘᴇᴇᴄʜ.")

    input_text = message.text.split(None, 1)[1]
    
    tts_engine = gTTS(input_text, lang="hi")
    audio_buffer = io.BytesIO()
    tts_engine.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    mem_file = io.BytesIO(audio_buffer.read())
    mem_file.name = "audio.mp3"
    
    await message.reply_audio(mem_file)

__HELP__ = """
**Tᴇxᴛ Tᴏ Sᴘᴇᴇᴄʜ ᴄᴏᴍᴍᴀɴᴅ:**
- `/tts <text>`: ᴄᴏɴᴠᴇʀᴛ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ɪɴᴛᴏ ᴀɴ ᴀᴜᴅɪᴏ ғɪʟᴇ (Hɪɴᴅɪ ᴀᴄᴄᴇɴᴛ).
"""
__MODULE__ = "TTS"