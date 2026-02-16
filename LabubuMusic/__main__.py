import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall

import config
from MattoMusic import LOGGER, app, userbot
from MattoMusic.core.stream_call import Samar
from MattoMusic.core_misc import load_sudoers
from MattoMusic.plugins import ALL_MODULES
from MattoMusic.utils.database import get_banned_users
from config import BANNED_USERS

MENU_COMMANDS = [
    BotCommand("start", "❖ sᴛᴀʀᴛ ʙᴏᴛ • ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
    BotCommand("help", "❖ ʜᴇʟᴘ ᴍᴇɴᴜ • ɢᴇᴛ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴀɴᴅ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ"),
    BotCommand("ping", "❖ ᴘɪɴɢ • ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛᴜs ᴀɴᴅ ʟᴀᴛᴇɴᴄʏ"),
    BotCommand("stats", "❖ sᴛᴀᴛs • ɢᴇᴛ ʙᴏᴛ's ɢʟᴏʙᴀʟ sᴛᴀᴛɪsᴛɪᴄs"),
    BotCommand("play", "❖ ᴘʟᴀʏ • ᴘʟᴀʏ ᴀ ᴍᴜsɪᴄ/ᴠɪᴅᴇᴏ ᴛʀᴀᴄᴋ"),
    BotCommand("skip", "❖ sᴋɪᴘ • sᴋɪᴘ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ"),
    BotCommand("pause", "❖ ᴘᴀᴜsᴇ • ᴘᴀᴜsᴇ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ"),
    BotCommand("resume", "❖ ʀᴇsᴜᴍᴇ • ʀᴇsᴜᴍᴇ ᴛʜᴇ ᴘʟᴀʏʙᴀᴄᴋ"),
    BotCommand("end", "❖ ᴇɴᴅ • sᴛᴏᴘ ᴘʟᴀʏʙᴀᴄᴋ ᴀɴᴅ ʟᴇᴀᴠᴇ ᴠᴄ"),
    BotCommand("shuffle", "❖ sʜᴜғғʟᴇ • ʀᴀɴᴅᴏᴍɪᴢᴇ ᴛʜᴇ ǫᴜᴇᴜᴇ"),
    BotCommand("loop", "❖ ʟᴏᴏᴘ • ʀᴇᴘᴇᴀᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴛʀᴀᴄᴋ"),
    BotCommand("queue", "❖ ǫᴜᴇᴜᴇ • sʜᴏᴡ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘʟᴀʏʟɪsᴛ"),
    BotCommand("settings", "❖ sᴇᴛᴛɪɴɢs • ᴄᴏɴғɪɢᴜʀᴇ ʙᴏᴛ sᴇᴛᴛɪɴɢs")
]

async def configure_bot_commands():
    try:
        await app.set_bot_commands(MENU_COMMANDS)
    except Exception as e:
        LOGGER("MattoMusic.Main").warning(f"Could not configure commands: {e}")

async def boot_matto_music():
    await load_sudoers()
    
    try:
        banned_list = await get_banned_users()
        for uid in banned_list:
            BANNED_USERS.add(uid)
    except Exception:
        pass
        
    await app.start()
    await configure_bot_commands()

    for module_name in ALL_MODULES:
        importlib.import_module("MattoMusic.plugins" + module_name)

    LOGGER("MattoMusic.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Samar.start()

    try:
        await Samar.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("MattoMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit(1)
    except Exception:
        pass

    await Samar.decorators()

    LOGGER("MattoMusic").info(
        "MattoMusic Started Successfully.\n\n"
        "Created with ❤️ for @Laboobubots."
    )
    
    await idle()
    
    await app.stop()
    await userbot.stop()
    LOGGER("MattoMusic").info("Stopping MattoMusic Bot...")

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(boot_matto_music())