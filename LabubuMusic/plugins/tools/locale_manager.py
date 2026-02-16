from pykeyboard import InlineKeyboard
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, Message

from MattoMusic import app
from MattoMusic.utils.database import get_lang, set_lang
from MattoMusic.utils.decorators import ActualAdminCB, language, languageCB
from config import BANNED_USERS
from strings import get_string, languages_present

def locale_buttons(_):
    layout = InlineKeyboard(row_width=2)
    layout.add(
        *[
            (InlineKeyboardButton(text=languages_present[i], callback_data=f"set_lang:{i}"))
            for i in languages_present
        ]
    )
    layout.row(
        InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data=f"settingsback_helper"),
        InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"close"),
    )
    return layout

@app.on_message(filters.command(["lang", "language"]) & filters.group & ~BANNED_USERS)
@language
async def trigger_language_menu(client, message: Message, _):
    btn_markup = locale_buttons(_)
    await message.reply_text(_["lang_1"], reply_markup=btn_markup)

@app.on_callback_query(filters.regex("LG") & ~BANNED_USERS)
@languageCB
async def trigger_language_cb(client, query, _):
    try: await query.answer()
    except Exception: pass
    btn_markup = locale_buttons(_)
    return await query.edit_message_reply_markup(reply_markup=btn_markup)

@app.on_callback_query(filters.regex(r"set_lang:(.*?)") & ~BANNED_USERS)
@ActualAdminCB
async def update_locale_selection(client, query, _):
    selected_lang = query.data.split(":")[1]
    current_lang = await get_lang(query.message.chat.id)
    
    if str(current_lang) == str(selected_lang):
        return await query.answer(_["lang_4"], show_alert=True)
        
    try:
        _ = get_string(selected_lang)
        await query.answer(_["lang_2"], show_alert=True)
    except Exception:
        _ = get_string(current_lang)
        return await query.answer(_["lang_3"], show_alert=True)
        
    await set_lang(query.message.chat.id, selected_lang)
    btn_markup = locale_buttons(_)
    return await query.edit_message_reply_markup(reply_markup=btn_markup)