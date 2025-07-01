from typing import List, Optional
import logging

from models.document import Document
from models.memo import Memo, MemoSection
from services.document_processor import DocumentProcessor
from services.llm_factory import llm_factory, LLMMessage

logger = logging.getLogger(__name__)

class MemoGenerator:
    """Service for generating memos from processed documents."""
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the memo generator."""
        self.model = model  # Will use default if None
        self.document_processor = DocumentProcessor(
            openai_api_key=""  # Not needed anymore, using LLM factory
        )

    async def generate_memo(
        self,
        title: str,
        documents: List[Document],
        user_id: str,
        sections: Optional[List[str]] = None,
        model: Optional[str] = None
    ) -> Memo:
        """Generate a memo from the given documents."""
        try:
            # Create memo instance
            memo = Memo(
                user_id=user_id,
                title=title,
                sections=[],
                document_ids=[doc.id for doc in documents],
                status="processing"
            )
            await memo.save()

            # Use provided model or instance default
            selected_model = model or self.model

            # Generate sections
            if not sections:
                sections = ["Executive Summary", "Key Points", "Detailed Analysis", "Recommendations"]

            for section_title in sections:
                section = await self._generate_section(section_title, documents, selected_model)
                memo.sections.append(section)

            # Update memo status
            memo.status = "completed"
            await memo.save()
            return memo

        except Exception as e:
            logger.error(f"Error generating memo: {str(e)}")
            if memo:
                memo.status = "failed"
                memo.error = str(e)
                await memo.save()
            raise

    async def _generate_section(
        self,
        section_title: str,
        documents: List[Document],
        model: Optional[str] = None
    ) -> MemoSection:
        """Generate a specific section of the memo."""
        try:
            # Collect relevant chunks from all documents
            relevant_chunks = []
            for doc in documents:
                chunks = await self.document_processor.get_similar_chunks(
                    section_title,
                    doc,
                    top_k=3
                )
                relevant_chunks.extend(chunks)

            # Prepare context from chunks
            context = "\n\n".join([chunk.text for chunk in relevant_chunks])
            
            # Create messages for LLM using centralized prompt template
            from prompt_template import format_prompt
            
            prompt_config = format_prompt(
                "memo_section",
                section_title=section_title,
                context=context
            )
            
            messages = [
                LLMMessage(
                    role="system",
                    content=prompt_config["system_prompt"]
                ),
                LLMMessage(
                    role="user",
                    content=prompt_config["user_prompt"]
                )
            ]

            # Generate section content using LLM factory with template config
            response = await llm_factory.generate_response(
                messages=messages,
                model=model or prompt_config["model"],
                temperature=prompt_config["temperature"],
                max_tokens=prompt_config["max_tokens"]
            )
            
            content = response.content

            # Extract citations from the content
            citations = self._extract_citations(content)

            return MemoSection(
                title=section_title,
                content=content,
                citations=citations
            )

        except Exception as e:
            logger.error(f"Error generating section {section_title}: {str(e)}")
            raise

    def _extract_citations(self, content: str) -> List[str]:
        """Extract citations from the generated content."""
        import re
        citations = []
        
        # Find all citation patterns [citation:doc_id]
        citation_pattern = r'\[citation:([^\]]+)\]'
        matches = re.findall(citation_pattern, content)
        
        for match in matches:
            if match not in citations:
                citations.append(match)
        
        return citations 