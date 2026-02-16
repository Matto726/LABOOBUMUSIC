import asyncio
from pyrogram import enums, filters
from pyrogram.errors import FloodWait

from MattoMusic import app

@app.on_message(filters.command("bots") & filters.group)
async def list_bots(client, message):
    try:
        bot_list = []
        async for target_bot in app.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            bot_list.append(target_bot.user)
            
        bot_count = len(bot_list)
        bot_txt = f"**ʙᴏᴛ ʟɪsᴛ - {message.chat.title}**\n\n🤖 ʙᴏᴛs\n"
        
        while len(bot_list) > 1:
            popped_bot = bot_list.pop(0)
            bot_txt += f"├ @{popped_bot.username}\n"
        else:
            popped_bot = bot_list.pop(0)
            bot_txt += f"└ @{popped_bot.username}\n\n"
            bot_txt += f"**ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ʙᴏᴛs**: {bot_count}**"
            await app.send_message(message.chat.id, bot_txt)
            
    except FloodWait as flood_err:
        await asyncio.sleep(flood_err.value)

__MODULE__ = "Bᴏᴛs"
__HELP__ = """
**ʙᴏᴛs**

• /bots - ɢᴇᴛ ᴀ ʟɪsᴛ ᴏғ ʙᴏᴛs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.
"""