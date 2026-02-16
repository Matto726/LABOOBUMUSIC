from MattoMusic import app
from MattoMusic.utils.database import get_cmode

async def get_channeplayCB(_, cmd_type, query_obj):
    if cmd_type == "c":
        c_id = await get_cmode(query_obj.message.chat.id)
        if c_id is None:
            try:
                return await query_obj.answer(_["setting_7"], show_alert=True)
            except Exception:
                return
        try:
            c_title = (await app.get_chat(c_id)).title
        except Exception:
            try:
                return await query_obj.answer(_["cplay_4"], show_alert=True)
            except Exception:
                return
    else:
        c_id = query_obj.message.chat.id
        c_title = None
        
    return c_id, c_title