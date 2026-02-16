from functools import wraps
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden
from pyrogram.types import Message
from MattoMusic import app
from MattoMusic.misc import SUDOERS

async def member_permissions(chat_id: int, user_id: int):
    active_perms = []
    try:
        user_info = await app.get_chat_member(chat_id, user_id)
        privs = user_info.privileges
        if not privs:
            return []
            
        if privs.can_post_messages: active_perms.append("can_post_messages")
        if privs.can_edit_messages: active_perms.append("can_edit_messages")
        if privs.can_delete_messages: active_perms.append("can_delete_messages")
        if privs.can_restrict_members: active_perms.append("can_restrict_members")
        if privs.can_promote_members: active_perms.append("can_promote_members")
        if privs.can_change_info: active_perms.append("can_change_info")
        if privs.can_invite_users: active_perms.append("can_invite_users")
        if privs.can_pin_messages: active_perms.append("can_pin_messages")
        if privs.can_manage_video_chats: active_perms.append("can_manage_video_chats")
    except Exception:
        pass
    return active_perms

async def bot_permissions(chat_id: int):
    active_perms = []
    try:
        bot_info = await app.get_chat_member(chat_id, app.id)
        privs = bot_info.privileges
        if not privs:
            return []
            
        if privs.can_post_messages: active_perms.append("can_post_messages")
        if privs.can_edit_messages: active_perms.append("can_edit_messages")
        if privs.can_delete_messages: active_perms.append("can_delete_messages")
        if privs.can_restrict_members: active_perms.append("can_restrict_members")
        if privs.can_promote_members: active_perms.append("can_promote_members")
        if privs.can_change_info: active_perms.append("can_change_info")
        if privs.can_invite_users: active_perms.append("can_invite_users")
        if privs.can_pin_messages: active_perms.append("can_pin_messages")
        if privs.can_manage_video_chats: active_perms.append("can_manage_video_chats")
    except Exception:
        pass
    return active_perms

async def unauthorised(message: Message, permission: str, bot_missing: bool = False):
    try:
        if bot_missing:
            text = f"I don't have the required permission to perform this action.\n**Missing:** `{permission}`"
        else:
            text = f"You don't have the required permission to perform this action.\n**Missing:** `{permission}`"
        await message.reply_text(text)
    except ChatWriteForbidden:
        await app.leave_chat(message.chat.id)
    except Exception:
        pass

async def authorised(func, client, message, *args, **kwargs):
    try:
        return await func(client, message, *args, **kwargs)
    except ChatWriteForbidden:
        await app.leave_chat(message.chat.id)
    except Exception as e:
        try:
            await message.reply_text(f"An error occurred: `{e}`")
        except Exception:
            pass

def adminsOnly(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            chat_id = message.chat.id
            
            # Check bot permissions first
            bot_perms = await bot_permissions(chat_id)
            if permission not in bot_perms:
                return await unauthorised(message, permission, bot_missing=True)
                
            # Check user permissions
            if not message.from_user:
                if message.sender_chat and message.sender_chat.id == chat_id:
                    return await authorised(func, client, message, *args, **kwargs)
                return await unauthorised(message, permission)
                
            user_id = message.from_user.id
            user_perms = await member_permissions(chat_id, user_id)
            
            if user_id not in SUDOERS and permission not in user_perms:
                return await unauthorised(message, permission)
                
            return await authorised(func, client, message, *args, **kwargs)
        return wrapper
    return decorator