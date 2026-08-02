import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import config

logger = logging.getLogger(__name__)

class InMemoryFallbackDB:
    """In-memory store used if MongoDB service is unavailable."""
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {}

    async def insert_one(self, collection_name: str, document: Dict[str, Any]):
        if collection_name not in self.collections:
            self.collections[collection_name] = []
        document["_id"] = len(self.collections[collection_name]) + 1
        document["created_at"] = datetime.utcnow().isoformat()
        self.collections[collection_name].append(document)
        return document["_id"]

    async def find(self, collection_name: str, query: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        items = self.collections.get(collection_name, [])
        if not query:
            return items[-limit:]
        filtered = []
        for doc in items:
            match = all(doc.get(k) == v for k, v in query.items())
            if match:
                filtered.append(doc)
        return filtered[-limit:]

class MongoDBManager:
    """Async MongoDB database manager with automatic fallback."""
    def __init__(self):
        self.client = None
        self.db = None
        self.is_connected = False
        self.fallback = InMemoryFallbackDB()

    async def connect(self):
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self.client = AsyncIOMotorClient(config.MONGODB_URI, serverSelectionTimeoutMS=2000)
            # Test connection
            await self.client.admin.command('ping')
            self.db = self.client[config.DB_NAME]
            self.is_connected = True
            logger.info(f"Successfully connected to MongoDB at {config.MONGODB_URI}")
        except Exception as e:
            self.is_connected = False
            logger.warning(f"MongoDB not available ({e}). Falling back to in-memory session database.")

    async def save_interaction(self, user_prompt: str, agent_response: str, tools_used: List[str] = None):
        doc = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_prompt": user_prompt,
            "agent_response": agent_response,
            "tools_used": tools_used or []
        }
        if self.is_connected and self.db is not None:
            try:
                await self.db["interactions"].insert_one(doc)
                return
            except Exception as e:
                logger.error(f"Error saving to MongoDB: {e}")
        await self.fallback.insert_one("interactions", doc)

    async def save_memory(self, key: str, value: Any, category: str = "general"):
        doc = {
            "key": key,
            "value": value,
            "category": category,
            "updated_at": datetime.utcnow().isoformat()
        }
        if self.is_connected and self.db is not None:
            try:
                await self.db["memories"].update_one(
                    {"key": key},
                    {"$set": doc},
                    upsert=True
                )
                return
            except Exception as e:
                logger.error(f"Error updating MongoDB memory: {e}")
        await self.fallback.insert_one("memories", doc)

    async def get_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {"category": category} if category else {}
        if self.is_connected and self.db is not None:
            try:
                cursor = self.db["memories"].find(query)
                return await cursor.to_list(length=100)
            except Exception as e:
                logger.error(f"Error fetching from MongoDB memory: {e}")
        return await self.fallback.find("memories", query)

db_manager = MongoDBManager()
