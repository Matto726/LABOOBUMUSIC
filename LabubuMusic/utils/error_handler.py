import traceback
from functools import wraps
from pyrogram.errors.exceptions.forbidden_403 import ChatWriteForbidden

from config import LOG_GROUP_ID
from MattoMusic import app

def split_limits(error_text):
    if len(error_text) < 2048:
        return [error_text]

    err_lines = error_text.splitlines(True)
    chunk = ""
    chunk_list = []
    
    for ln in err_lines:
        if len(chunk) + len(ln) < 2048:
            chunk += ln
        else:
            chunk_list.append(chunk)
            chunk = ln

    chunk_list.append(chunk)
    return chunk_list

def capture_err(target_func):
    @wraps(target_func)
    async def error_catcher(client, message, *args, **kwargs):
        try:
            return await target_func(client, message, *args, **kwargs)
        except ChatWriteForbidden:
            await app.leave_chat(message.chat.id)
            return
        except Exception as ex:
            trace_str = traceback.format_exc()
            u_mention = message.from_user.mention if message.from_user else 0
            
            c_info = 0
            if message.chat:
                c_info = f"@{message.chat.username}" if message.chat.username else f"`{message.chat.id}`"
                
            msg_content = message.text or message.caption
            
            err_fmt = "**ERROR** | {} | {}\n```command\n{}```\n\n```python\n{}```\n".format(
                u_mention, c_info, msg_content, "".join(trace_str)
            )
            
            for txt_chunk in split_limits(err_fmt):
                await app.send_message(LOG_GROUP_ID, txt_chunk)
            raise ex

    return error_catcher