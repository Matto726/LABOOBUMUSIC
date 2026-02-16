from typing import Dict, List
from MattoMusic.core.db_setup import mongodb

db_queries = mongodb.queries
db_userstats = mongodb.userstats
db_chatstats = mongodb.chatstats
db_auth_users = mongodb.authuser
db_global_bans = mongodb.gban
db_sudo_users = mongodb.sudoers
db_chat_cache = mongodb.chats
db_blacklisted_chats = mongodb.blacklistChat
db_telegram_users = mongodb.tgusersdb
db_playlists = mongodb.playlist
db_blocked_list = mongodb.blockedusers
db_private_cache = mongodb.privatechats
db_deployments = mongodb.deployments

global_playlist_cache = []

async def fetch_playlist_data(c_id: int) -> Dict[str, int]:
    record = await db_playlists.find_one({"chat_id": c_id})
    return record["notes"] if record else {}

async def fetch_playlist_keys(c_id: int) -> List[str]:
    keys = []
    record = await db_playlists.find_one({"chat_id": c_id})
    if not record:
        return keys
    for key in record["notes"]:
        keys.append(key)
    return keys

async def get_playlist_item(c_id: int, item_name: str):
    item_name = item_name.lower().strip()
    pl_data = await fetch_playlist_data(c_id)
    if item_name in pl_data:
        return pl_data[item_name]
    return False

async def insert_playlist_item(c_id: int, item_name: str, item_details: dict):
    item_name = item_name.lower().strip()
    pl_data = await fetch_playlist_data(c_id)
    pl_data[item_name] = item_details
    await db_playlists.update_one(
        {"chat_id": c_id}, {"$set": {"notes": pl_data}}, upsert=True
    )

async def remove_playlist_item(c_id: int, item_name: str) -> bool:
    item_name = item_name.lower().strip()
    pl_data = await fetch_playlist_data(c_id)
    if item_name in pl_data:
        del pl_data[item_name]
        await db_playlists.update_one(
            {"chat_id": c_id}, {"$set": {"notes": pl_data}}, upsert=True
        )
        return True
    return False

async def register_deployment(u_id: int, app_id: str):
    record = await db_deployments.find_one({"_id": u_id})
    if record:
        app_list = record.get("apps", [])
        if app_id not in app_list:
            app_list.append(app_id)
        await db_deployments.update_one({"_id": u_id}, {"$set": {"apps": app_list}})
    else:
        await db_deployments.insert_one({"_id": u_id, "apps": [app_id]})

async def retrieve_deployments(u_id: int):
    record = await db_deployments.find_one({"_id": u_id})
    return record.get("apps", []) if record else []

async def unregister_deployment(u_id: int, app_id: str):
    record = await db_deployments.find_one({"_id": u_id})
    if record:
        app_list = record.get("apps", [])
        if app_id in app_list:
            app_list.remove(app_id)
            await db_deployments.update_one({"_id": u_id}, {"$set": {"apps": app_list}})
            return True
    return False