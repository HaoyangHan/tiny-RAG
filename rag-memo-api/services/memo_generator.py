from typing import List, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from models.document import Document
from models.memo import Memo, MemoSection
from services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class MemoGenerator:
    """Service for generating memos from processed documents."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the memo generator."""
        self.llm = ChatOpenAI(
            model_name="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        self.document_processor = DocumentProcessor(openai_api_key)

    async def generate_memo(
        self,
        title: str,
        documents: List[Document],
        user_id: str,
        sections: Optional[List[str]] = None
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

            # Generate sections
            if not sections:
                sections = ["Executive Summary", "Key Points", "Detailed Analysis", "Recommendations"]

            for section_title in sections:
                section = await self._generate_section(section_title, documents)
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
        documents: List[Document]
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
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are an expert memo writer. 
                Your task is to write a clear and concise section for a memo based on the provided context.
                Focus on extracting and synthesizing the most relevant information.
                Use proper citations when referencing specific information."""),
                HumanMessage(content=f"""Write the '{section_title}' section for a memo.
                Use the following context to inform your writing:
                
                {context}
                
                Format the section with clear paragraphs and proper citations.""")
            ])

            # Generate section content
            response = await self.llm.ainvoke(prompt)
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
        # This is a simple implementation that looks for citation markers
        # In a production environment, you would want a more sophisticated approach
        citations = []
        for line in content.split("\n"):
            if "[citation:" in line:
                # Extract citation ID from the format [citation:doc_id]
                start = line.find("[citation:") + 11
                end = line.find("]", start)
                if start > 10 and end > start:
                    citation = line[start:end]
                    citations.append(citation)
        return citations 