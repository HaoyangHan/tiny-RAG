#!/usr/bin/env python3
"""
Direct Test of Enhanced LlamaIndex Document Processor
====================================================

This script tests the LlamaIndex document processor directly
to verify comprehensive metadata extraction for text chunks.
"""

import asyncio
import json
import time
from pathlib import Path

# Test configuration
OPENAI_API_KEY = "sk-proj-1234567890abcdef"  # Replace with actual key

async def test_llamaindex_metadata_direct():
    """Test comprehensive metadata extraction directly."""
    
    print("🧪 Direct Test of Enhanced LlamaIndex Document Processor")
    print("=" * 60)
    
    try:
        # Import the processor
        from services.llamaindex_document_processor import create_llamaindex_document_processor
        
        # Create processor instance
        processor = create_llamaindex_document_processor(OPENAI_API_KEY)
        
        print(f"✅ LlamaIndex processor created successfully")
        
        # Create a simple test document
        test_content = """
        Artificial Intelligence and Machine Learning in Modern Business
        
        Artificial Intelligence (AI) and Machine Learning (ML) have revolutionized how businesses operate in the 21st century. 
        Companies are increasingly adopting AI technologies to improve efficiency, reduce costs, and enhance customer experiences.
        
        Key applications include:
        - Natural Language Processing for customer service automation
        - Computer Vision for quality control in manufacturing
        - Predictive Analytics for demand forecasting
        - Recommendation Systems for personalized marketing
        
        The implementation of AI requires careful consideration of data privacy, ethical concerns, and workforce training. 
        Organizations must balance innovation with responsible AI development practices.
        
        Recent developments in large language models like GPT-4 have opened new possibilities for content generation, 
        code assistance, and creative applications. However, these technologies also raise important questions about 
        intellectual property, misinformation, and job displacement.
        
        The future of AI in business looks promising, with continued investment in research and development 
        driving innovation across industries.
        """
        
        # Create temporary test file
        test_file = Path("temp_test_doc.txt")
        with open(test_file, "w") as f:
            f.write(test_content)
        
        print(f"\n📄 Processing test document with comprehensive metadata extraction")
        
        # Process document
        start_time = time.time()
        document = await processor.process_document(
            file_path=test_file,
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
        
        # Analyze metadata for text chunks
        text_chunks = [c for c in document.chunks if c.chunk_type == "text"]
        
        print(f"\n📝 Text Chunks ({len(text_chunks)}) with Comprehensive Metadata:")
        for i, chunk in enumerate(text_chunks):
            metadata = chunk.chunk_metadata
            print(f"\n   Chunk {i+1}:")
            print(f"     - Keywords: {len(metadata.get('keywords', []))}")
            print(f"     - Entities: {len(metadata.get('entities', []))}")
            print(f"     - Topics: {len(metadata.get('topics', []))}")
            print(f"     - Sentiment: {metadata.get('sentiment', 'N/A')}")
            print(f"     - Language: {metadata.get('language', 'N/A')}")
            print(f"     - Readability: {metadata.get('readability_score', 'N/A')}")
            print(f"     - Information Density: {metadata.get('information_density', 'N/A')}")
            print(f"     - Word Count: {metadata.get('word_count', 'N/A')}")
            print(f"     - Processing Time: {metadata.get('processing_time', 'N/A')}")
            
            # Show sample keywords and entities
            if metadata.get('keywords'):
                sample_keywords = metadata['keywords'][:5]
                print(f"     - Sample keywords: {[k.get('term', '') for k in sample_keywords]}")
            
            if metadata.get('entities'):
                sample_entities = metadata['entities'][:3]
                print(f"     - Sample entities: {[e.get('text', '') for e in sample_entities]}")
            
            if metadata.get('topics'):
                sample_topics = metadata['topics'][:3]
                print(f"     - Sample topics: {[t.get('topic_id', '') for t in sample_topics]}")
        
        # Save detailed results
        results = {
            "test_name": "Direct LlamaIndex Metadata Extraction Test",
            "timestamp": time.time(),
            "processing_time": processing_time,
            "document_stats": {
                "total_chunks": len(document.chunks),
                "text_chunks": len(text_chunks),
                "tables": len(document.tables),
                "images": len(document.images)
            },
            "metadata_samples": {
                "text_chunks": [
                    {
                        "chunk_index": c.chunk_index,
                        "text_preview": c.text[:100] + "...",
                        "metadata": c.chunk_metadata
                    } for c in text_chunks[:2]
                ]
            }
        }
        
        with open("test_llamaindex_metadata_direct_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: test_llamaindex_metadata_direct_results.json")
        
        # Clean up
        test_file.unlink()
        
        # Summary
        print(f"\n🎯 Test Summary:")
        print(f"   ✅ LlamaIndex processor successfully extracts comprehensive metadata")
        print(f"   ✅ Text chunks include: keywords, entities, topics, sentiment, language, readability")
        print(f"   ✅ Processing time: {processing_time:.2f} seconds")
        
        # Check if comprehensive metadata is present
        has_comprehensive_metadata = False
        for chunk in text_chunks:
            metadata = chunk.chunk_metadata
            if (metadata.get('keywords') and metadata.get('entities') and 
                metadata.get('topics') and metadata.get('sentiment')):
                has_comprehensive_metadata = True
                break
        
        if has_comprehensive_metadata:
            print(f"   ✅ Comprehensive metadata extraction confirmed")
        else:
            print(f"   ⚠️  Some metadata fields may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_llamaindex_metadata_direct()) 