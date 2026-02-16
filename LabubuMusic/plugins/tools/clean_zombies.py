import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait

from MattoMusic import app
from MattoMusic.utils.permissions import adminsOnly

ongoing_zombie_cleans = []
halt_zombie_cleanup = False

@app.on_message(filters.command(["zombies"]))
@adminsOnly("can_restrict_members")
async def clear_deleted_accounts(client, message):
    global halt_zombie_cleanup
    chat_id = message.chat.id
    
    try:
        try:
            requesting_admin = await app.get_chat_member(chat_id, message.from_user.id)
            admin_privileges = requesting_admin.privileges
        except BaseException:
            admin_privileges = message.sender_chat
            
        if admin_privileges:
            bot_status = await app.get_chat_member(chat_id, "self")
            if bot_status.status == ChatMemberStatus.MEMBER:
                await message.reply("➠ | ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs.")
            else:
                if len(ongoing_zombie_cleans) > 30:
                    await message.reply("➠ | ɪ'ᴍ ᴀʟʀᴇᴀᴅʏ ᴡᴏʀᴋɪɴɢ ᴏɴ ᴍʏ ᴍᴀxɪᴍᴜᴍ ɴᴜᴍʙᴇʀ ᴏғ 30 ᴄʜᴀᴛs ᴀᴛ ᴛʜᴇ ᴍᴏᴍᴇɴᴛ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ sʜᴏʀᴛʟʏ.")
                elif chat_id in ongoing_zombie_cleans:
                    await message.reply("➠ | ᴛʜᴇʀᴇ's ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴏɴɢɪɪɴɢ ᴘʀᴏᴄᴇss ɪɴ ᴛʜɪs ᴄʜᴀᴛ. ᴘʟᴇᴀsᴇ [ /stop ] ᴛᴏ sᴛᴀʀᴛ ᴀ ɴᴇᴡ ᴏɴᴇ.")
                else:
                    ongoing_zombie_cleans.append(chat_id)
                    ghost_accounts = []
                    
                    async for member in app.get_chat_members(chat_id):
                        if member.user.is_deleted:
                            ghost_accounts.append(member.user)
                            
                    ghost_count = len(ghost_accounts)
                    if ghost_count == 0:
                        await message.reply("⟳ | ɴᴏ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.")
                        ongoing_zombie_cleans.remove(chat_id)
                    else:
                        cleared = 0
                        eta_seconds = ghost_count * 1
                        status_alert = await app.send_message(
                            chat_id,
                            f"🧭 | ᴛᴏᴛᴀʟ ᴏғ {ghost_count} ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ʜᴀs ʙᴇᴇɴ ᴅᴇᴛᴇᴄᴛᴇᴅ.\n🥀 | ᴇsᴛɪᴍᴀᴛᴇᴅ ᴛɪᴍᴇ: {eta_seconds} sᴇᴄᴏɴᴅs ғʀᴏᴍ ɴᴏᴡ.",
                        )
                        
                        if halt_zombie_cleanup:
                            halt_zombie_cleanup = False
                            
                        while len(ghost_accounts) > 0 and not halt_zombie_cleanup:
                            target_ghost = ghost_accounts.pop(0)
                            try:
                                await app.ban_chat_member(chat_id, target_ghost.id)
                            except FloodWait as flood_err:
                                await asyncio.sleep(flood_err.value)
                            except Exception:
                                pass
                            cleared += 1
                            
                        if cleared == ghost_count:
                            await message.reply("✅ | sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ᴀʟʟ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄɪᴜɴᴛs ғʀᴏᴍ ᴛʜɪs ᴄʜᴀᴛ.")
                        else:
                            await message.reply(f"✅ | sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ {cleared} ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ғʀᴏᴍ ᴛʜɪs ᴄʜᴀᴛ.")
                            
                        await status_alert.delete()
                        ongoing_zombie_cleans.remove(chat_id)
        else:
            await message.reply("👮🏻 | sᴏʀʀʏ, **ᴏɴʟʏ ᴀᴅᴍɪɴ** ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    except FloodWait as flood_err:
        await asyncio.sleep(flood_err.value)


__MODULE__ = "Zᴏᴍʙɪᴇs"
__HELP__ = """
**Commands:**
- /zombies: ʀᴇᴍᴏᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ.

**Info:**
- ᴍᴏᴅᴜʟᴇ ɴᴀᴍᴇ: ʀᴇᴍᴏᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs
- ᴅᴇsᴄʀɪᴘᴛɪᴏɴ: ʀᴇᴍᴏᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ.
- ᴄᴏᴍᴍᴀɴᴅs: /zombies
- ᴘᴇʀᴍɪssɪᴏɴs ɴᴇᴇᴅᴇᴅ: ᴄᴀɴ ʀᴇsᴛʀɪᴄᴛ ᴍᴇᴍʙᴇʀs

**Note:**
- ᴜsᴇ ᴅɪʀᴇᴄᴛʟʏ ɪɴ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡɪᴛʜ ᴍᴇ ғᴏʀ ʙᴇsᴛ ᴇғғᴇᴄᴛ. ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.
"""