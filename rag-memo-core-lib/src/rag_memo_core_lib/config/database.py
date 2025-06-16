"""Database configuration for RAG Memo Core Library."""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import redis.asyncio as redis
from loguru import logger

from .settings import CoreSettings


class DatabaseConfig:
    """Database configuration and connection management.
    
    This class handles MongoDB and Redis connections for the RAG Memo platform,
    providing async connection management and initialization.
    """
    
    def __init__(self, settings: CoreSettings):
        """Initialize database configuration.
        
        Args:
            settings: Core settings instance
        """
        self.settings = settings
        self.mongodb_client: Optional[AsyncIOMotorClient] = None
        self.redis_client: Optional[redis.Redis] = None
        self._mongodb_database = None
    
    async def connect_mongodb(self) -> AsyncIOMotorClient:
        """Connect to MongoDB and initialize Beanie ODM.
        
        Returns:
            MongoDB client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Create MongoDB client
            self.mongodb_client = AsyncIOMotorClient(
                self.settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                maxPoolSize=10,
                minPoolSize=1,
            )
            
            # Test connection
            await self.mongodb_client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.settings.MONGODB_URL}")
            
            # Get database
            self._mongodb_database = self.mongodb_client[self.settings.MONGODB_DB_NAME]
            
            # Initialize Beanie ODM with document models
            await self._init_beanie()
            
            return self.mongodb_client
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"MongoDB connection failed: {e}")
    
    async def connect_redis(self) -> redis.Redis:
        """Connect to Redis for caching and task queue.
        
        Returns:
            Redis client instance
            
        Raises:
            ConnectionError: If connection fails
        """
        try:
            # Create Redis client
            self.redis_client = redis.from_url(
                self.settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info(f"Connected to Redis: {self.settings.REDIS_URL}")
            
            return self.redis_client
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ConnectionError(f"Redis connection failed: {e}")
    
    async def disconnect_mongodb(self) -> None:
        """Disconnect from MongoDB."""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info("Disconnected from MongoDB")
    
    async def disconnect_redis(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def disconnect_all(self) -> None:
        """Disconnect from all databases."""
        await self.disconnect_mongodb()
        await self.disconnect_redis()
    
    def get_mongodb_database(self):
        """Get MongoDB database instance.
        
        Returns:
            MongoDB database instance
            
        Raises:
            RuntimeError: If not connected to MongoDB
        """
        if not self._mongodb_database:
            raise RuntimeError("Not connected to MongoDB. Call connect_mongodb() first.")
        return self._mongodb_database
    
    def get_redis_client(self) -> redis.Redis:
        """Get Redis client instance.
        
        Returns:
            Redis client instance
            
        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect_redis() first.")
        return self.redis_client
    
    async def _init_beanie(self) -> None:
        """Initialize Beanie ODM with document models."""
        try:
            # Import document models
            from ..models.document import Document
            from ..models.generation import Generation
            from ..models.project import Project
            from ..models.user import User
            from ..models.evaluation import Evaluation
            
            # Initialize Beanie
            await init_beanie(
                database=self._mongodb_database,
                document_models=[
                    Document,
                    Generation,
                    Project,
                    User,
                    Evaluation,
                ]
            )
            
            logger.info("Beanie ODM initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Beanie ODM: {e}")
            raise
    
    async def create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        try:
            db = self.get_mongodb_database()
            
            # Document indexes
            await db.documents.create_index([("filename", 1)])
            await db.documents.create_index([("created_at", -1)])
            await db.documents.create_index([("status", 1)])
            await db.documents.create_index([("project_id", 1)])
            
            # Generation indexes
            await db.generations.create_index([("document_id", 1)])
            await db.generations.create_index([("created_at", -1)])
            await db.generations.create_index([("status", 1)])
            await db.generations.create_index([("model", 1)])
            
            # Project indexes
            await db.projects.create_index([("name", 1)])
            await db.projects.create_index([("created_at", -1)])
            await db.projects.create_index([("user_id", 1)])
            
            # User indexes
            await db.users.create_index([("email", 1)], unique=True)
            await db.users.create_index([("username", 1)], unique=True)
            
            # Evaluation indexes
            await db.evaluations.create_index([("generation_id", 1)])
            await db.evaluations.create_index([("created_at", -1)])
            await db.evaluations.create_index([("metric_type", 1)])
            
            # Vector search index (if using MongoDB Atlas)
            if "atlas" in self.settings.MONGODB_URL.lower():
                await self._create_vector_search_index(db)
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database indexes: {e}")
            raise
    
    async def _create_vector_search_index(self, db) -> None:
        """Create vector search index for MongoDB Atlas.
        
        Args:
            db: MongoDB database instance
        """
        try:
            # Vector search index for document embeddings
            vector_index = {
                "name": "document_embeddings_index",
                "type": "vectorSearch",
                "definition": {
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": 1536,  # text-embedding-3-small
                            "similarity": "cosine"
                        },
                        {
                            "type": "filter",
                            "path": "document_id"
                        },
                        {
                            "type": "filter",
                            "path": "chunk_index"
                        }
                    ]
                }
            }
            
            # Create the index (this would typically be done via Atlas UI or CLI)
            logger.info("Vector search index configuration prepared for MongoDB Atlas")
            
        except Exception as e:
            logger.warning(f"Vector search index creation skipped: {e}")
    
    async def health_check(self) -> dict:
        """Perform health check on all database connections.
        
        Returns:
            Health status dictionary
        """
        health_status = {
            "mongodb": {"status": "unknown", "error": None},
            "redis": {"status": "unknown", "error": None}
        }
        
        # Check MongoDB
        try:
            if self.mongodb_client:
                await self.mongodb_client.admin.command('ping')
                health_status["mongodb"]["status"] = "healthy"
            else:
                health_status["mongodb"]["status"] = "disconnected"
        except Exception as e:
            health_status["mongodb"]["status"] = "unhealthy"
            health_status["mongodb"]["error"] = str(e)
        
        # Check Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"]["status"] = "healthy"
            else:
                health_status["redis"]["status"] = "disconnected"
        except Exception as e:
            health_status["redis"]["status"] = "unhealthy"
            health_status["redis"]["error"] = str(e)
        
        return health_status 