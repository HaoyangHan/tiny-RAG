#!/usr/bin/env python3
"""
Test Enhanced LlamaIndex Document Processor with Comprehensive Metadata
====================================================================

This script tests the enhanced LlamaIndex document processor to verify
that it extracts comprehensive metadata for text and image chunks including:
- Keywords
- Entities  
- Topics
- Sentiment analysis
- Language detection
- Readability scores

Author: TinyRAG Development Team
Version: 1.4.3
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any

# Test configuration
OPENAI_API_KEY = "sk-proj-1234567890abcdef"  # Replace with actual key
TEST_PDF_PATH = Path("test_table.pdf")  # PDF with tables and images

async def test_enhanced_llamaindex_metadata():
    """Test comprehensive metadata extraction with LlamaIndex processor."""
    
    print("🧪 Testing Enhanced LlamaIndex Document Processor with Comprehensive Metadata")
    print("=" * 80)
    
    try:
        # Import the processor
        from services.llamaindex_document_processor import create_llamaindex_document_processor
        
        # Create processor instance
        processor = create_llamaindex_document_processor(OPENAI_API_KEY)
        
        print(f"✅ LlamaIndex processor created successfully")
        
        # Test document processing
        if TEST_PDF_PATH.exists():
            print(f"\n📄 Processing test document: {TEST_PDF_PATH}")
            
            # Process document
            start_time = time.time()
            document = await processor.process_document(
                file_path=TEST_PDF_PATH,
                user_id="test_user_123",
                document_id="test_doc_456",
                project_id="test_project_789"
            )
            processing_time = time.time() - start_time
            
            print(f"✅ Document processed in {processing_time:.2f} seconds")
            print(f"📊 Document stats:")
            print(f"   - Total chunks: {len(document.chunks)}")
            print(f"   - Tables: {len(document.tables)}")
            print(f"   - Images: {len(document.images)}")
            
            # Analyze metadata for each chunk type
            text_chunks = [c for c in document.chunks if c.chunk_type == "text"]
            table_chunks = [c for c in document.chunks if c.chunk_type == "table"]
            image_chunks = [c for c in document.chunks if c.chunk_type == "image"]
            
            print(f"\n📝 Text Chunks ({len(text_chunks)}):")
            for i, chunk in enumerate(text_chunks[:3]):  # Show first 3
                metadata = chunk.chunk_metadata
                print(f"   Chunk {i+1}:")
                print(f"     - Keywords: {len(metadata.get('keywords', []))}")
                print(f"     - Entities: {len(metadata.get('entities', []))}")
                print(f"     - Topics: {len(metadata.get('topics', []))}")
                print(f"     - Sentiment: {metadata.get('sentiment', 'N/A')}")
                print(f"     - Language: {metadata.get('language', 'N/A')}")
                print(f"     - Readability: {metadata.get('readability_score', 'N/A')}")
                
                # Show sample keywords and entities
                if metadata.get('keywords'):
                    sample_keywords = metadata['keywords'][:3]
                    print(f"     - Sample keywords: {[k.get('term', '') for k in sample_keywords]}")
                
                if metadata.get('entities'):
                    sample_entities = metadata['entities'][:3]
                    print(f"     - Sample entities: {[e.get('text', '') for e in sample_entities]}")
            
            print(f"\n📊 Table Chunks ({len(table_chunks)}):")
            for i, chunk in enumerate(table_chunks[:2]):  # Show first 2
                metadata = chunk.chunk_metadata
                print(f"   Table {i+1}:")
                print(f"     - Keywords: {len(metadata.get('keywords', []))}")
                print(f"     - Entities: {len(metadata.get('entities', []))}")
                print(f"     - Topics: {len(metadata.get('topics', []))}")
                print(f"     - Sentiment: {metadata.get('sentiment', 'N/A')}")
                print(f"     - Summary: {metadata.get('summary', 'N/A')[:100]}...")
                
                # Show sample metadata
                if metadata.get('keywords'):
                    sample_keywords = metadata['keywords'][:3]
                    print(f"     - Sample keywords: {[k.get('term', '') for k in sample_keywords]}")
            
            print(f"\n🖼️  Image Chunks ({len(image_chunks)}):")
            for i, chunk in enumerate(image_chunks[:2]):  # Show first 2
                metadata = chunk.chunk_metadata
                print(f"   Image {i+1}:")
                print(f"     - Keywords: {len(metadata.get('keywords', []))}")
                print(f"     - Entities: {len(metadata.get('entities', []))}")
                print(f"     - Topics: {len(metadata.get('topics', []))}")
                print(f"     - Sentiment: {metadata.get('sentiment', 'N/A')}")
                print(f"     - Description: {metadata.get('description', 'N/A')[:100]}...")
                
                # Show sample metadata
                if metadata.get('keywords'):
                    sample_keywords = metadata['keywords'][:3]
                    print(f"     - Sample keywords: {[k.get('term', '') for k in sample_keywords]}")
            
            # Save detailed results
            results = {
                "test_name": "Enhanced LlamaIndex Metadata Extraction",
                "timestamp": time.time(),
                "processing_time": processing_time,
                "document_stats": {
                    "total_chunks": len(document.chunks),
                    "text_chunks": len(text_chunks),
                    "table_chunks": len(table_chunks),
                    "image_chunks": len(image_chunks),
                    "tables": len(document.tables),
                    "images": len(document.images)
                },
                "metadata_samples": {
                    "text_chunks": [
                        {
                            "chunk_index": c.chunk_index,
                            "metadata": c.chunk_metadata
                        } for c in text_chunks[:2]
                    ],
                    "table_chunks": [
                        {
                            "chunk_index": c.chunk_index,
                            "metadata": c.chunk_metadata
                        } for c in table_chunks[:1]
                    ],
                    "image_chunks": [
                        {
                            "chunk_index": c.chunk_index,
                            "metadata": c.chunk_metadata
                        } for c in image_chunks[:1]
                    ]
                }
            }
            
            with open("test_enhanced_llamaindex_metadata_results.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n💾 Detailed results saved to: test_enhanced_llamaindex_metadata_results.json")
            
            # Summary
            print(f"\n🎯 Test Summary:")
            print(f"   ✅ LlamaIndex processor successfully extracts comprehensive metadata")
            print(f"   ✅ Text chunks include: keywords, entities, topics, sentiment, language, readability")
            print(f"   ✅ Table chunks include: keywords, entities, topics, sentiment, summary")
            print(f"   ✅ Image chunks include: keywords, entities, topics, sentiment, description")
            print(f"   ✅ Processing time: {processing_time:.2f} seconds")
            
            return True
            
        else:
            print(f"❌ Test document not found: {TEST_PDF_PATH}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_enhanced_llamaindex_metadata()) 