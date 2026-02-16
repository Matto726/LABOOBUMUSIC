from typing import Union
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, Message

from MattoMusic import app
from MattoMusic.utils.database import get_lang
from MattoMusic.utils.decorators.language import LanguageStart, languageCB
from MattoMusic.utils.inline.help import (
    help_back_markup, private_help_panel, help_pannel_page1,
    help_pannel_page2, help_pannel_page3, help_pannel_page4,
)
from config import BANNED_USERS, START_IMG_URL, SUPPORT_GROUP
from strings import get_string, helpers

@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("help_page_1") & ~BANNED_USERS)
async def private_help_handler(client: app, update: Union[types.Message, types.CallbackQuery]):
    is_cb = isinstance(update, types.CallbackQuery)
    
    if is_cb:
        try: await update.answer()
        except Exception: pass
        
        chat_id = update.message.chat.id
        lang_code = await get_lang(chat_id)
        _ = get_string(lang_code)
        
        from MattoMusic.utils.inline.help import help_pannel_page1
        btn_markup = help_pannel_page1(_, True)
        await update.edit_message_text(_["help_1"].format(SUPPORT_GROUP), reply_markup=btn_markup)
    else:
        try: await update.delete()
        except Exception: pass
        
        lang_code = await get_lang(update.chat.id)
        _ = get_string(lang_code)
        
        from MattoMusic.utils.inline.help import help_pannel_page1
        btn_markup = help_pannel_page1(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_GROUP),
            reply_markup=btn_markup,
        )

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def group_help_handler(client, message: Message, _):
    from MattoMusic.utils.inline.help import private_help_panel
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))

@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_pagination_cb(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]

    def build_keyboard(req_page):
        p1 = ["hb1", "hb2", "hb3", "hb4", "hb5", "hb6", "hb7", "hb8", "hb9", "hb10"]
        p2 = ["hb11", "hb12", "hb13", "hb14", "hb15", "hb17", "hb18", "hb19", "hb20", "hb21"]
        p3 = ["hb22", "hb23", "hb24", "hb25", "hb26", "hb27", "hb28", "hb29", "hb30", "hb31"]
        p4 = ["hb32", "hb33", "hb34", "hb35", "hb36", "hb37", "hb38", "hb39"]

        if req_page in p1: return help_back_markup(_, page=1)
        elif req_page in p2: return help_back_markup(_, page=2)
        elif req_page in p3: return help_back_markup(_, page=3)
        elif req_page in p4: return help_back_markup(_, page=4)
        return help_back_markup(_, page=1)

    if cb_data.startswith("hb") and cb_data[2:].isdigit():
        idx = int(cb_data[2:])
        if 1 <= idx <= 39:
            help_text = getattr(helpers, f"HELP_{idx}", helpers.HELP_1)
            await query.edit_message_text(help_text, reply_markup=build_keyboard(cb_data))