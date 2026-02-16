import re
from pymongo import MongoClient
from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app

URI_PATTERN = re.compile(r"mongodb(?:\+srv)?:\/\/[^\s]+")

@app.on_message(filters.command("mongochk"))
async def verify_mongo_uri(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ᴀғᴛᴇʀ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ:**\n`/mongochk your_mongodb_url`")

    input_uri = message.command[1]
    
    if re.match(URI_PATTERN, input_uri):
        loading_msg = await message.reply("🔄 **ᴛᴇsᴛɪɴɢ ᴄᴏɴɴᴇᴄᴛɪᴏɴ...**")
        try:
            temp_client = MongoClient(input_uri, serverSelectionTimeoutMS=5000)
            temp_client.server_info()
            await loading_msg.edit("✅ **ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ɪs ᴠᴀʟɪᴅ ᴀɴᴅ ᴄᴏɴɴᴇᴄᴛɪᴏɴ sᴜᴄᴇssғᴜʟ!**")
        except Exception as e:
            await loading_msg.edit(f"❌ **ғᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴍᴏɴɢᴏᴅʙ:**\n`{e}`")
    else:
        await message.reply("⚠️ **ᴏᴏᴘs! ʏᴏᴜʀ ᴍᴏɴɢᴏᴅʙ ᴜʀʟ ғᴏʀᴍᴀᴛ ɪs ɪɴᴠᴀʟɪᴅ.**")