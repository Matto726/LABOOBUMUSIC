from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from MattoMusic import app
from MattoMusic.misc import SUDOERS, db
from MattoMusic.utils.database import (
    get_authuser_names,
    get_cmode,
    get_lang,
    get_upvote_count,
    is_active_chat,
    is_maintenance,
    is_nonadmin_chat,
    is_skipmode,
)
from config import SUPPORT_GROUP, adminlist, confirmer
from strings import get_string
from ..formatters import int_to_alpha


def verify_admin_rights(func_to_wrap):
    async def rights_wrapper(client, message):
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
            
        if message.sender_chat:
            btn_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(lang_str["general_3"], reply_markup=btn_markup)
            
        if message.command[0][0] == "c":
            target_chat_id = await get_cmode(message.chat.id)
            if target_chat_id is None:
                return await message.reply_text(lang_str["setting_7"])
            try:
                await app.get_chat(target_chat_id)
            except Exception:
                return await message.reply_text(lang_str["cplay_4"])
        else:
            target_chat_id = message.chat.id
            
        if not await is_active_chat(target_chat_id):
            return await message.reply_text(lang_str["general_5"])
            
        is_regular_chat = await is_nonadmin_chat(message.chat.id)
        
        if not is_regular_chat:
            if message.from_user.id not in SUDOERS:
                chat_admins = adminlist.get(message.chat.id)
                if not chat_admins:
                    return await message.reply_text(lang_str["admin_13"])
                else:
                    if message.from_user.id not in chat_admins:
                        if await is_skipmode(message.chat.id):
                            req_upvotes = await get_upvote_count(target_chat_id)
                            alert_text = f"""<b>ᴀᴅᴍɪɴ ʀɪɢʜᴛs ɴᴇᴇᴅᴇᴅ</b>\n\nʀᴇғʀᴇsʜ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ ᴠɪᴀ : /reload\n\n» {req_upvotes} ᴠᴏᴛᴇs ɴᴇᴇᴅᴇᴅ ғᴏʀ ᴘᴇʀғᴏʀᴍɪɴɢ ᴛʜɪs ᴀᴄᴛɪᴏɴ."""

                            cmd_action = message.command[0]
                            if cmd_action[0] == "c":
                                cmd_action = cmd_action[1:]
                            if cmd_action == "speed":
                                return await message.reply_text(lang_str["admin_14"])
                                
                            action_mode = cmd_action.title()
                            vote_markup = InlineKeyboardMarkup(
                                [[InlineKeyboardButton(text="ᴠᴏᴛᴇ", callback_data=f"ADMIN  UpVote|{target_chat_id}_{action_mode}")]]
                            )
                            
                            if target_chat_id not in confirmer:
                                confirmer[target_chat_id] = {}
                            try:
                                stream_vidid = db[target_chat_id][0]["vidid"]
                                stream_file = db[target_chat_id][0]["file"]
                            except Exception:
                                return await message.reply_text(lang_str["admin_14"])
                                
                            dispatched_msg = await message.reply_text(alert_text, reply_markup=vote_markup)
                            confirmer[target_chat_id][dispatched_msg.id] = {
                                "vidid": stream_vidid,
                                "file": stream_file,
                            }
                            return
                        else:
                            return await message.reply_text(lang_str["admin_14"])

        return await func_to_wrap(client, message, lang_str, target_chat_id)

    return rights_wrapper


def require_admin_status(func_to_wrap):
    async def actual_admin_wrapper(client, message):
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
            
        if message.sender_chat:
            btn_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin")]]
            )
            return await message.reply_text(lang_str["general_3"], reply_markup=btn_markup)
            
        if message.from_user.id not in SUDOERS:
            try:
                user_privileges = (
                    await app.get_chat_member(message.chat.id, message.from_user.id)
                ).privileges
            except Exception:
                return
            if not user_privileges.can_manage_video_chats:
                return await message.reply(lang_str["general_4"])
                
        return await func_to_wrap(client, message, lang_str)

    return actual_admin_wrapper


def verify_admin_cb(func_to_wrap):
    async def cb_admin_wrapper(client, query):
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
            
        if query.message.chat.type == ChatType.PRIVATE:
            return await func_to_wrap(client, query, lang_str)
            
        is_regular_chat = await is_nonadmin_chat(query.message.chat.id)
        if not is_regular_chat:
            try:
                user_privileges = (
                    await app.get_chat_member(
                        query.message.chat.id,
                        query.from_user.id,
                    )
                ).privileges
            except Exception:
                return await query.answer(lang_str["general_4"], show_alert=True)
                
            if not user_privileges.can_manage_video_chats:
                if query.from_user.id not in SUDOERS:
                    u_token = await int_to_alpha(query.from_user.id)
                    auth_list = await get_authuser_names(query.from_user.id)
                    if u_token not in auth_list:
                        try:
                            return await query.answer(lang_str["general_4"], show_alert=True)
                        except Exception:
                            return
                            
        return await func_to_wrap(client, query, lang_str)

    return cb_admin_wrapper