import random
from os.path import realpath
import aiohttp
from aiohttp import client_exceptions

class CarbonFetchError(Exception):
    pass

CARBON_THEMES = [
    "3024-night", "a11y-dark", "blackboard", "base16-dark", "base16-light",
    "cobalt", "duotone-dark", "dracula-pro", "hopscotch", "lucario",
    "material", "monokai", "nightowl", "nord", "oceanic-next", "one-light",
    "one-dark", "panda-syntax", "parasio-dark", "seti", "shades-of-purple",
    "solarized+dark", "solarized+light", "synthwave-84", "twilight",
    "verminal", "vscode", "yeti", "zenburn",
]

CARBON_COLORS = [
    "#FF0000", "#FF5733", "#FFFF00", "#008000", "#0000FF", "#800080",
    "#A52A2A", "#FF00FF", "#D2B48C", "#00FFFF", "#808000", "#800000",
    "#00FFFF", "#30D5C8", "#00FF00", "#008080", "#4B0082", "#EE82EE",
    "#FFC0CB", "#000000", "#FFFFFF", "#808080",
]

class CarbonCodeAPI:
    def __init__(self):
        self.carbon_config = {
            "language": "auto",
            "dropShadow": True,
            "dropShadowBlurRadius": "68px",
            "dropShadowOffsetY": "20px",
            "fontFamily": "JetBrains Mono",
            "widthAdjustment": True,
            "watermark": False
        }

    async def generate(self, text: str, user_id):
        async with aiohttp.ClientSession(headers={"Content-Type": "application/json"}) as session:
            payload = {
                "code": text,
                "backgroundColor": random.choice(CARBON_COLORS),
                "theme": random.choice(CARBON_THEMES),
                **self.carbon_config
            }
            
            try:
                response = await session.post("https://carbonara.solopov.dev/api/cook", json=payload)
            except client_exceptions.ClientConnectorError:
                raise CarbonFetchError("Host unreachable!")
                
            img_data = await response.read()
            cache_path = f"cache/carbon{user_id}.jpg"
            
            with open(cache_path, "wb") as img_file:
                img_file.write(img_data)
                
            return realpath(img_file.name)