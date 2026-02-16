from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)
from py_yt import VideosSearch
from MattoMusic import app
from MattoMusic.utils.inlinequery import answer
from config import BANNED_USERS

@app.on_inline_query(~BANNED_USERS)
async def yt_inline_search(client, query):
    search_term = query.query.strip().lower()
    results_list = []
    
    if not search_term:
        try:
            return await client.answer_inline_query(query.id, results=answer, cache_time=10)
        except Exception:
            return
            
    yt_client = VideosSearch(search_term, limit=20)
    fetched_data = (await yt_client.next()).get("result")
    
    for idx in range(min(15, len(fetched_data))):
        v_title = (fetched_data[idx]["title"]).title()
        v_dur = fetched_data[idx]["duration"]
        v_views = fetched_data[idx]["viewCount"]["short"]
        v_thumb = fetched_data[idx]["thumbnails"][0]["url"].split("?")[0]
        c_link = fetched_data[idx]["channel"]["link"]
        c_name = fetched_data[idx]["channel"]["name"]
        v_link = fetched_data[idx]["link"]
        v_pub = fetched_data[idx]["publishedTime"]
        
        desc_text = f"{v_views} | {v_dur} ᴍɪɴᴜᴛᴇs | {c_name} | {v_pub}"
        btn_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="ʏᴏᴜᴛᴜʙᴇ 🎄", url=v_link)]])
        
        res_text = f"""
❄ <b>ᴛɪᴛʟᴇ :</b> <a href={v_link}>{v_title}</a>

⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {v_dur} ᴍɪɴᴜᴛᴇs
👀 <b>ᴠɪᴇᴡs :</b> <code>{v_views}</code>
🎥 <b>ᴄʜᴀɴɴᴇʟ :</b> <a href={c_link}>{c_name}</a>
⏰ <b>ᴘᴜʙʟɪsʜᴇᴅ ᴏɴ :</b> {v_pub}

<u><b>➻ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴍᴏᴅᴇ ʙʏ {app.name}</b></u>"""

        results_list.append(
            InlineQueryResultPhoto(
                photo_url=v_thumb,
                title=v_title,
                thumb_url=v_thumb,
                description=desc_text,
                caption=res_text,
                reply_markup=btn_markup,
            )
        )
        
    try:
        await client.answer_inline_query(query.id, results=results_list)
    except Exception:
        pass