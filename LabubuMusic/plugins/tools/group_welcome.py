import os
from unidecode import unidecode
from PIL import ImageDraw, Image, ImageFont, ImageChops
from pyrogram import filters
from pyrogram.types import Message
from MattoMusic import app
from MattoMusic.utils.database import db

try:
    welcome_db = db.welcome
except Exception:
    pass

class MemoryStorage:
    CURRENT = 2
    WELCOME_CACHE = {}

def crop_circle(pfp, output_size=(450, 450)):
    pfp = pfp.resize(output_size, Image.LANCZOS).convert("RGBA")
    large_size = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", large_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + large_size, fill=255)
    mask = mask.resize(pfp.size, Image.LANCZOS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp

def render_welcome_card(user_pic, first_name, chat_title, user_id, username):
    base_bg = Image.open("MattoMusic/assets/welcome2.png")
    user_pic = Image.open(user_pic).convert("RGBA")
    
    rounded_pic = crop_circle(user_pic, (450, 450))
    base_bg.paste(rounded_pic, (425, 203), rounded_pic)
    draw = ImageDraw.Draw(base_bg)
    
    font_bold = ImageFont.truetype("MattoMusic/assets/font.ttf", 60)
    font_reg = ImageFont.truetype("MattoMusic/assets/font.ttf", 75)
    
    first_name = unidecode(first_name)[:20]
    chat_title = unidecode(chat_title)[:22]
    
    draw.text((455, 680), text=first_name, fill="white", font=font_reg)
    draw.text((455, 825), text=f"ID : {user_id}", fill="white", font=font_bold)
    draw.text((455, 900), text=f"@{username}" if username else "No Username", fill="white", font=font_bold)
    
    generated_path = f"downloads/welcome_{user_id}.png"
    base_bg.save(generated_path)
    return generated_path

@app.on_message(filters.new_chat_members & filters.group, group=-1)
async def process_welcome_event(client, message: Message):
    chat_id = message.chat.id
    
    if welcome_db.find_one({"chat_id": chat_id}):
        return

    for new_member in message.new_chat_members:
        if new_member.is_bot or new_member.is_deleted or new_member.is_restricted:
            continue
            
        try:
            dl_pic = await app.download_media(new_member.photo.big_file_id, file_name=f"pp{new_member.id}.png")
        except AttributeError:
            dl_pic = "MattoMusic/assets/upic.png"
            
        cache_key = f"welcome-{chat_id}"
        if cache_key in MemoryStorage.WELCOME_CACHE:
            try: await MemoryStorage.WELCOME_CACHE[cache_key].delete()
            except Exception: pass
            
        try:
            rendered_img = render_welcome_card(dl_pic, new_member.first_name, message.chat.title, new_member.id, new_member.username)
            caption_text = f"""🌟 **Wᴇʟᴄᴏᴍᴇ {new_member.mention}!**\n\n📋 **Gʀᴏᴜᴘ:** {message.chat.title}\n🆔 **Yᴏᴜʀ ɪᴅ:** <code>{new_member.id}</code>\n👤 **Usᴇʀɴᴀᴍᴇ:** @{new_member.username if new_member.username else "Nᴏᴛ sᴇᴛ"}\n\n**Hᴏᴘᴇ ʏᴏᴜ ғɪɴᴅ ɢᴏᴏᴅ ᴠɪʙᴇs ᴀɴᴅ ɴᴇᴡ ғʀɪᴇɴᴅs ʜᴇʀᴇ!** ✨"""
            
            MemoryStorage.WELCOME_CACHE[cache_key] = await app.send_photo(chat_id, photo=rendered_img, caption=caption_text)
        except Exception:
            pass
        finally:
            if dl_pic != "MattoMusic/assets/upic.png" and os.path.exists(dl_pic):
                os.remove(dl_pic)
            if 'rendered_img' in locals() and os.path.exists(rendered_img):
                os.remove(rendered_img)