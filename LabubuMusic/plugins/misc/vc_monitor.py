from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.core.stream_call import Samar

VC_INIT = 20
VC_TERMINATE = 30

@app.on_message(filters.video_chat_started, group=VC_INIT)
@app.on_message(filters.video_chat_ended, group=VC_TERMINATE)
async def handle_vc_events(client, message: Message):
    await Samar.stop_stream_force(message.chat.id)