from MattoMusic.core.client_bot import SamarClient
from MattoMusic.core.folder_utils import setup_directories
from MattoMusic.core.repo_manager import update_repo
from MattoMusic.core.assistant_bot import SamarUserbot
from MattoMusic.core_misc import initialize_memory_db, setup_heroku
from .logger_setup import LOGGER

setup_directories()
update_repo()
initialize_memory_db()
setup_heroku()

app = SamarClient()
userbot = SamarUserbot()

from .platforms import *

Apple = AppleMusicAPI()
Carbon = CarbonCodeAPI()
SoundCloud = SoundCloudAPI()
Spotify = SpotifyMusicAPI()
Resso = RessoMusicAPI()
Telegram = TelegramCoreAPI()
YouTube = YouTubeCoreAPI()