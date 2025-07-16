#!/usr/bin/env python3
"""
Test script for enhanced text summary and metadata extraction.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the API directory to the path
sys.path.append(str(Path(__file__).parent / "rag-memo-api"))

from services.enhanced_document_processor import EnhancedDocumentProcessor

async def test_text_summary_metadata():
    """Test text summary and metadata extraction."""
    
    # Sample text for testing
    test_text = """
    Artificial Intelligence and Machine Learning have revolutionized the way we approach problem-solving in the digital age. 
    These technologies enable computers to learn from data, identify patterns, and make decisions with minimal human intervention. 
    
    Key applications include natural language processing, computer vision, and predictive analytics. 
    Companies like Google, Microsoft, and OpenAI are leading the development of advanced AI systems.
    
    The field continues to evolve rapidly, with new breakthroughs in deep learning, neural networks, and large language models.
    """
    
    # Initialize the enhanced document processor
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return
    
    processor = EnhancedDocumentProcessor(openai_api_key)
    
    print("🧪 Testing Text Summary and Metadata Extraction")
    print("=" * 50)
    print(f"Input text length: {len(test_text)} characters")
    print()
    
    try:
        # Test the new text summary with metadata method
        summary, metadata = await processor._generate_text_summary_with_metadata(test_text)
        
        print("✅ Text Summary and Metadata Extraction Successful!")
        print()
        print("📝 Generated Summary:")
        print("-" * 30)
        print(summary)
        print()
        
        print("📊 Extracted Metadata:")
        print("-" * 30)
        print(json.dumps(metadata, indent=2, default=str))
        print()
        
        # Verify key metadata fields
        expected_fields = ["text_type", "key_topics", "key_entities", "sentiment", "complexity", "language", "readability"]
        missing_fields = [field for field in expected_fields if field not in metadata]
        
        if missing_fields:
            print(f"⚠️  Missing metadata fields: {missing_fields}")
        else:
            print("✅ All expected metadata fields present")
            
        print()
        print("🎯 Summary:")
        print(f"- Text type: {metadata.get('text_type', 'N/A')}")
        print(f"- Sentiment: {metadata.get('sentiment', 'N/A')}")
        print(f"- Complexity: {metadata.get('complexity', 'N/A')}")
        print(f"- Language: {metadata.get('language', 'N/A')}")
        print(f"- Readability: {metadata.get('readability', 'N/A')}")
        print(f"- Key topics: {len(metadata.get('key_topics', []))}")
        print(f"- Key entities: {len(metadata.get('key_entities', []))}")
        
    except Exception as e:
        print(f"❌ Error during text summary and metadata extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_text_summary_metadata()) 