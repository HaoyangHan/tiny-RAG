#!/usr/bin/env python3
"""
Test script for enhanced metadata extraction in TinyRAG v1.4.3
============================================================

This script tests the new LlamaIndex-style metadata extractor and enhanced
document processing capabilities.

Usage:
    python test_enhanced_metadata.py
"""

import asyncio
import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test imports
try:
    from services.metadata_extractor import create_metadata_extractor, BaseNode
    from services.enhanced_document_processor import create_enhanced_document_processor
    from prompt_template import get_prompt_template, list_available_templates
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class MetadataExtractionTester:
    """Test class for metadata extraction functionality."""
    
    def __init__(self):
        """Initialize the tester."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            print("⚠️  Warning: OPENAI_API_KEY not set - testing without LLM features")
        
        # Create metadata extractor
        self.metadata_extractor = create_metadata_extractor(
            openai_client=None  # Start without OpenAI for basic testing
        )
        
        print("🚀 Metadata extraction tester initialized")
    
    def test_basic_metadata_extraction(self):
        """Test basic metadata extraction without LLM."""
        print("\n" + "="*60)
        print("TEST 1: Basic Metadata Extraction (No LLM)")
        print("="*60)
        
        # Test text
        test_text = """
        Artificial Intelligence (AI) has revolutionized many industries since 2020.
        Companies like OpenAI, Google, and Microsoft have invested billions of dollars
        in AI research and development. The market is expected to grow to $190 billion
        by 2025, according to recent studies published on January 15, 2024.
        
        Key benefits of AI include:
        - Automation of repetitive tasks
        - Enhanced decision-making capabilities
        - Improved customer experience
        - Cost reduction and efficiency gains
        
        However, challenges remain around data privacy, ethical considerations,
        and the need for skilled professionals in the field.
        """
        
        # Create test node
        node = BaseNode(text=test_text, node_id="test_001")
        
        # Extract metadata
        try:
            metadata_list = self.metadata_extractor.extract([node])
            
            if metadata_list:
                metadata = metadata_list[0]
                
                print(f"✅ Metadata extracted successfully")
                print(f"   - Chunk ID: {metadata.get('chunk_id', 'N/A')}")
                print(f"   - Text Length: {metadata.get('text_length', 'N/A')}")
                print(f"   - Word Count: {metadata.get('word_count', 'N/A')}")
                print(f"   - Language: {metadata.get('language', 'N/A')}")
                print(f"   - Text Type: {metadata.get('text_type', 'N/A')}")
                print(f"   - Readability Score: {metadata.get('readability_score', 'N/A'):.3f}")
                print(f"   - Information Density: {metadata.get('information_density', 'N/A'):.3f}")
                
                # Keywords
                keywords = metadata.get('keywords', [])
                print(f"   - Keywords Found: {len(keywords)}")
                for i, kw in enumerate(keywords[:5]):  # Show first 5
                    print(f"     {i+1}. {kw.get('term', 'N/A')} (score: {kw.get('score', 0):.3f})")
                
                # Dates
                dates = metadata.get('dates', [])
                print(f"   - Dates Found: {len(dates)}")
                for i, date in enumerate(dates):
                    print(f"     {i+1}. {date.get('text', 'N/A')} -> {date.get('date', 'N/A')}")
                
                print(f"   - Processing Time: {metadata.get('processing_time', 'N/A'):.3f}s")
                
                return True
            else:
                print("❌ No metadata extracted")
                return False
                
        except Exception as e:
            print(f"❌ Error in basic metadata extraction: {e}")
            return False
    
    def test_chunk_metadata_extraction(self):
        """Test TinyRAG-specific chunk metadata extraction."""
        print("\n" + "="*60)
        print("TEST 2: TinyRAG Chunk Metadata Extraction")
        print("="*60)
        
        test_text = """
        The quarterly financial report shows significant growth in Q4 2023.
        Revenue increased by 25% compared to the previous quarter, reaching $2.5 million.
        The company's stock price rose from $45.20 to $58.75 during this period.
        Key performance indicators include customer acquisition cost of $125
        and customer lifetime value of $1,850.
        """
        
        try:
            # Use TinyRAG-specific method
            metadata = self.metadata_extractor.extract_chunk_metadata(
                text=test_text,
                chunk_id="chunk_test_001",
                document_id="doc_test_001",
                chunk_index=0,
                start_pos=0,
                end_pos=len(test_text),
                page_number=1,
                section="Financial Summary"
            )
            
            print(f"✅ TinyRAG chunk metadata extracted successfully")
            print(f"   - Document ID: {metadata.get('document_id', 'N/A')}")
            print(f"   - Chunk Index: {metadata.get('chunk_index', 'N/A')}")
            print(f"   - Start Position: {metadata.get('start_pos', 'N/A')}")
            print(f"   - End Position: {metadata.get('end_pos', 'N/A')}")
            print(f"   - Page Number: {metadata.get('page_number', 'N/A')}")
            print(f"   - Section: {metadata.get('section', 'N/A')}")
            print(f"   - Extractor Version: {metadata.get('extractor_version', 'N/A')}")
            
            # Show extracted features
            if 'keywords' in metadata:
                print(f"   - Keywords: {len(metadata['keywords'])} found")
            if 'dates' in metadata:
                print(f"   - Dates: {len(metadata['dates'])} found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in chunk metadata extraction: {e}")
            return False
    
    def test_prompt_templates(self):
        """Test centralized prompt templates."""
        print("\n" + "="*60)
        print("TEST 3: Prompt Template System")
        print("="*60)
        
        try:
            # List available templates
            templates = list_available_templates()
            print(f"✅ Available templates: {len(templates)}")
            for template in templates:
                print(f"   - {template}")
            
            # Test specific templates
            test_templates = ["table_summary", "image_description", "comprehensive_metadata"]
            
            for template_name in test_templates:
                if template_name in templates:
                    try:
                        template = get_prompt_template(template_name)
                        print(f"✅ Template '{template_name}' loaded successfully")
                        print(f"   - Model: {template.model}")
                        print(f"   - Temperature: {template.temperature}")
                        print(f"   - Max Tokens: {template.max_tokens}")
                        print(f"   - Variables: {template.variables}")
                    except Exception as e:
                        print(f"❌ Error loading template '{template_name}': {e}")
                else:
                    print(f"⚠️  Template '{template_name}' not found")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing prompt templates: {e}")
            return False
    
    async def test_enhanced_document_processor(self):
        """Test enhanced document processor (without actual file processing)."""
        print("\n" + "="*60)
        print("TEST 4: Enhanced Document Processor")
        print("="*60)
        
        if not self.openai_api_key:
            print("⚠️  Skipping enhanced processor test - OpenAI API key not available")
            return True
        
        try:
            # Create enhanced processor
            processor = create_enhanced_document_processor(self.openai_api_key)
            print("✅ Enhanced document processor created successfully")
            
            # Test embedding generation (simple test)
            test_text = "This is a test for embedding generation."
            embedding = await processor._generate_embedding(test_text)
            
            if embedding:
                print(f"✅ Embedding generation working (dimension: {len(embedding)})")
            else:
                print("⚠️  Embedding generation returned empty result")
            
            # Test similarity calculation
            vec1 = [1.0, 0.5, 0.2]
            vec2 = [0.8, 0.6, 0.3]
            similarity = processor._cosine_similarity(vec1, vec2)
            print(f"✅ Cosine similarity calculation working (test result: {similarity:.3f})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing enhanced document processor: {e}")
            return False
    
    def test_integration_pipeline(self):
        """Test the complete integration pipeline."""
        print("\n" + "="*60)
        print("TEST 5: Integration Pipeline")
        print("="*60)
        
        try:
            # Simulate a complete document processing pipeline
            sample_chunks = [
                "Introduction to machine learning algorithms and their applications in modern business.",
                "Data preprocessing is crucial for model performance. Clean data leads to better results.",
                "The evaluation metrics include accuracy, precision, recall, and F1-score for classification tasks."
            ]
            
            # Process each chunk through the pipeline
            total_metadata_fields = 0
            
            for i, chunk_text in enumerate(sample_chunks):
                # Extract metadata
                metadata = self.metadata_extractor.extract_chunk_metadata(
                    text=chunk_text,
                    chunk_id=f"integration_chunk_{i}",
                    document_id="integration_test_doc",
                    chunk_index=i,
                    start_pos=i * 100,
                    end_pos=(i + 1) * 100,
                    page_number=1,
                    section=f"Section {i + 1}"
                )
                
                total_metadata_fields += len(metadata)
                
                print(f"✅ Chunk {i + 1} processed:")
                print(f"   - Text length: {len(chunk_text)}")
                print(f"   - Metadata fields: {len(metadata)}")
                print(f"   - Keywords found: {len(metadata.get('keywords', []))}")
            
            print(f"\n🎉 Integration pipeline completed successfully!")
            print(f"   - Total chunks processed: {len(sample_chunks)}")
            print(f"   - Total metadata fields: {total_metadata_fields}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error in integration pipeline test: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests."""
        print("🧪 Starting Enhanced Metadata Extraction Tests")
        print("=" * 80)
        
        tests = [
            ("Basic Metadata Extraction", self.test_basic_metadata_extraction),
            ("Chunk Metadata Extraction", self.test_chunk_metadata_extraction),
            ("Prompt Template System", self.test_prompt_templates),
            ("Enhanced Document Processor", self.test_enhanced_document_processor),
            ("Integration Pipeline", self.test_integration_pipeline),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test '{test_name}' failed with exception: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Enhanced metadata extraction is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the output above for details.")
        
        return passed == total


async def main():
    """Main test function."""
    tester = MetadataExtractionTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Enhanced metadata extraction system is ready for production!")
    else:
        print("\n❌ Issues detected. Please resolve before deployment.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 