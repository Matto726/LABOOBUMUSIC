import asyncio
from typing import List
from MattoMusic.core.db_setup import mongodb

db_auth = mongodb.adminauth
db_authuser = mongodb.authuser
db_autoend = mongodb.autoend
db_autoleave = mongodb.autoleave
db_assistants = mongodb.assistants
db_blacklist_chat = mongodb.blacklistChat
db_blocked = mongodb.blockedusers
db_chats = mongodb.chats
db_single_chat = mongodb.chat
db_channel_mode = mongodb.cplaymode
db_upvote_count = mongodb.upcount
db_gban = mongodb.gban
db_lang = mongodb.language
db_onoff = mongodb.onoffper
db_playmode = mongodb.playmode
db_playtype = mongodb.playtypedb
db_skipmode = mongodb.skipmode
db_sudoers = mongodb.sudoers
db_users = mongodb.tgusersdb

_active_audio_sessions = []
_active_video_sessions = []
_commanders = []

async def fetch_sudoers() -> list:
    sudo_record = await db_sudoers.find_one({"sudo": "sudo"})
    return sudo_record.get("sudoers", []) if sudo_record else []

async def insert_sudo(u_id: int) -> bool:
    current_sudoers = await fetch_sudoers()
    current_sudoers.append(u_id)
    await db_sudoers.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": current_sudoers}}, upsert=True
    )
    return True

async def delete_sudo(u_id: int) -> bool:
    current_sudoers = await fetch_sudoers()
    if u_id in current_sudoers:
        current_sudoers.remove(u_id)
        await db_sudoers.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": current_sudoers}}, upsert=True
        )
    return True

async def fetch_banned_users() -> list:
    banned_list = []
    async for entry in db_blocked.find({"user_id": {"$gt": 0}}):
        banned_list.append(entry["user_id"])
    return banned_list

async def fetch_banned_count() -> int:
    banned_docs = db_blocked.find({"user_id": {"$gt": 0}})
    doc_list = await banned_docs.to_list(length=100000)
    return len(doc_list)

async def check_banned_user(u_id: int) -> bool:
    record = await db_blocked.find_one({"user_id": u_id})
    return bool(record)

async def insert_banned_user(u_id: int):
    if await check_banned_user(u_id):
        return
    return await db_blocked.insert_one({"user_id": u_id})

async def erase_banned_user(u_id: int):
    if not await check_banned_user(u_id):
        return
    return await db_blocked.delete_one({"user_id": u_id})