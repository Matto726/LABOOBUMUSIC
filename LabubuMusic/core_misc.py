import socket
import time
import heroku3
from pyrogram import filters

import config
from MattoMusic.core.db_setup import mongodb
from .logger_setup import LOGGER

SUDOERS = filters.user()
HAPP = None
_boot_ = time.time()

def check_if_heroku():
    return "heroku" in socket.getfqdn()

XCB = [
    "/", "@", ".", "com", ":", "git", "heroku", "push",
    str(config.HEROKU_API_KEY), "https", str(config.HEROKU_APP_NAME),
    "HEAD", "master",
]

def initialize_memory_db():
    global db
    db = {}
    LOGGER(__name__).info("Local Memory Database Initialized.")

async def load_sudoers():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    
    sudoers_col = mongodb.sudoers
    sudo_data = await sudoers_col.find_one({"sudo": "sudo"})
    sudo_list = sudo_data["sudoers"] if sudo_data else []
    
    if config.OWNER_ID not in sudo_list:
        sudo_list.append(config.OWNER_ID)
        await sudoers_col.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudo_list}},
            upsert=True,
        )
        
    if sudo_list:
        for uid in sudo_list:
            SUDOERS.add(uid)
            
    LOGGER(__name__).info("Sudoers Data Loaded Successfully.")

def setup_heroku():
    global HAPP
    if check_if_heroku():
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                heroku_client = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = heroku_client.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info("Heroku Application Configured.")
            except BaseException:
                LOGGER(__name__).warning(
                    "Please make sure your Heroku API Key and App name are configured correctly."
                )