import requests
from pyrogram import filters
from pyrogram.types import Message
from MattoMusic import app

@app.on_message(filters.command(["dice", "ludo", "dart", "basket", "basketball", "football", "slot", "bowling", "jackpot"]))
async def play_games(client, message: Message):
    cmd_name = message.command[0]
    
    emoji_map = {
        "dice": "🎲", "ludo": "🎲",
        "dart": "🎯", "basket": "🏀", "basketball": "🏀",
        "football": "⚽", "slot": "🎰", "jackpot": "🎰",
        "bowling": "🎳"
    }
    
    target_emoji = emoji_map.get(cmd_name, "🎲")
    game_response = await client.send_dice(message.chat.id, emoji=target_emoji, reply_to_message_id=message.id)
    await game_response.reply_text(f"ʏᴏᴜʀ sᴄᴏʀᴇ ɪs {game_response.dice.value}")

BORED_API_ENDPOINT = "https://apis.scrimba.com/bored/api/activity"

@app.on_message(filters.command("bored", prefixes="/"))
async def fetch_bored_activity(client, message: Message):
    try:
        api_req = requests.get(BORED_API_ENDPOINT)
        if api_req.status_code == 200:
            resp_json = api_req.json()
            suggested_act = resp_json.get("activity")
            if suggested_act:
                await message.reply(f"𝗙𝗲𝗲𝗹𝗶𝗻𝗴 𝗯𝗼𝗿𝗲𝗱? 𝗛𝗼𝘄 𝗮𝗯𝗼𝘂𝘁:\n\n {suggested_act}")
            else:
                await message.reply("Nᴏ ᴀᴄᴛɪᴠɪᴛʏ ғᴏᴜɴᴅ.")
        else:
            await message.reply("Fᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ᴀᴄᴛɪᴠɪᴛʏ.")
    except Exception:
        await message.reply("Eʀʀᴏʀ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ API.")

__MODULE__ = "Eɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ"
__HELP__ = """
**ʜᴀᴠɪɴɢ ꜰᴜɴ:**

• `/dice` / `/ludo`: Rᴏʟʟs ᴀ ᴅɪᴄᴇ.
• `/dart`: Pʟᴀʏs ᴅᴀʀᴛs.
• `/basket` / `/basketball`: Tʜʀᴏᴡs ᴀ ʙᴀsᴋᴇᴛʙᴀʟʟ.
• `/football`: Kɪᴄᴋs ᴀ ғᴏᴏᴛʙᴀʟʟ.
• `/slot` / `/jackpot`: Pʟᴀʏs ᴛʜᴇ sʟᴏᴛ ᴍᴀᴄʜɪɴᴇ.
• `/bowling`: Rᴏʟʟs ᴀ ʙᴏᴡʟɪɴɢ ʙᴀʟʟ.
• `/bored`: Sᴜɢɢᴇsᴛs ᴀ ʀᴀɴᴅᴏᴍ ᴀᴄᴛɪᴠɪᴛʏ ᴛᴏ ᴅᴏ.
"""