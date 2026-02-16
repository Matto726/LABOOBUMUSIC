from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.utils import extract_user, int_to_alpha
from MattoMusic.utils.database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from MattoMusic.utils.decorators import AdminActual, language
from MattoMusic.utils.inline import close_markup
from config import BANNED_USERS, adminlist

@app.on_message(filters.command("auth") & filters.group & ~BANNED_USERS)
@AdminActual
async def authorize_user(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
            
    target_user = await extract_user(message)
    user_token = await int_to_alpha(target_user.id)
    auth_list = await get_authuser_names(message.chat.id)
    
    if len(auth_list) == 25:
        return await message.reply_text(_["auth_1"])
        
    if user_token not in auth_list:
        auth_data = {
            "auth_user_id": target_user.id,
            "auth_name": target_user.first_name,
            "admin_id": message.from_user.id,
            "admin_name": message.from_user.first_name,
        }
        admins = adminlist.get(message.chat.id)
        if admins and target_user.id not in admins:
            admins.append(target_user.id)
            
        await save_authuser(message.chat.id, user_token, auth_data)
        return await message.reply_text(_["auth_2"].format(target_user.mention))
    else:
        return await message.reply_text(_["auth_3"].format(target_user.mention))


@app.on_message(filters.command("unauth") & filters.group & ~BANNED_USERS)
@AdminActual
async def unauthorize_user(client, message: Message, _):
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["general_1"])
            
    target_user = await extract_user(message)
    user_token = await int_to_alpha(target_user.id)
    is_deleted = await delete_authuser(message.chat.id, user_token)
    
    admins = adminlist.get(message.chat.id)
    if admins and target_user.id in admins:
        admins.remove(target_user.id)
        
    if is_deleted:
        return await message.reply_text(_["auth_4"].format(target_user.mention))
    else:
        return await message.reply_text(_["auth_5"].format(target_user.mention))


@app.on_message(filters.command(["authlist", "authusers"]) & filters.group & ~BANNED_USERS)
@language
async def list_authorized_users(client, message: Message, _):
    auth_list = await get_authuser_names(message.chat.id)
    
    if not auth_list:
        return await message.reply_text(_["setting_4"])
        
    counter = 0
    loading_msg = await message.reply_text(_["auth_6"])
    display_text = _["auth_7"].format(message.chat.title)
    
    for token in auth_list:
        auth_info = await get_authuser(message.chat.id, token)
        u_id = auth_info["auth_user_id"]
        a_id = auth_info["admin_id"]
        a_name = auth_info["admin_name"]
        
        try:
            u_info = (await app.get_users(u_id)).first_name
            counter += 1
        except Exception:
            continue
            
        display_text += f"{counter}➤ {u_info}[<code>{u_id}</code>]\n"
        display_text += f"   {_['auth_8']} {a_name}[<code>{a_id}</code>]\n\n"
        
    await loading_msg.edit_text(display_text, reply_markup=close_markup(_))