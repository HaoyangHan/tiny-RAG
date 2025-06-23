"""
Main worker module for TinyRAG core library.

This module provides background processing capabilities for document processing,
metadata extraction, and other CPU-intensive tasks.
"""

import asyncio
import logging
import os
import signal
import sys
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoreWorker:
    """Core worker for background processing tasks."""
    
    def __init__(self):
        """Initialize the core worker."""
        self.running = False
        self.tasks = []
        
    async def start(self):
        """Start the worker."""
        logger.info("Starting TinyRAG Core Worker v1.3...")
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Main worker loop
            while self.running:
                await self._process_tasks()
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Worker error: {e}")
        finally:
            await self.stop()
    
    async def _process_tasks(self):
        """Process background tasks."""
        # Placeholder for task processing
        # In a real implementation, this would:
        # 1. Check for new documents to process
        # 2. Extract metadata using LLM
        # 3. Generate embeddings
        # 4. Update search indices
        pass
    
    async def stop(self):
        """Stop the worker."""
        logger.info("Stopping TinyRAG Core Worker...")
        self.running = False
        
        # Cancel running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        logger.info("TinyRAG Core Worker stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False


async def main():
    """Main entry point for the worker."""
    logger.info("TinyRAG Core Library Worker starting...")
    
    # Check environment
    required_env_vars = [
        "MONGODB_URL",
        "REDIS_URL"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Start worker
    worker = CoreWorker()
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker interrupted")
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1) 