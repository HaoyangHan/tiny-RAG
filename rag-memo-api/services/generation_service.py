from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import motor.motor_asyncio
import redis.asyncio as redis
from openai import OpenAI

from models.generation import Generation, GenerationMetadata
from .document_service import DocumentService

logger = logging.getLogger(__name__)

class GenerationService:
    """Service for handling generation requests and responses."""
    
    def __init__(self, database: motor.motor_asyncio.AsyncIOMotorDatabase,
                 redis_client: redis.Redis, document_service: DocumentService,
                 enhanced_reranker=None):
        """Initialize the generation service."""
        self.database = database
        self.redis_client = redis_client
        self.document_service = document_service
        self.enhanced_reranker = enhanced_reranker
        
        # Initialize OpenAI client
        import os
        self.openai_client = OpenAI(
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "")
        )
        
    async def create_generation(self, query: str, user_id: str,
                              document_ids: Optional[List[str]] = None,
                              max_tokens: Optional[int] = 1000,
                              temperature: Optional[float] = 0.7,
                              use_enhanced_reranking: bool = False) -> Generation:
        """Create a new generation request and process it immediately."""
        try:
            generation = Generation(
                user_id=user_id,
                query=query,
                document_ids=document_ids or [],
                max_tokens=max_tokens,
                temperature=temperature,
                status="processing"
            )
            
            await generation.save()
            
            # Process the generation immediately for testing
            try:
                await self.process_generation(str(generation.id))
            except Exception as e:
                logger.error(f"Failed to process generation immediately: {e}")
                # Don't fail the creation, let it remain in processing state
            
            return generation
            
        except Exception as e:
            logger.error(f"Error creating generation: {str(e)}")
            raise
    
    async def process_generation(self, generation_id: str) -> Generation:
        """Process a generation request."""
        try:
            generation = await Generation.get(generation_id)
            if not generation:
                raise ValueError("Generation not found")
            
            start_time = datetime.utcnow()
            logger.info(f"Starting generation processing for ID: {generation_id}")
            
            # Step 1: Retrieve relevant documents
            retrieval_start = datetime.utcnow()
            sources = await self.document_service.search_documents(
                user_id=generation.user_id,
                query=generation.query,
                document_ids=generation.document_ids if generation.document_ids else None,
                top_k=10
            )
            retrieval_time = (datetime.utcnow() - retrieval_start).total_seconds()
            logger.info(f"Retrieved {len(sources)} relevant document chunks")
            
            # Step 2: Enhanced reranking if available
            if self.enhanced_reranker and sources:
                try:
                    reranked_sources = await self.enhanced_reranker.rerank(
                        query=generation.query,
                        documents=sources
                    )
                    sources = reranked_sources[:5]  # Top 5 after reranking
                except Exception as e:
                    logger.warning(f"Enhanced reranking failed: {e}")
            
            # Step 3: Generate response
            generation_start = datetime.utcnow()
            
            if sources:
                # Build context from sources
                context = self._build_context(sources)
                logger.info(f"Built context from {len(sources)} sources")
                
                # Generate response using the sources
                response = await self._generate_response(
                    query=generation.query,
                    context=context,
                    max_tokens=generation.max_tokens,
                    temperature=generation.temperature
                )
                
                generation.response = response
                generation.sources = sources
            else:
                generation.response = "I couldn't find any relevant information in the provided documents to answer your question."
                generation.sources = []
            
            generation_time = (datetime.utcnow() - generation_start).total_seconds()
            total_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update metadata
            generation.metadata = GenerationMetadata(
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_documents_searched=len(sources) if sources else 0,
                documents_used=len([s for s in sources if s.get("chunk_text")]) if sources else 0,
                model_name="gpt-4o-mini",
                temperature=generation.temperature,
                max_tokens=generation.max_tokens
            )
            
            generation.status = "completed"
            generation.completed_at = datetime.utcnow()
            
            await generation.save()
            logger.info(f"Generation completed successfully in {total_time:.2f}s")
            return generation
            
        except Exception as e:
            logger.error(f"Error processing generation: {str(e)}")
            
            # Update generation with error
            try:
                generation = await Generation.get(generation_id)
                if generation:
                    generation.status = "failed"
                    generation.error = str(e)
                    await generation.save()
            except:
                pass
            
            raise
    
    async def get_generation(self, generation_id: str, user_id: str) -> Optional[Generation]:
        """Get a generation by ID for a specific user."""
        try:
            generation = await Generation.get(generation_id)
            if generation and generation.user_id == user_id:
                return generation
            return None
            
        except Exception as e:
            logger.error(f"Error getting generation: {str(e)}")
            return None
    
    async def get_user_generation(self, generation_id: str, user_id: str) -> Optional[Generation]:
        """Get a generation by ID for a specific user (alias for get_generation)."""
        return await self.get_generation(generation_id, user_id)
    
    async def list_generations(self, user_id: str, skip: int = 0,
                             limit: int = 20) -> List[Generation]:
        """List generations for a user."""
        try:
            generations = await Generation.find(
                {"user_id": user_id}
            ).sort("-created_at").skip(skip).limit(limit).to_list()
            
            return generations
            
        except Exception as e:
            logger.error(f"Error listing generations: {str(e)}")
            return []
    
    def _build_context(self, sources: List[Dict[str, Any]]) -> str:
        """Build context string from source documents."""
        context_parts = []
        
        for i, source in enumerate(sources):
            chunk_text = source.get('chunk_text', source.get('text', ''))
            doc_title = source.get('document_title', source.get('filename', 'Unknown'))
            
            context_parts.append(
                f"Source {i+1} ({doc_title}):\n"
                f"{chunk_text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    async def _generate_response(self, query: str, context: str,
                               max_tokens: int, temperature: float) -> str:
        """Generate response using OpenAI LLM."""
        try:
            prompt = f"""Based on the following context from documents, please answer the question comprehensively.

Context:
{context}

Question: {query}

Please provide a detailed answer based on the information in the context. If the context doesn't contain enough information to fully answer the question, please indicate what information is missing. Use specific details and examples from the context when possible.

Answer:"""

            logger.info("Calling OpenAI API for response generation")
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document context. Always be accurate and cite specific information from the context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content
            logger.info("Successfully generated response from OpenAI")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {str(e)}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"
    
    async def get_generation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get generation statistics for a user."""
        try:
            total_generations = await Generation.find({"user_id": user_id}).count()
            completed_generations = await Generation.find({
                "user_id": user_id,
                "status": "completed"
            }).count()
            failed_generations = await Generation.find({
                "user_id": user_id,
                "status": "failed"
            }).count()
            
            return {
                "total_generations": total_generations,
                "completed_generations": completed_generations,
                "failed_generations": failed_generations,
                "success_rate": completed_generations / total_generations if total_generations > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting generation stats: {str(e)}")
            return {
                "total_generations": 0,
                "completed_generations": 0,
                "failed_generations": 0,
                "success_rate": 0
            } 