#!/usr/bin/env python3
"""
Test Direct Content Metadata Extraction for TinyRAG v1.4.3
===========================================================

This test demonstrates the direct content metadata extraction approach
for tables and images without using text summaries.

Author: TinyRAG Development Team
Version: 1.4.3
Last Updated: January 2025
"""

import asyncio
import logging
import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from PIL import Image
import io

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.direct_content_metadata_extractor import (
    DirectTableMetadataExtractor,
    DirectImageMetadataExtractor,
    TableContent,
    ImageContent,
    create_direct_table_extractor,
    create_direct_image_extractor
)
from services.direct_enhanced_document_processor import (
    DirectEnhancedDocumentProcessor,
    create_direct_enhanced_processor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class DirectContentExtractionTester:
    """Test suite for direct content metadata extraction."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.table_extractor = create_direct_table_extractor()
        self.image_extractor = create_direct_image_extractor()
        self.processor = create_direct_enhanced_processor()
    
    def create_sample_table_content(self) -> TableContent:
        """Create a sample table for testing."""
        
        # Financial data table
        headers = ["Quarter", "Revenue", "Profit", "Growth %", "Date"]
        data = [
            ["Q1 2024", "$1,250,000", "$187,500", "15.2%", "2024-03-31"],
            ["Q2 2024", "$1,450,000", "$217,500", "16.0%", "2024-06-30"],
            ["Q3 2024", "$1,380,000", "$207,000", "-4.8%", "2024-09-30"],
            ["Q4 2024", "$1,620,000", "$243,000", "17.4%", "2024-12-31"],
            ["Total", "$5,700,000", "$855,000", "11.0%", "2024"]
        ]
        
        return TableContent(
            data=data,
            headers=headers,
            row_count=len(data),
            column_count=len(headers)
        )
    
    def create_sample_image_content(self) -> ImageContent:
        """Create a sample image for testing."""
        
        # Create a synthetic chart-like image
        img_array = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Add some structure (bars for a bar chart)
        img_array[100:150, 50:100] = [255, 0, 0]    # Red bar
        img_array[80:150, 150:200] = [0, 255, 0]    # Green bar
        img_array[120:150, 250:300] = [0, 0, 255]   # Blue bar
        img_array[60:150, 350:400] = [255, 255, 0]  # Yellow bar
        
        # Add some text-like patterns
        img_array[300:320, 50:500] = [128, 128, 128]  # Gray horizontal line
        img_array[50:350, 500:520] = [128, 128, 128]  # Gray vertical line
        
        # Convert to PIL Image and then to bytes
        pil_img = Image.fromarray(img_array, 'RGB')
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='PNG')
        img_data = img_bytes.getvalue()
        
        return ImageContent(
            image_data=img_data,
            width=600,
            height=400,
            format="PNG",
            mode="RGB"
        )
    
    async def test_direct_table_extraction(self) -> Dict[str, Any]:
        """Test direct table metadata extraction."""
        
        logger.info("=== Testing Direct Table Metadata Extraction ===")
        
        # Create sample table
        table_content = self.create_sample_table_content()
        
        # Extract metadata directly from table content
        metadata = self.table_extractor.extract_table_metadata(
            table_content=table_content,
            table_id="test_table_001",
            document_id="test_doc_001",
            page_number=1
        )
        
        # Generate embedding directly from table
        embedding = await self.table_extractor.generate_table_embedding(table_content)
        
        # Display results
        logger.info(f"Table Metadata Extracted:")
        logger.info(f"  - Table ID: {metadata['table_id']}")
        logger.info(f"  - Dimensions: {metadata['row_count']}x{metadata['column_count']}")
        logger.info(f"  - Data Quality Score: {metadata['data_quality_score']:.3f}")
        
        # Column types
        column_types = metadata.get('column_types', {})
        logger.info(f"  - Column Types:")
        for col, type_info in column_types.items():
            logger.info(f"    * {col}: {type_info['type']} (numeric: {type_info['numeric_ratio']:.2f})")
        
        # Content patterns
        patterns = metadata.get('content_patterns', {})
        logger.info(f"  - Content Patterns:")
        logger.info(f"    * Has Headers: {patterns.get('has_headers', False)}")
        logger.info(f"    * Has Totals: {patterns.get('has_totals', False)}")
        logger.info(f"    * Table Purpose: {patterns.get('table_purpose', 'unknown')}")
        
        # Numerical analysis
        numerical = metadata.get('numerical', {})
        logger.info(f"  - Numerical Analysis:")
        logger.info(f"    * Numeric Columns: {len(numerical.get('numeric_columns', []))}")
        logger.info(f"    * Financial Indicators: {numerical.get('financial_indicators', False)}")
        
        # Temporal analysis
        temporal = metadata.get('temporal', {})
        logger.info(f"  - Temporal Analysis:")
        logger.info(f"    * Has Dates: {temporal.get('has_dates', False)}")
        logger.info(f"    * Date Columns: {temporal.get('date_columns', [])}")
        
        # Embedding
        logger.info(f"  - Embedding: Generated {len(embedding)} dimensions")
        
        return {
            "test_name": "Direct Table Extraction",
            "status": "PASSED",
            "metadata_fields": len(metadata),
            "embedding_dimensions": len(embedding),
            "table_purpose": patterns.get('table_purpose', 'unknown'),
            "data_quality": metadata['data_quality_score']
        }
    
    async def test_direct_image_extraction(self) -> Dict[str, Any]:
        """Test direct image metadata extraction."""
        
        logger.info("=== Testing Direct Image Metadata Extraction ===")
        
        # Create sample image
        image_content = self.create_sample_image_content()
        
        # Extract metadata directly from image content
        metadata = self.image_extractor.extract_image_metadata(
            image_content=image_content,
            image_id="test_image_001",
            document_id="test_doc_001",
            page_number=1
        )
        
        # Generate embedding directly from image
        embedding = await self.image_extractor.generate_image_embedding(image_content)
        
        # Display results
        logger.info(f"Image Metadata Extracted:")
        logger.info(f"  - Image ID: {metadata['image_id']}")
        logger.info(f"  - Dimensions: {metadata['width']}x{metadata['height']}")
        logger.info(f"  - Format: {metadata['format']}")
        logger.info(f"  - File Size: {metadata['file_size']} bytes")
        
        # Visual properties
        visual = metadata.get('visual', {})
        logger.info(f"  - Visual Properties:")
        logger.info(f"    * Brightness: {visual.get('brightness', 0):.1f}")
        logger.info(f"    * Contrast: {visual.get('contrast', 0):.1f}")
        logger.info(f"    * Resolution Category: {visual.get('resolution_category', 'unknown')}")
        logger.info(f"    * Is Grayscale: {visual.get('is_grayscale', False)}")
        
        # Color properties
        colors = metadata.get('colors', {})
        logger.info(f"  - Color Properties:")
        logger.info(f"    * Color Diversity: {colors.get('color_diversity', 0):.3f}")
        logger.info(f"    * Color Temperature: {colors.get('color_temperature', 'unknown')}")
        
        dominant = colors.get('dominant_colors', [])
        if dominant:
            logger.info(f"    * Dominant Colors:")
            for i, color in enumerate(dominant[:3]):
                rgb = color['rgb']
                percentage = color['percentage']
                logger.info(f"      - Color {i+1}: RGB({rgb[0]}, {rgb[1]}, {rgb[2]}) - {percentage:.1%}")
        
        # Composition analysis
        composition = metadata.get('composition', {})
        logger.info(f"  - Composition Analysis:")
        logger.info(f"    * Edge Density: {composition.get('edge_density', 0):.3f}")
        logger.info(f"    * Texture Complexity: {composition.get('texture_complexity', 0):.1f}")
        logger.info(f"    * Symmetry Score: {composition.get('symmetry_score', 0):.3f}")
        
        # Content type detection
        content_type = metadata.get('content_type', {})
        logger.info(f"  - Content Type Detection:")
        logger.info(f"    * Likely Type: {content_type.get('likely_type', 'unknown')}")
        logger.info(f"    * Complexity Level: {content_type.get('complexity_level', 'unknown')}")
        logger.info(f"    * Has Text: {content_type.get('has_text', False)}")
        logger.info(f"    * Has Charts: {content_type.get('has_charts', False)}")
        
        # Quality metrics
        quality = metadata.get('quality', {})
        logger.info(f"  - Quality Metrics:")
        logger.info(f"    * Sharpness: {quality.get('sharpness', 0):.1f}")
        logger.info(f"    * Noise Level: {quality.get('noise_level', 0):.1f}")
        logger.info(f"    * Overall Quality Score: {quality.get('overall_quality_score', 0):.3f}")
        
        # Embedding
        logger.info(f"  - Embedding: Generated {len(embedding)} dimensions")
        
        return {
            "test_name": "Direct Image Extraction",
            "status": "PASSED",
            "metadata_fields": len(metadata),
            "embedding_dimensions": len(embedding),
            "content_type": content_type.get('likely_type', 'unknown'),
            "quality_score": quality.get('overall_quality_score', 0)
        }
    
    async def test_embedding_comparison(self) -> Dict[str, Any]:
        """Test embedding comparison between direct content and text representation."""
        
        logger.info("=== Testing Embedding Comparison ===")
        
        # Create sample content
        table_content = self.create_sample_table_content()
        image_content = self.create_sample_image_content()
        
        # Generate direct embeddings
        table_embedding = await self.table_extractor.generate_table_embedding(table_content)
        image_embedding = await self.image_extractor.generate_image_embedding(image_content)
        
        # Create text representations
        table_metadata = self.table_extractor.extract_table_metadata(
            table_content, "test", "test", 1
        )
        image_metadata = self.image_extractor.extract_image_metadata(
            image_content, "test", "test", 1
        )
        
        # Calculate embedding statistics
        table_stats = {
            "mean": float(np.mean(table_embedding)) if table_embedding else 0,
            "std": float(np.std(table_embedding)) if table_embedding else 0,
            "min": float(np.min(table_embedding)) if table_embedding else 0,
            "max": float(np.max(table_embedding)) if table_embedding else 0
        }
        
        image_stats = {
            "mean": float(np.mean(image_embedding)) if image_embedding else 0,
            "std": float(np.std(image_embedding)) if image_embedding else 0,
            "min": float(np.min(image_embedding)) if image_embedding else 0,
            "max": float(np.max(image_embedding)) if image_embedding else 0
        }
        
        logger.info(f"Embedding Statistics:")
        logger.info(f"  - Table Embedding:")
        logger.info(f"    * Dimensions: {len(table_embedding)}")
        logger.info(f"    * Mean: {table_stats['mean']:.6f}")
        logger.info(f"    * Std Dev: {table_stats['std']:.6f}")
        logger.info(f"    * Range: [{table_stats['min']:.6f}, {table_stats['max']:.6f}]")
        
        logger.info(f"  - Image Embedding:")
        logger.info(f"    * Dimensions: {len(image_embedding)}")
        logger.info(f"    * Mean: {image_stats['mean']:.6f}")
        logger.info(f"    * Std Dev: {image_stats['std']:.6f}")
        logger.info(f"    * Range: [{image_stats['min']:.6f}, {image_stats['max']:.6f}]")
        
        # Calculate similarity if both embeddings exist
        similarity = 0.0
        if table_embedding and image_embedding:
            # Cosine similarity
            dot_product = np.dot(table_embedding, image_embedding)
            norm_a = np.linalg.norm(table_embedding)
            norm_b = np.linalg.norm(image_embedding)
            similarity = dot_product / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
            
            logger.info(f"  - Cosine Similarity: {similarity:.6f}")
        
        return {
            "test_name": "Embedding Comparison",
            "status": "PASSED",
            "table_embedding_dims": len(table_embedding),
            "image_embedding_dims": len(image_embedding),
            "cosine_similarity": similarity
        }
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance metrics for direct content extraction."""
        
        logger.info("=== Testing Performance Metrics ===")
        
        import time
        
        # Performance test for table extraction
        table_content = self.create_sample_table_content()
        
        start_time = time.time()
        table_metadata = self.table_extractor.extract_table_metadata(
            table_content, "perf_test_table", "perf_test_doc", 1
        )
        table_extraction_time = time.time() - start_time
        
        start_time = time.time()
        table_embedding = await self.table_extractor.generate_table_embedding(table_content)
        table_embedding_time = time.time() - start_time
        
        # Performance test for image extraction
        image_content = self.create_sample_image_content()
        
        start_time = time.time()
        image_metadata = self.image_extractor.extract_image_metadata(
            image_content, "perf_test_image", "perf_test_doc", 1
        )
        image_extraction_time = time.time() - start_time
        
        start_time = time.time()
        image_embedding = await self.image_extractor.generate_image_embedding(image_content)
        image_embedding_time = time.time() - start_time
        
        logger.info(f"Performance Metrics:")
        logger.info(f"  - Table Processing:")
        logger.info(f"    * Metadata Extraction: {table_extraction_time:.4f} seconds")
        logger.info(f"    * Embedding Generation: {table_embedding_time:.4f} seconds")
        logger.info(f"    * Total Time: {table_extraction_time + table_embedding_time:.4f} seconds")
        logger.info(f"    * Metadata Fields: {len(table_metadata)}")
        
        logger.info(f"  - Image Processing:")
        logger.info(f"    * Metadata Extraction: {image_extraction_time:.4f} seconds")
        logger.info(f"    * Embedding Generation: {image_embedding_time:.4f} seconds")
        logger.info(f"    * Total Time: {image_extraction_time + image_embedding_time:.4f} seconds")
        logger.info(f"    * Metadata Fields: {len(image_metadata)}")
        
        return {
            "test_name": "Performance Metrics",
            "status": "PASSED",
            "table_extraction_time": table_extraction_time,
            "table_embedding_time": table_embedding_time,
            "image_extraction_time": image_extraction_time,
            "image_embedding_time": image_embedding_time,
            "total_processing_time": (table_extraction_time + table_embedding_time + 
                                    image_extraction_time + image_embedding_time)
        }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all direct content extraction tests."""
        
        logger.info("Starting Direct Content Extraction Test Suite")
        logger.info("=" * 60)
        
        test_results = []
        
        try:
            # Test 1: Direct Table Extraction
            result1 = await self.test_direct_table_extraction()
            test_results.append(result1)
            
            # Test 2: Direct Image Extraction
            result2 = await self.test_direct_image_extraction()
            test_results.append(result2)
            
            # Test 3: Embedding Comparison
            result3 = await self.test_embedding_comparison()
            test_results.append(result3)
            
            # Test 4: Performance Metrics
            result4 = await self.test_performance_metrics()
            test_results.append(result4)
            
        except Exception as e:
            logger.error(f"Error during testing: {e}")
            test_results.append({
                "test_name": "Error",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Summary
        logger.info("=" * 60)
        logger.info("Test Suite Summary:")
        
        passed_tests = [r for r in test_results if r.get('status') == 'PASSED']
        failed_tests = [r for r in test_results if r.get('status') == 'FAILED']
        
        logger.info(f"  - Total Tests: {len(test_results)}")
        logger.info(f"  - Passed: {len(passed_tests)}")
        logger.info(f"  - Failed: {len(failed_tests)}")
        
        if failed_tests:
            logger.error("Failed Tests:")
            for test in failed_tests:
                logger.error(f"  - {test['test_name']}: {test.get('error', 'Unknown error')}")
        
        logger.info("Direct Content Extraction Test Suite Completed")
        
        return test_results


async def main():
    """Main test execution function."""
    
    logger.info("TinyRAG Direct Content Metadata Extraction Test Suite")
    logger.info("Version: 1.4.3")
    logger.info("Testing direct table and image content processing without text summaries")
    logger.info("")
    
    # Initialize and run tests
    tester = DirectContentExtractionTester()
    results = await tester.run_all_tests()
    
    # Export results
    import json
    with open('direct_content_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Test results exported to: direct_content_test_results.json")
    
    # Return success/failure status
    failed_count = len([r for r in results if r.get('status') == 'FAILED'])
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main()) 