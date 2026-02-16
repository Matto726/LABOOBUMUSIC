import platform
import psutil
from sys import version as py_version
from pyrogram import __version__ as pyro_version
from pyrogram import filters
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytg_version

import config
from MattoMusic import app
from MattoMusic.core.assistant_bot import assistants
from MattoMusic.misc import SUDOERS, mongodb
from MattoMusic.plugins import ALL_MODULES
from MattoMusic.utils.database import get_served_chats, get_served_users, get_sudoers, is_autoend, is_autoleave
from MattoMusic.utils.decorators.language import language, languageCB
from MattoMusic.utils.inline.stats import back_stats_buttons, stats_buttons
from config import BANNED_USERS

@app.on_message(filters.command(["stats", "gstats"]) & filters.group & ~BANNED_USERS)
@language
async def show_bot_stats(client, message: Message, _):
    btn_markup = stats_buttons(_, True if message.from_user.id in SUDOERS else False)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_1"].format(app.mention),
        reply_markup=btn_markup,
    )

@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats_cb(client, query, _):
    try: await query.answer()
    except Exception: pass
    await query.edit_message_text(_["gstats_2"])

@app.on_callback_query(filters.regex("bot_stats_sudo") & ~BANNED_USERS)
@languageCB
async def hardware_stats_cb(client, query, _):
    if query.from_user.id not in SUDOERS:
        return await query.answer(_["gstats_3"], show_alert=True)
        
    sys_markup = back_stats_buttons(_)
    try: await query.answer()
    except Exception: pass
    
    physical_cores = psutil.cpu_count(logical=False)
    total_cores = psutil.cpu_count(logical=True)
    ram_usage = f"{round(psutil.virtual_memory().total / (1024.0**3))} GB"
    cpu_freq = "N/A"
    try: cpu_freq = f"{round(psutil.cpu_freq().current / 1000, 2)} GHz"
    except Exception: pass
    
    disk_data = psutil.disk_usage("/")
    total_disk = disk_data.total / (1024.0**3)
    used_disk = disk_data.used / (1024.0**3)
    free_disk = disk_data.free / (1024.0**3)
    
    db_stats = await mongodb.command("dbstats")
    d_size = db_stats["dataSize"] / 1024
    s_size = db_stats["storageSize"] / 1024
    
    chats_count = len(await get_served_chats())
    users_count = len(await get_served_users())
    
    formatted_stats = _["gstats_5"].format(
        app.mention, len(ALL_MODULES), platform.system(), ram_usage,
        physical_cores, total_cores, cpu_freq, py_version.split()[0],
        pyro_version, pytg_version, str(total_disk)[:4], str(used_disk)[:4],
        str(free_disk)[:4], chats_count, users_count, len(BANNED_USERS),
        len(await get_sudoers()), str(d_size)[:6], s_size, db_stats["collections"], db_stats["objects"]
    )
    
    new_media = InputMediaPhoto(media=config.STATS_IMG_URL, caption=formatted_stats)
    try:
        await query.edit_message_media(media=new_media, reply_markup=sys_markup)
    except MessageIdInvalid:
        await query.message.reply_photo(photo=config.STATS_IMG_URL, caption=formatted_stats, reply_markup=sys_markup)

@app.on_callback_query(filters.regex("state_back") & ~BANNED_USERS)
@languageCB
async def revert_to_main_stats(client, query, _):
    try: await query.answer()
    except Exception: pass
    
    btn_markup = stats_buttons(_, True if query.from_user.id in SUDOERS else False)
    new_media = InputMediaPhoto(media=config.STATS_IMG_URL, caption=_["gstats_1"].format(app.mention))
    
    try:
        await query.edit_message_media(media=new_media, reply_markup=btn_markup)
    except MessageIdInvalid:
        await query.message.reply_photo(photo=config.STATS_IMG_URL, caption=_["gstats_1"].format(app.mention), reply_markup=btn_markup)