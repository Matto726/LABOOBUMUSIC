from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from MattoMusic import app
import requests
import os

@app.on_message(filters.command("vid"))
async def fetch_video_dl(_, message: Message):
    if len(message.command) < 2: return await message.reply_text("❌ Please provide a video URL.\n\nExample:\n/vid Any_video_url")
    vid_target = message.text.split(None, 1)[1]
    status_msg = await message.reply("🔍 Fetching video...")

    dl_payload = {"url": vid_target, "token": "c99f113fab0762d216b4545e5c3d615eefb30f0975fe107caab629d17e51b52d"}
    req_headers = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Linux; Android 14)"}

    try:
        api_res = requests.post("https://allvideodownloader.cc/wp-json/aio-dl/video-data/", data=dl_payload, headers=req_headers)
        res_data = api_res.json()

        if "medias" not in res_data or not res_data["medias"]: return await status_msg.edit("❌ No downloadable video found.")

        highest_res_video = sorted(res_data["medias"], key=lambda x: x.get("quality", ""), reverse=True)[0]
        video_target_link = highest_res_video["url"]

        await status_msg.edit("⬇️ Downloading video...")
        temp_file = "video.mp4"
        
        with requests.get(video_target_link, stream=True) as stream_req:
            with open(temp_file, "wb") as disk_file:
                for chunk in stream_req.iter_content(chunk_size=8192): disk_file.write(chunk)

        await app.send_video(chat_id=message.chat.id, video=temp_file, caption=f"🎬 {res_data.get('title', 'Video')}\n\n✅ ", supports_streaming=True)
        await status_msg.delete()
        os.remove(temp_file)
    except Exception as err:
        await status_msg.edit(f"❌ Error: {str(err)}")

REPO_VIDEO_LINK = "https://files.catbox.moe/aoafwn.mp4"

@app.on_message(filters.command(["repo", "source"]))
async def display_repo(_, message: Message):
    await message.reply_video(
        video=REPO_VIDEO_LINK,
        caption=(
            "<b>✨ ʜᴇʏ ᴅᴇᴀʀ, ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ᴏꜰꜰɪᴄɪᴀʟ ʀᴇᴘᴏꜱɪᴛᴏʀʏ ᴏꜰ ᴛʜɪꜱ ʙᴏᴛ ✨</b>\n\n"
            "🔗 ᴏɴ'ᴛ ꜰᴏʀɢᴇᴛ ᴛᴏ ɢɪᴠᴇ ᴀ ꜱᴛᴀʀ 🌟 ᴀɴᴅ ꜰᴏʟʟᴏᴡ!\n\n"
            "🧡 ᴄʀᴇᴅɪᴛꜱ : <a href='https://t.me/laboobusupportbot'>@laboobusupportbot</a>"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📂 Management Bot", url="https://github.com/Matto726/LabubuMusic"), InlineKeyboardButton("📂 Music Bot", url="https://github.com/Matto726/LabubuMusic")]
        ]),
        supports_streaming=True,
        has_spoiler=True,
    )