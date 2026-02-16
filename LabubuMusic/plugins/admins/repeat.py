from pyrogram import filters
from pyrogram.types import Message

from MattoMusic import app
from MattoMusic.utils.database import get_loop, set_loop
from MattoMusic.utils.decorators import AdminRightsCheck
from MattoMusic.utils.inline import close_markup
from config import BANNED_USERS

@app.on_message(filters.command(["loop", "cloop"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def set_repeat_mode(cli, message: Message, _, chat_id):
    help_usage = _["admin_17"]
    if len(message.command) != 2:
        return await message.reply_text(help_usage)
        
    loop_val = message.text.split(None, 1)[1].strip()
    
    if loop_val.isnumeric():
        loop_val = int(loop_val)
        if 1 <= loop_val <= 10:
            current_loop = await get_loop(chat_id)
            if current_loop != 0:
                loop_val += current_loop
            if loop_val > 10:
                loop_val = 10
                
            await set_loop(chat_id, loop_val)
            return await message.reply_text(
                text=_["admin_18"].format(loop_val, message.from_user.mention),
                reply_markup=close_markup(_),
            )
        else:
            return await message.reply_text(_["admin_17"])
            
    elif loop_val.lower() == "enable":
        await set_loop(chat_id, 10)
        return await message.reply_text(
            text=_["admin_18"].format(loop_val, message.from_user.mention),
            reply_markup=close_markup(_),
        )
        
    elif loop_val.lower() == "disable":
        await set_loop(chat_id, 0)
        return await message.reply_text(
            _["admin_19"].format(message.from_user.mention),
            reply_markup=close_markup(_),
        )
        
    else:
        return await message.reply_text(help_usage)