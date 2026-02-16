from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageNotModified
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from MattoMusic import app
from MattoMusic.utils.database import (
    add_nonadmin_chat, get_authuser, get_authuser_names, get_playmode,
    get_playtype, get_upvote_count, is_nonadmin_chat, is_skipmode,
    remove_nonadmin_chat, set_playmode, set_playtype, set_upvotes, skip_off, skip_on,
)
from MattoMusic.utils import bot_sys_stats
from MattoMusic.utils.decorators.admins import ActualAdminCB
from MattoMusic.utils.decorators.language import language, languageCB
from MattoMusic.utils.inline.settings import (
    auth_users_markup, playmode_users_markup, setting_markup, vote_mode_markup,
)
from MattoMusic.utils.inline.start import private_panel
from config import BANNED_USERS, OWNER_ID

@app.on_message(filters.command(["settings", "setting"]) & filters.group & ~BANNED_USERS)
@language
async def settings_command_handler(client, message: Message, _):
    btn_markup = setting_markup(_)
    await message.reply_text(
        _["setting_1"].format(app.mention, message.chat.id, message.chat.title),
        reply_markup=InlineKeyboardMarkup(btn_markup),
    )

@app.on_callback_query(filters.regex("settings_helper") & ~BANNED_USERS)
@languageCB
async def settings_menu_cb(client, query: CallbackQuery, _):
    try: await query.answer(_["set_cb_5"])
    except Exception: pass
    
    btn_markup = setting_markup(_)
    return await query.edit_message_text(
        _["setting_1"].format(app.mention, query.message.chat.id, query.message.chat.title),
        reply_markup=InlineKeyboardMarkup(btn_markup),
    )

@app.on_callback_query(filters.regex("settingsback_helper") & ~BANNED_USERS)
@languageCB
async def settings_back_cb(client, query: CallbackQuery, _):
    try: await query.answer()
    except Exception: pass
    
    if query.message.chat.type == ChatType.PRIVATE:
        await app.resolve_peer(OWNER_ID)
        btn_markup = private_panel(_)
        up_t, cpu_u, ram_u, disk_u = await bot_sys_stats()
        return await query.edit_message_text(
            _["start_2"].format(query.from_user.mention, app.mention, up_t, disk_u, cpu_u, ram_u),
            reply_markup=InlineKeyboardMarkup(btn_markup),
        )
    else:
        btn_markup = setting_markup(_)
        return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))

@app.on_callback_query(filters.regex(pattern=r"^(SEARCHANSWER|PLAYMODEANSWER|PLAYTYPEANSWER|AUTHANSWER|ANSWERVOMODE|VOTEANSWER|PM|AU|VM)$") & ~BANNED_USERS)
@languageCB
async def basic_settings_cb(client, query: CallbackQuery, _):
    cmd = query.matches[0].group(1)
    
    alerts = {
        "SEARCHANSWER": _["setting_2"],
        "PLAYMODEANSWER": _["setting_5"],
        "PLAYTYPEANSWER": _["setting_6"],
        "AUTHANSWER": _["setting_3"],
        "VOTEANSWER": _["setting_8"],
    }
    
    if cmd in alerts:
        try: return await query.answer(alerts[cmd], show_alert=True)
        except Exception: return
        
    if cmd == "ANSWERVOMODE":
        current_votes = await get_upvote_count(query.message.chat.id)
        try: return await query.answer(_["setting_9"].format(current_votes), show_alert=True)
        except Exception: return
        
    btn_markup = None
    if cmd == "PM":
        try: await query.answer(_["set_cb_2"], show_alert=True)
        except Exception: pass
        
        is_direct = (await get_playmode(query.message.chat.id)) == "Direct"
        is_group = not (await is_nonadmin_chat(query.message.chat.id))
        is_playtype = (await get_playtype(query.message.chat.id)) != "Everyone"
        
        btn_markup = playmode_users_markup(_, True if is_direct else None, True if is_group else None, True if is_playtype else None)
        
    elif cmd == "AU":
        try: await query.answer(_["set_cb_1"], show_alert=True)
        except Exception: pass
        
        is_non_admin = await is_nonadmin_chat(query.message.chat.id)
        btn_markup = auth_users_markup(_, True if not is_non_admin else False)
        
    elif cmd == "VM":
        is_skip = await is_skipmode(query.message.chat.id)
        current_votes = await get_upvote_count(query.message.chat.id)
        btn_markup = vote_mode_markup(_, current_votes, is_skip)
        
    if btn_markup:
        try: return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))
        except MessageNotModified: return

@app.on_callback_query(filters.regex("FERRARIUDTI") & ~BANNED_USERS)
@ActualAdminCB
async def adjust_votes_cb(client, query: CallbackQuery, _):
    cb_data = query.data.strip().split(None, 1)[1]
    
    if not await is_skipmode(query.message.chat.id):
        return await query.answer(_["setting_10"], show_alert=True)
        
    current_votes = await get_upvote_count(query.message.chat.id)
    
    if cb_data == "M":
        new_val = max(2, current_votes - 2)
        if current_votes - 2 <= 0:
            return await query.answer(_["setting_11"], show_alert=True)
    else:
        new_val = min(15, current_votes + 2)
        if current_votes + 2 > 15:
            return await query.answer(_["setting_12"], show_alert=True)
            
    await set_upvotes(query.message.chat.id, new_val)
    btn_markup = vote_mode_markup(_, new_val, True)
    
    try: return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))
    except MessageNotModified: return

@app.on_callback_query(filters.regex(pattern=r"^(MODECHANGE|CHANNELMODECHANGE|PLAYTYPECHANGE)$") & ~BANNED_USERS)
@ActualAdminCB
async def toggle_playmode_cb(client, query: CallbackQuery, _):
    cmd = query.matches[0].group(1)
    chat_id = query.message.chat.id
    
    if cmd == "CHANNELMODECHANGE":
        is_non_admin = await is_nonadmin_chat(chat_id)
        if not is_non_admin: await add_nonadmin_chat(chat_id)
        else: await remove_nonadmin_chat(chat_id)
        
    elif cmd == "MODECHANGE":
        try: await query.answer(_["set_cb_3"], show_alert=True)
        except Exception: pass
        current_mode = await get_playmode(chat_id)
        await set_playmode(chat_id, "Inline" if current_mode == "Direct" else "Direct")
        
    elif cmd == "PLAYTYPECHANGE":
        try: await query.answer(_["set_cb_3"], show_alert=True)
        except Exception: pass
        current_type = await get_playtype(chat_id)
        await set_playtype(chat_id, "Admin" if current_type == "Everyone" else "Everyone")

    is_direct = (await get_playmode(chat_id)) == "Direct"
    is_group = not (await is_nonadmin_chat(chat_id))
    is_playtype = (await get_playtype(chat_id)) != "Everyone"
    
    btn_markup = playmode_users_markup(_, True if is_direct else None, True if is_group else None, True if is_playtype else False)
    
    try: return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))
    except MessageNotModified: return

@app.on_callback_query(filters.regex(pattern=r"^(AUTH|AUTHLIST)$") & ~BANNED_USERS)
@ActualAdminCB
async def toggle_auth_cb(client, query: CallbackQuery, _):
    cmd = query.matches[0].group(1)
    chat_id = query.message.chat.id
    
    if cmd == "AUTHLIST":
        auth_names = await get_authuser_names(chat_id)
        if not auth_names:
            try: return await query.answer(_["setting_4"], show_alert=True)
            except Exception: return
            
        try: await query.answer(_["set_cb_4"], show_alert=True)
        except Exception: pass
        
        await query.edit_message_text(_["auth_6"])
        msg_text = _["auth_7"].format(query.message.chat.title)
        
        for idx, token in enumerate(auth_names, 1):
            auth_info = await get_authuser(chat_id, token)
            try:
                user_obj = await app.get_users(auth_info["auth_user_id"])
                msg_text += f"{idx}➤ {user_obj.first_name}[<code>{auth_info['auth_user_id']}</code>]\n   {_['auth_8']} {auth_info['admin_name']}[<code>{auth_info['admin_id']}</code>]\n\n"
            except Exception: continue
            
        btn_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="AU"), InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]
        ])
        
        try: return await query.edit_message_text(msg_text, reply_markup=btn_markup)
        except MessageNotModified: return

    try: await query.answer(_["set_cb_3"], show_alert=True)
    except Exception: pass
    
    if cmd == "AUTH":
        is_non_admin = await is_nonadmin_chat(chat_id)
        if not is_non_admin: await add_nonadmin_chat(chat_id)
        else: await remove_nonadmin_chat(chat_id)
        
        btn_markup = auth_users_markup(_, True if not is_non_admin else False)
        
    try: return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))
    except MessageNotModified: return

@app.on_callback_query(filters.regex("VOMODECHANGE") & ~BANNED_USERS)
@ActualAdminCB
async def toggle_vote_mode_cb(client, query: CallbackQuery, _):
    try: await query.answer(_["set_cb_3"], show_alert=True)
    except Exception: pass
    
    chat_id = query.message.chat.id
    if await is_skipmode(chat_id):
        await skip_off(chat_id)
        is_skip = None
    else:
        await skip_on(chat_id)
        is_skip = True
        
    current_votes = await get_upvote_count(chat_id)
    btn_markup = vote_mode_markup(_, current_votes, is_skip)

    try: return await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn_markup))
    except MessageNotModified: return