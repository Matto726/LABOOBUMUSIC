from motor.motor_asyncio import AsyncIOMotorClient
import config
from ..logging import LOGGER

LOGGER(__name__).info("Initializing MongoDB Connection...")

try:
    _mongo_client_ = AsyncIOMotorClient(config.MONGO_DB_URI)
    mongodb = _mongo_client_.Matto
    LOGGER(__name__).info("MongoDB Connection Established Successfully.")
except Exception as e:
    LOGGER(__name__).error(f"Critical Error: Failed to connect to MongoDB Database. {e}")
    exit(1)