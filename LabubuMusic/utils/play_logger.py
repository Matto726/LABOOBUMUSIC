from pyrogram.enums import ParseMode

from MattoMusic import app
from MattoMusic.utils.database import is_on_off
from config import LOG_GROUP_ID

async def play_logs(msg_obj, stream_mode):
    if await is_on_off(2):
        log_content = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{msg_obj.chat.id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {msg_obj.chat.title}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> @{msg_obj.chat.username}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{msg_obj.from_user.id}</code>
<b>ɴᴀᴍᴇ :</b> {msg_obj.from_user.mention}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{msg_obj.from_user.username}

<b>ǫᴜᴇʀʏ :</b> {msg_obj.text.split(None, 1)[1]}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {stream_mode}"""

        if msg_obj.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=log_content,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception:
                pass