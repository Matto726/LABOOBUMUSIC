from MattoMusic.misc import SUDOERS
from MattoMusic.utils.database import get_lang, is_maintenance
from config import SUPPORT_GROUP
from strings import get_string


def inject_language(func_to_wrap):
    async def standard_lang_wrapper(_, message, **kwargs):
        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except Exception:
            pass

        try:
            lang_code = await get_lang(message.chat.id)
            lang_str = get_string(lang_code)
        except Exception:
            lang_str = get_string("en")
            
        return await func_to_wrap(_, message, lang_str)

    return standard_lang_wrapper


def inject_language_cb(func_to_wrap):
    async def cb_lang_wrapper(_, query, **kwargs):
        if not await is_maintenance():
            if query.from_user.id not in SUDOERS:
                return await query.answer(
                    f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    show_alert=True,
                )
        try:
            lang_code = await get_lang(query.message.chat.id)
            lang_str = get_string(lang_code)
        except Exception:
            lang_str = get_string("en")
            
        return await func_to_wrap(_, query, lang_str)

    return cb_lang_wrapper


def inject_language_start(func_to_wrap):
    async def start_lang_wrapper(_, message, **kwargs):
        try:
            lang_code = await get_lang(message.chat.id)
            lang_str = get_string(lang_code)
        except Exception:
            lang_str = get_string("en")
            
        return await func_to_wrap(_, message, lang_str)

    return start_lang_wrapper