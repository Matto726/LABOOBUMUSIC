import os
from ..logging import LOGGER

def setup_directories():
    allowed_extensions = (".jpg", ".jpeg", ".png")
    
    for item in list(os.listdir()):
        if item.endswith(allowed_extensions):
            os.remove(item)

    required_folders = ["downloads", "cache"]
    for folder in required_folders:
        if folder not in os.listdir():
            os.mkdir(folder)

    LOGGER(__name__).info("System Directories Synced.")