from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging
from typing import Optional
import os

from models.document import Document
from models.memo import Memo
from models.element import Element
from models.element_template import ElementTemplate as StandaloneElementTemplate
from models.project import Project
from models.tenant_configuration import TenantConfiguration
from auth.models import User
from models.generation import Generation
from models.evaluation import Evaluation

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """Get MongoDB connection URL from environment or use default."""
    # Check for explicit MongoDB URL first
    if os.getenv("MONGODB_URL"):
        return os.getenv("MONGODB_URL")
    
    # Try to build from individual components
    username = os.getenv("MONGO_ROOT_USERNAME", "admin")
    password = os.getenv("MONGO_ROOT_PASSWORD", "password123")
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    database = os.getenv("MONGO_DATABASE", "tinyrag")
    
    # Try authenticated connection first
    if username and password:
        return f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
    else:
        # Fall back to unauthenticated for local development
        return f"mongodb://{host}:{port}/{database}"

class Database:
    """Database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_to_database(cls, mongodb_url: str, database_name: str):
        """Connect to MongoDB and initialize Beanie."""
        try:
            # Create Motor client
            cls.client = AsyncIOMotorClient(mongodb_url)
            
            # Initialize Beanie with all required models
            await init_beanie(
                database=cls.client[database_name],
                document_models=[
                    Document,
                    Memo,
                    Element,
                    StandaloneElementTemplate,
                    Project,
                    TenantConfiguration,
                    User,
                    Generation,
                    Evaluation
                ]
            )
            
            logger.info("Connected to MongoDB with all models initialized")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_database_connection(cls):
        """Close the database connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection") 