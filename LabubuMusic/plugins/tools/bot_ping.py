from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.core.stream_call import Samar
from MattoMusic.utils import bot_sys_stats
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.inline import supp_markup
from config import BANNED_USERS, PING_IMG_URL

@app.on_message(filters.command(["ping", "alive"]) & ~BANNED_USERS)
@language
async def reply_ping(client, message: Message, _):
    start_t = datetime.now()
    ping_status = await message.reply_photo(photo=PING_IMG_URL, caption=_["ping_1"].format(app.mention))
    
    tg_ping_res = await Samar.ping()
    sys_up, sys_cpu, sys_ram, sys_disk = await bot_sys_stats()
    
    latency = (datetime.now() - start_t).microseconds / 1000
    
    await ping_status.edit_text(
        _["ping_2"].format(latency, app.mention, sys_up, sys_ram, sys_cpu, sys_disk, tg_ping_res),
        reply_markup=supp_markup(_)
    )