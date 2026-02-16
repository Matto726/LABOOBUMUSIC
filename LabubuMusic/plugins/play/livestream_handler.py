from pyrogram import filters

from MattoMusic import YouTube, app
from MattoMusic.utils.channelplay import get_channeplayCB
from MattoMusic.utils.decorators.language import languageCB
from MattoMusic.utils.stream.stream import stream
from config import BANNED_USERS

@app.on_callback_query(filters.regex("LiveStream") & ~BANNED_USERS)
@languageCB
async def process_live_stream_cb(client, query, _):
    cb_data = query.data.strip().split(None, 1)[1]
    vid_id, u_id, mode, c_play, f_play = cb_data.split("|")
    
    if query.from_user.id != int(u_id):
        try: return await query.answer(_["playcb_1"], show_alert=True)
        except Exception: return
        
    try:
        target_chat_id, target_channel = await get_channeplayCB(_, c_play, query)
    except Exception:
        return
        
    is_video = True if mode == "v" else None
    initiator_name = query.from_user.first_name
    
    await query.message.delete()
    try: await query.answer()
    except Exception: pass
    
    status_msg = await query.message.reply_text(
        _["play_2"].format(target_channel) if target_channel else _["play_1"]
    )
    
    try:
        track_details, track_uid = await YouTube.track(vid_id, True)
    except Exception:
        return await status_msg.edit_text(_["play_3"])
        
    is_force_play = True if f_play == "f" else None
    
    if not track_details.get("duration_min"):
        try:
            await stream(
                _, status_msg, u_id, track_details, target_chat_id,
                initiator_name, query.message.chat.id, is_video,
                streamtype="live", forceplay=is_force_play,
            )
        except Exception as err:
            err_type = type(err).__name__
            err_msg = err if err_type == "AssistantErr" else _["general_2"].format(err_type)
            return await status_msg.edit_text(err_msg)
    else:
        return await status_msg.edit_text("» ɴᴏᴛ ᴀ ʟɪᴠᴇ sᴛʀᴇᴀᴍ.")
        
    await status_msg.delete()