from datetime import datetime, timedelta
import pytz
import os
import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from telegraph import upload_file
from PIL import Image, ImageDraw
import requests

from MattoMusic.utils import get_image, get_couple, save_couple
from MattoMusic import app

def fetch_today_date():
    timezone = pytz.timezone("Asia/Kolkata")
    now = datetime.now(timezone)
    return now.strftime("%d/%m/%Y")

def fetch_tomorrow_date():
    timezone = pytz.timezone("Asia/Kolkata")
    tomorrow = datetime.now(timezone) + timedelta(days=1)
    return tomorrow.strftime("%d/%m/%Y")

def pull_image_from_url(url, dest_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, "wb") as file:
            file.write(response.content)
    return dest_path

target_tomorrow = fetch_tomorrow_date()
target_today = fetch_today_date()

@app.on_message(filters.command(["couple", "couples"]))
async def generate_couple(_, message):
    c_id = message.chat.id
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    profile1_path = "downloads/pfp.png"
    profile2_path = "downloads/pfp1.png"
    gen_image_path = f"downloads/test_{c_id}.png"
    bg_pic_path = "downloads/cppic.png"

    try:
        active_couple = await get_couple(c_id, target_today)
        if not active_couple:
            status_msg = await message.reply_text("❣️")
            user_collection = []

            async for member in app.get_chat_members(message.chat.id, limit=50):
                if not member.user.is_bot and not member.user.is_deleted:
                    user_collection.append(member.user.id)

            u1_id = random.choice(user_collection)
            u2_id = random.choice(user_collection)
            while u1_id == u2_id:
                u1_id = random.choice(user_collection)

            pic1 = (await app.get_chat(u1_id)).photo
            pic2 = (await app.get_chat(u2_id)).photo

            u1_mention = (await app.get_users(u1_id)).mention
            u2_mention = (await app.get_users(u2_id)).mention

            try: dl1 = await app.download_media(pic1.big_file_id, file_name=profile1_path)
            except Exception: dl1 = pull_image_from_url("https://telegra.ph/file/05aa686cf52fc666184bf.jpg", profile1_path)
            
            try: dl2 = await app.download_media(pic2.big_file_id, file_name=profile2_path)
            except Exception: dl2 = pull_image_from_url("https://telegra.ph/file/05aa686cf52fc666184bf.jpg", profile2_path)

            image1 = Image.open(dl1).resize((437, 437))
            image2 = Image.open(dl2).resize((437, 437))

            bg_download = pull_image_from_url("https://telegra.ph/file/96f36504f149e5680741a.jpg", bg_pic_path)
            base_image = Image.open(bg_download)

            m_mask1 = Image.new("L", image1.size, 0)
            m_draw1 = ImageDraw.Draw(m_mask1)
            m_draw1.ellipse((0, 0) + image1.size, fill=255)

            m_mask2 = Image.new("L", image2.size, 0)
            m_draw2 = ImageDraw.Draw(m_mask2)
            m_draw2.ellipse((0, 0) + image2.size, fill=255)

            image1.putalpha(m_mask1)
            image2.putalpha(m_mask2)

            base_image.paste(image1, (116, 160), image1)
            base_image.paste(image2, (789, 160), image2)
            base_image.save(gen_image_path)

            display_txt = f"<b>Tᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ:\n\n{u1_mention} + {u2_mention} = 💚\n\nNᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {target_tomorrow}!!</b>"

            await message.reply_photo(
                gen_image_path, caption=display_txt,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Aᴅᴅ ᴍᴇ 🌋", url=f"https://t.me/{app.username}?startgroup=true")]])
            )
            await status_msg.delete()
            
            tg_upload = upload_file(gen_image_path)
            for item in tg_upload:
                img_link = "https://graph.org/" + item
                stored_couple = {"c1_id": u1_id, "c2_id": u2_id}
                await save_couple(c_id, target_today, stored_couple, img_link)
        else:
            status_msg = await message.reply_text("❣️")
            stored_img = await get_image(c_id)
            u1_id = int(active_couple["c1_id"])
            u2_id = int(active_couple["c2_id"])
            u1_fname = (await app.get_users(u1_id)).first_name
            u2_fname = (await app.get_users(u2_id)).first_name

            display_txt = f"<b>Tᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ 🎉:\n\n[{u1_fname}](tg://openmessage?user_id={u1_id}) + [{u2_fname}](tg://openmessage?user_id={u2_id}) = ❣️\n\nNᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {target_tomorrow}!!</b>"
            await message.reply_photo(
                stored_img, caption=display_txt,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Aᴅᴅ ᴍᴇ🌋", url=f"https://t.me/{app.username}?startgroup=true")]])
            )
            await status_msg.delete()
    except Exception as err:
        print(str(err))
    finally:
        for file in [profile1_path, profile2_path, gen_image_path, bg_pic_path]:
            try: os.remove(file)
            except Exception: pass