from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from typing import Optional

from models.document import Document
from models.memo import Memo

logger = logging.getLogger(__name__)

class Database:
    """Database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_to_database(cls, mongodb_url: str, database_name: str):
        """Connect to MongoDB and initialize Beanie."""
        try:
            # Create Motor client
            cls.client = AsyncIOMotorClient(mongodb_url)
            
            # Initialize Beanie with the models
            await init_beanie(
                database=cls.client[database_name],
                document_models=[
                    Document,
                    Memo
                ]
            )
            
            logger.info("Connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_database_connection(cls):
        """Close the database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection") 