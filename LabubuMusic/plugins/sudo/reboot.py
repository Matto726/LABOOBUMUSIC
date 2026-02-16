import asyncio
import os
import shutil
import socket
from datetime import datetime
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters

import config
from MattoMusic import app
from MattoMusic.misc import HAPP, SUDOERS, XCB
from MattoMusic.utils.database import get_active_chats, remove_active_chat, remove_active_video_chat
from MattoMusic.utils.decorators.language import language
from MattoMusic.utils.pastebin import SamarBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def check_heroku():
    return "heroku" in socket.getfqdn()

@app.on_message(filters.command(["getlog", "logs", "getlogs"]) & SUDOERS)
@language
async def fetch_logs(client, message, _):
    try: await message.reply_document(document="log.txt")
    except Exception: await message.reply_text(_["server_1"])

@app.on_message(filters.command(["update", "gitpull"]) & SUDOERS)
@language
async def pull_updates(client, message, _):
    if await check_heroku() and HAPP is None:
        return await message.reply_text(_["server_2"])
        
    status_msg = await message.reply_text(_["server_3"])
    
    try: git_repo = Repo()
    except GitCommandError: return await status_msg.edit(_["server_4"])
    except InvalidGitRepositoryError: return await status_msg.edit(_["server_5"])
    
    os.system(f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null")
    await asyncio.sleep(7)
    
    v_check = ""
    origin_repo = git_repo.remotes.origin.url.split(".git")[0]
    
    for cm_info in git_repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        v_check = str(cm_info.count())
    if not v_check:
        return await status_msg.edit(_["server_6"])
        
    update_log = ""
    def ordinal_fmt(val): return "%d%s" % (val, "tsnrhtdd"[(val // 10 % 10 != 1) * (val % 10 < 4) * val % 10 :: 4])
    
    for c_data in git_repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"):
        c_date = datetime.fromtimestamp(c_data.committed_date)
        update_log += f"<b>➣ #{c_data.count()}: <a href={origin_repo}/commit/{c_data}>{c_data.summary}</a> ʙʏ -> {c_data.author}</b>\n\t\t\t\t<b>➥ ᴄᴏᴍᴍɪᴛᴇᴅ ᴏɴ :</b> {ordinal_fmt(int(c_date.strftime('%d')))} {c_date.strftime('%b')}, {c_date.strftime('%Y')}\n\n"
        
    head_txt = "<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n<b><u>ᴜᴩᴅᴀᴛᴇs:</u></b>\n\n"
    complete_txt = head_txt + update_log
    
    if len(complete_txt) > 4096:
        log_url = await SamarBin(update_log)
        render_msg = await status_msg.edit(f"<b>ᴀ ɴᴇᴡ ᴜᴩᴅᴀᴛᴇ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ !</b>\n\n➣ ᴩᴜsʜɪɴɢ ᴜᴩᴅᴀᴛᴇs ɴᴏᴡ\n\n<u><b>ᴜᴩᴅᴀᴛᴇs :</b></u>\n\n<a href={log_url}>ᴄʜᴇᴄᴋ ᴜᴩᴅᴀᴛᴇs</a>")
    else:
        render_msg = await status_msg.edit(complete_txt, disable_web_page_preview=True)
        
    os.system("git stash &> /dev/null && git pull")

    try:
        active_c_ids = await get_active_chats()
        for c_id in active_c_ids:
            try:
                await app.send_message(chat_id=int(c_id), text=_["server_8"].format(app.mention))
                await remove_active_chat(c_id)
                await remove_active_video_chat(c_id)
            except Exception: pass
        await status_msg.edit(f"{render_msg.text}\n\n{_['server_7']}")
    except Exception: pass

    if await check_heroku():
        try:
            os.system(f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}")
            return
        except Exception as err:
            await status_msg.edit(f"{render_msg.text}\n\n{_['server_9']}")
            return await app.send_message(chat_id=config.LOG_GROUP_ID, text=_["server_10"].format(err))
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()

@app.on_message(filters.command(["restart"]) & SUDOERS)
async def reboot_bot(client, message):
    status_msg = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    active_c_ids = await get_active_chats()
    
    for c_id in active_c_ids:
        try:
            await app.send_message(
                chat_id=int(c_id),
                text=f"{app.mention} ɪs ʀᴇsᴛᴀʀᴛɪɴɢ...\n\nʏᴏᴜ ᴄᴀɴ sᴛᴀʀᴛ ᴩʟᴀʏɪɴɢ ᴀɢᴀɪɴ ᴀғᴛᴇʀ 15-20 sᴇᴄᴏɴᴅs.",
            )
            await remove_active_chat(c_id)
            await remove_active_video_chat(c_id)
        except Exception: pass

    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except Exception: pass
    
    await status_msg.edit_text("» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs...")
    os.system(f"kill -9 {os.getpid()} && bash start")