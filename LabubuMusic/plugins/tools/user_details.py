import asyncio
import re
from datetime import datetime
from pyrogram import filters, types, enums
from MattoMusic import app

INFO_TEXT_LAYOUT = """
**👤 ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:**
**ɪᴅ:** `{}`
**ɴᴀᴍᴇ:** {}
**ᴜsᴇʀɴᴀᴍᴇ:** {}
**ᴍᴇɴᴛɪᴏɴ:** {}
**ᴅᴄ ɪᴅ:** {}
**ᴘʀᴇᴍɪᴜᴍ:** {}
**ʙɪᴏ:** {}
**ᴍᴜᴛᴜᴀʟ ᴄʜᴀᴛs:** {}
**ᴊᴏɪɴᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ:** {}
**sᴛᴀᴛᴜs:** {}
"""

async def get_user_status(uid):
    try:
        u_data = await app.get_users(uid)
        u_stat = u_data.status
        if u_stat == enums.UserStatus.RECENTLY: return "ʀᴇᴄᴇɴᴛʟʏ ᴀᴄᴛɪᴠᴇ"
        elif u_stat == enums.UserStatus.LAST_WEEK: return "ʟᴀsᴛ ᴡᴇᴇᴋ"
        elif u_stat == enums.UserStatus.LONG_AGO: return "ʟᴏɴɢ ᴛɪᴍᴇ ᴀɢᴏ"
        elif u_stat == enums.UserStatus.OFFLINE: return "ᴏғғʟɪɴᴇ"
        elif u_stat == enums.UserStatus.ONLINE: return "ᴏɴʟɪɴᴇ ɴᴏᴡ"
        else: return "ᴜɴᴋɴᴏᴡɴ"
    except Exception:
        return "ᴜɴᴋɴᴏᴡɴ"

@app.on_message(filters.command(["info", "userinfo"]))
async def display_user_details(client, message: types.Message):
    target_user = None
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target_user = await client.get_users(message.command[1])
        except Exception:
            return await message.reply("❌ **Cᴏᴜʟᴅ ɴᴏᴛ ғɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ.**")
    else:
        target_user = message.from_user

    if not target_user:
        return await message.reply("❌ **Cᴏᴜʟᴅ ɴᴏᴛ ʀᴇᴛʀɪᴇᴠᴇ ᴜsᴇʀ ɪɴғᴏ.**")

    loader = await message.reply("🔄 **Fᴇᴛᴄʜɪɴɢ ᴜsᴇʀ ᴅᴇᴛᴀɪʟs...**")
    
    try:
        full_user = await client.get_chat(target_user.id)
        u_id = target_user.id
        u_name = target_user.first_name + (f" {target_user.last_name}" if target_user.last_name else "")
        u_user = f"@{target_user.username}" if target_user.username else "N/A"
        u_mention = target_user.mention
        u_dc = target_user.dc_id or "N/A"
        u_prem = "✅ ʏᴇs" if getattr(target_user, "is_premium", False) else "❌ ɴᴏ"
        
        raw_bio = full_user.bio or ""
        if not raw_bio:
            u_bio = "ɴᴏ ʙɪᴏ sᴇᴛ"
        elif re.search(r"(t\.me|https?://|@)", raw_bio, re.IGNORECASE):
            u_bio = "ᴜsᴇʀ ʜᴀs ᴀ ʟɪɴᴋ/ᴜsᴇʀɴᴀᴍᴇ ɪɴ ʙɪᴏ 🪄" if "@" in raw_bio else "ᴜsᴇʀ ʜᴀs ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ 🌐"
        else:
            u_bio = raw_bio

        try:
            m_chats = await client.get_common_chats(target_user.id)
            u_mutual = len(m_chats)
        except Exception:
            u_mutual = "ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"

        u_join = getattr(target_user, "added_to_attachment_menu_date", None)
        u_join_str = u_join.strftime("%d %b %Y") if u_join else "ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
        u_stat = await get_user_status(target_user.id)

        final_cap = INFO_TEXT_LAYOUT.format(u_id, u_name, u_user, u_mention, u_dc, u_prem, u_bio, u_mutual, u_join_str, u_stat)
        
        btn_markup = InlineKeyboardMarkup([[types.InlineKeyboardButton("🌐 ᴠɪᴇᴡ ᴘʀᴏғɪʟᴇ", url=f"tg://user?id={u_id}")]])

        if full_user.photo:
            photo_path = await client.download_media(full_user.photo.big_file_id)
            await message.reply_photo(photo=photo_path, caption=final_cap, reply_markup=btn_markup)
            import os; os.remove(photo_path)
        else:
            await message.reply_text(text=final_cap, reply_markup=btn_markup, disable_web_page_preview=True)
            
        await loader.delete()
    except Exception as e:
        await loader.edit(f"❌ **Eʀʀᴏʀ:** {e}")