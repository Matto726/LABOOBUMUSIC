import time
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from MattoMusic import app
from MattoMusic.misc import _boot_
from MattoMusic.plugins.sudo.sudoers import sudoers_list
from MattoMusic.utils.database import (
    add_served_chat, add_served_user, blacklisted_chats,
    get_lang, is_banned_user, is_on_off,
)
from MattoMusic.utils import bot_sys_stats
from MattoMusic.utils.decorators.language import LanguageStart
from MattoMusic.utils.formatters import get_readable_time
from MattoMusic.utils.inline import help_pannel_page1, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def handle_start_private(client, message: Message, _):
    await add_served_user(message.from_user.id)
    args = message.text.split()
    
    if len(args) > 1:
        payload = args[1]
        
        if payload.startswith("help"):
            btn_markup = help_pannel_page1(_)
            kwargs = {"photo": config.START_IMG_URL, "caption": _["help_1"].format(config.SUPPORT_GROUP), "reply_markup": btn_markup}
            try: return await message.reply_photo(**kwargs, message_effect_id=5159385139981059251)
            except Exception: return await message.reply_photo(**kwargs)
                
        if payload.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
            return
            
        if payload.startswith("inf"):
            loader = await message.reply_text("🔎")
            v_query = payload.replace("info_", "", 1)
            search_url = f"https://www.youtube.com/watch?v={v_query}"
            
            yt_res = VideosSearch(search_url, limit=1)
            v_data = (await yt_res.next())["result"][0]
            
            info_text = _["start_6"].format(
                v_data["title"], v_data["duration"], v_data["viewCount"]["short"], 
                v_data["publishedTime"], v_data["channel"]["link"], v_data["channel"]["name"], app.mention
            )
            
            btn_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=_["S_B_8"], url=v_data["link"]), InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP)]
            ])
            
            await loader.delete()
            kwargs = {"photo": v_data["thumbnails"][0]["url"].split("?")[0], "caption": info_text, "reply_markup": btn_markup}
            try: await app.send_photo(chat_id=message.chat.id, **kwargs, message_effect_id=5159385139981059251)
            except Exception: await app.send_photo(chat_id=message.chat.id, **kwargs)
                
            if await is_on_off(2):
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                )
                
        if payload == "start":
            pass # Falls through to default start block

    btn_markup = private_panel(_)
    up_t, cpu_u, ram_u, disk_u = await bot_sys_stats()
    kwargs = {"photo": config.START_IMG_URL, "caption": _["start_2"].format(message.from_user.mention, app.mention, up_t, disk_u, cpu_u, ram_u), "reply_markup": InlineKeyboardMarkup(btn_markup)}
    
    try: await message.reply_photo(**kwargs, message_effect_id=5159385139981059251)
    except Exception: await message.reply_photo(**kwargs)
        
    if await is_on_off(2):
        return await app.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
        )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def handle_start_group(client, message: Message, _):
    btn_markup = start_panel(_)
    up_duration = int(time.time() - _boot_)
    kwargs = {"photo": config.START_IMG_URL, "caption": _["start_1"].format(app.mention, get_readable_time(up_duration)), "reply_markup": InlineKeyboardMarkup(btn_markup)}
    
    try: await message.reply_photo(**kwargs, message_effect_id=5159385139981059251)
    except Exception: await message.reply_photo(**kwargs)
        
    return await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def handle_new_members(client, message: Message):
    for new_member in message.new_chat_members:
        try:
            lang_code = await get_lang(message.chat.id)
            _ = get_string(lang_code)
            
            if await is_banned_user(new_member.id):
                try: await message.chat.ban_member(new_member.id)
                except Exception: pass
                
            if new_member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(app.mention, f"https://t.me/{app.username}?start=sudolist", config.SUPPORT_GROUP),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                btn_markup = start_panel(_)
                kwargs = {"photo": config.START_IMG_URL, "caption": _["start_3"].format(message.from_user.first_name, app.mention, message.chat.title, app.mention), "reply_markup": InlineKeyboardMarkup(btn_markup)}
                
                try: await message.reply_photo(**kwargs, message_effect_id=5159385139981059251)
                except Exception: await message.reply_photo(**kwargs)
                    
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except Exception as e:
            print(f"Welcome Watcher Error: {e}")