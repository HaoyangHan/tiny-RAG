# Metadata Extraction & Document Processing

**TinyRAG Knowledge Base** | Last Updated: June 25, 2025

---

## Overview

TinyRAG's metadata extraction system is a sophisticated pipeline that transforms raw documents into searchable, contextually-rich data structures. This guide explains how documents are processed, chunked, and enhanced with metadata to enable powerful RAG workflows.

## 🔄 Document Processing Pipeline

### 1. **Document Ingestion**

When a document is uploaded through the API (`POST /documents/upload`), it enters the processing pipeline:

```python
# Document upload flow
document = Document(
    filename="research_paper.pdf",
    content_type="application/pdf",
    project_id=project_id,
    status=DocumentStatus.PROCESSING
)
```

**Supported Formats:**
- PDF documents (.pdf)
- Microsoft Word (.docx)
- Plain text (.txt)
- Markdown (.md)

### 2. **Content Extraction**

Different parsers handle each document type:

#### PDF Processing
```python
# PDF text extraction with PyMuPDF
import fitz  # PyMuPDF

def extract_pdf_content(file_path):
    doc = fitz.open(file_path)
    pages = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text()
        
        # Extract page-level metadata
        page_info = {
            "page_number": page_num + 1,
            "text": text,
            "metadata": {
                "bbox": page.rect,
                "rotation": page.rotation,
                "images": len(page.get_images()),
                "tables": detect_tables(page)
            }
        }
        pages.append(page_info)
    
    return pages
```

#### DOCX Processing
```python
# DOCX processing with python-docx
from docx import Document

def extract_docx_content(file_path):
    doc = Document(file_path)
    content = []
    
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            content.append({
                "text": paragraph.text,
                "style": paragraph.style.name,
                "metadata": {
                    "alignment": paragraph.alignment,
                    "indent": paragraph.paragraph_format.left_indent
                }
            })
    
    return content
```

### 3. **Text Preprocessing**

Raw text undergoes several preprocessing steps:

```python
def preprocess_text(text: str) -> str:
    """Clean and normalize text content."""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR errors
    text = fix_ocr_errors(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove control characters
    text = ''.join(char for char in text if char.isprintable())
    
    return text.strip()
```

## 🧩 Intelligent Chunking

### Chunking Strategies

TinyRAG employs multiple chunking strategies based on document type and content:

#### 1. **Semantic Chunking**
```python
def semantic_chunking(text: str, max_chunk_size: int = 1000) -> List[Chunk]:
    """Split text based on semantic boundaries."""
    
    # Use sentence boundaries
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # Check if adding sentence exceeds limit
        if len(current_chunk) + len(sentence) > max_chunk_size:
            if current_chunk:
                chunks.append(create_chunk(current_chunk))
                current_chunk = sentence
            else:
                # Handle very long sentences
                chunks.extend(split_long_sentence(sentence, max_chunk_size))
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk:
        chunks.append(create_chunk(current_chunk))
    
    return chunks
```

#### 2. **Hierarchical Chunking**
```python
def hierarchical_chunking(document: Document) -> List[Chunk]:
    """Create chunks with hierarchical context."""
    
    chunks = []
    
    for section in document.sections:
        # Create section-level chunk
        section_chunk = Chunk(
            text=section.title + "\n" + section.content,
            metadata={
                "chunk_type": "section",
                "section_title": section.title,
                "section_level": section.level,
                "subsections": [s.title for s in section.subsections]
            }
        )
        chunks.append(section_chunk)
        
        # Create smaller sub-chunks for detailed retrieval
        sub_chunks = semantic_chunking(section.content)
        for sub_chunk in sub_chunks:
            sub_chunk.metadata.update({
                "parent_section": section.title,
                "chunk_type": "subsection"
            })
            chunks.append(sub_chunk)
    
    return chunks
```

#### 3. **Sliding Window Chunking**
```python
def sliding_window_chunking(text: str, window_size: int = 500, overlap: int = 50) -> List[Chunk]:
    """Create overlapping chunks for better context preservation."""
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), window_size - overlap):
        chunk_words = words[i:i + window_size]
        chunk_text = " ".join(chunk_words)
        
        chunk = Chunk(
            text=chunk_text,
            metadata={
                "chunk_index": len(chunks),
                "start_word": i,
                "end_word": min(i + window_size, len(words)),
                "overlap_words": overlap if i > 0 else 0
            }
        )
        chunks.append(chunk)
    
    return chunks
```

## 📊 Metadata Enhancement

### Extracting Rich Metadata

Each chunk is enhanced with comprehensive metadata:

```python
class ChunkMetadata:
    """Comprehensive metadata for document chunks."""
    
    # Document-level metadata
    document_id: str
    filename: str
    document_type: str
    upload_date: datetime
    
    # Chunk-level metadata
    chunk_index: int
    page_number: Optional[int]
    section_title: Optional[str]
    chunk_type: str  # paragraph, table, list, header
    
    # Content analysis
    word_count: int
    character_count: int
    language: str
    readability_score: float
    
    # Semantic metadata
    topics: List[str]
    entities: List[Dict[str, Any]]
    keywords: List[str]
    sentiment: Dict[str, float]
    
    # Technical metadata
    embedding_model: str
    embedding_dimension: int
    processing_timestamp: datetime
    quality_score: float
```

### Named Entity Recognition

```python
def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Extract named entities using spaCy."""
    
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
            "confidence": ent._.confidence if hasattr(ent._, 'confidence') else 1.0
        })
    
    return entities
```

### Topic Modeling

```python
def extract_topics(chunks: List[str], num_topics: int = 5) -> List[Dict[str, Any]]:
    """Extract topics using LDA topic modeling."""
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    
    # Vectorize text
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    doc_term_matrix = vectorizer.fit_transform(chunks)
    
    # Fit LDA model
    lda = LatentDirichletAllocation(
        n_components=num_topics,
        random_state=42
    )
    lda.fit(doc_term_matrix)
    
    # Extract topics
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[-10:]]
        topics.append({
            "topic_id": topic_idx,
            "keywords": top_words,
            "weight": topic.max()
        })
    
    return topics
```

## 🔗 Vector Embeddings

### Embedding Generation

TinyRAG generates high-quality embeddings for semantic search:

```python
def generate_embeddings(chunks: List[Chunk]) -> List[Chunk]:
    """Generate embeddings for chunks using OpenAI or local models."""
    
    embedding_model = get_embedding_model()
    
    for chunk in chunks:
        # Prepare text for embedding
        embedding_text = prepare_embedding_text(chunk)
        
        # Generate embedding
        embedding = embedding_model.embed(embedding_text)
        
        # Store embedding with metadata
        chunk.embedding = embedding
        chunk.metadata["embedding_model"] = embedding_model.name
        chunk.metadata["embedding_dimension"] = len(embedding)
        
    return chunks

def prepare_embedding_text(chunk: Chunk) -> str:
    """Prepare text for optimal embedding generation."""
    
    text = chunk.text
    
    # Add context from metadata
    if chunk.metadata.get("section_title"):
        text = f"Section: {chunk.metadata['section_title']}\n{text}"
    
    if chunk.metadata.get("document_title"):
        text = f"Document: {chunk.metadata['document_title']}\n{text}"
    
    # Limit text length for embedding models
    if len(text) > 8000:  # OpenAI ada-002 limit
        text = text[:8000]
    
    return text
```

### Embedding Storage

Embeddings are stored in Qdrant vector database:

```python
def store_embeddings(chunks: List[Chunk], collection_name: str):
    """Store embeddings in Qdrant vector database."""
    
    from qdrant_client import QdrantClient
    
    client = QdrantClient(host="localhost", port=6333)
    
    points = []
    for chunk in chunks:
        point = {
            "id": chunk.id,
            "vector": chunk.embedding,
            "payload": {
                "text": chunk.text,
                "metadata": chunk.metadata,
                "document_id": chunk.document_id,
                "chunk_index": chunk.metadata["chunk_index"]
            }
        }
        points.append(point)
    
    # Batch upload to Qdrant
    client.upsert(
        collection_name=collection_name,
        points=points
    )
```

## 🔍 Quality Control

### Content Quality Assessment

```python
def assess_chunk_quality(chunk: Chunk) -> float:
    """Assess the quality of a processed chunk."""
    
    quality_score = 0.0
    
    # Text length check
    text_length = len(chunk.text)
    if 100 <= text_length <= 2000:
        quality_score += 0.3
    elif text_length > 50:
        quality_score += 0.1
    
    # Language detection confidence
    lang_confidence = detect_language_confidence(chunk.text)
    quality_score += min(lang_confidence, 0.3)
    
    # Readability assessment
    readability = calculate_readability(chunk.text)
    if readability > 0.5:
        quality_score += 0.2
    
    # Entity density (information richness)
    entity_density = len(chunk.metadata.get("entities", [])) / max(len(chunk.text.split()), 1)
    if entity_density > 0.02:
        quality_score += 0.2
    
    return min(quality_score, 1.0)
```

### Error Detection and Handling

```python
def detect_processing_errors(chunk: Chunk) -> List[str]:
    """Detect potential processing errors in chunks."""
    
    errors = []
    
    # Check for excessive special characters (OCR errors)
    special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in chunk.text) / len(chunk.text)
    if special_char_ratio > 0.3:
        errors.append("high_special_character_ratio")
    
    # Check for repeated patterns (scanning artifacts)
    if detect_repeated_patterns(chunk.text):
        errors.append("repeated_patterns")
    
    # Check for incomplete sentences
    if not chunk.text.strip().endswith(('.', '!', '?', ':')):
        errors.append("incomplete_sentence")
    
    # Check for very short chunks
    if len(chunk.text.split()) < 5:
        errors.append("too_short")
    
    return errors
```

## 📈 Performance Optimization

### Parallel Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_document_async(document_path: str) -> Document:
    """Process document with parallel chunk processing."""
    
    # Extract content
    content = await extract_content_async(document_path)
    
    # Create chunks
    chunks = create_chunks(content)
    
    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        loop = asyncio.get_event_loop()
        
        # Parallel metadata extraction
        metadata_tasks = [
            loop.run_in_executor(executor, extract_chunk_metadata, chunk)
            for chunk in chunks
        ]
        
        # Parallel embedding generation
        embedding_tasks = [
            loop.run_in_executor(executor, generate_chunk_embedding, chunk)
            for chunk in chunks
        ]
        
        # Wait for all tasks
        await asyncio.gather(*metadata_tasks, *embedding_tasks)
    
    return Document(chunks=chunks)
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_cached_embedding(text_hash: str) -> Optional[List[float]]:
    """Get cached embedding for text content."""
    
    # Check Redis cache
    cache_key = f"embedding:{text_hash}"
    cached_embedding = redis_client.get(cache_key)
    
    if cached_embedding:
        return json.loads(cached_embedding)
    
    return None

def cache_embedding(text: str, embedding: List[float]):
    """Cache embedding with text hash as key."""
    
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    cache_key = f"embedding:{text_hash}"
    
    # Store in Redis with 30-day expiration
    redis_client.setex(
        cache_key,
        30 * 24 * 3600,  # 30 days
        json.dumps(embedding)
    )
```

## 🔧 Configuration Options

### Processing Configuration

```python
class ProcessingConfig:
    """Configuration for document processing pipeline."""
    
    # Chunking settings
    max_chunk_size: int = 1000
    chunk_overlap: int = 100
    chunking_strategy: str = "semantic"  # semantic, fixed, sliding
    
    # Embedding settings
    embedding_model: str = "text-embedding-ada-002"
    embedding_batch_size: int = 100
    
    # Metadata extraction
    extract_entities: bool = True
    extract_topics: bool = True
    extract_keywords: bool = True
    
    # Quality control
    min_chunk_length: int = 50
    max_chunk_length: int = 2000
    quality_threshold: float = 0.5
    
    # Performance settings
    parallel_processing: bool = True
    max_workers: int = 4
    cache_embeddings: bool = True
```

## 📋 Best Practices

### 1. **Document Preparation**
- Use high-quality source documents
- Ensure consistent formatting
- Remove sensitive information before upload
- Use descriptive filenames

### 2. **Chunking Strategy Selection**
```python
def choose_chunking_strategy(document_type: str, content_length: int) -> str:
    """Choose optimal chunking strategy based on document characteristics."""
    
    if document_type == "academic_paper":
        return "hierarchical"  # Preserve section structure
    elif content_length > 50000:
        return "sliding_window"  # Better for very long documents
    else:
        return "semantic"  # Default for most documents
```

### 3. **Quality Monitoring**
- Monitor chunk quality scores
- Review and improve low-quality chunks
- Track embedding generation success rates
- Monitor retrieval performance

### 4. **Performance Optimization**
- Batch process multiple documents
- Use appropriate chunk sizes for your use case
- Monitor and tune embedding model performance
- Implement proper caching strategies

## 🔍 Debugging and Troubleshooting

### Common Issues

1. **Poor Chunk Quality**
   - Check source document quality
   - Adjust chunking parameters
   - Review preprocessing steps

2. **Slow Processing**
   - Enable parallel processing
   - Optimize chunk sizes
   - Use embedding caching

3. **Missing Metadata**
   - Verify NLP model installation
   - Check entity recognition confidence
   - Review topic modeling parameters

### Monitoring and Logging

```python
import logging

def setup_processing_logging():
    """Configure logging for document processing."""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('document_processing.log'),
            logging.StreamHandler()
        ]
    )
    
    # Log processing metrics
    logger = logging.getLogger(__name__)
    
    def log_processing_metrics(document: Document):
        logger.info(f"Processed document: {document.filename}")
        logger.info(f"Chunks created: {len(document.chunks)}")
        logger.info(f"Average chunk quality: {document.average_quality_score:.2f}")
        logger.info(f"Processing time: {document.processing_time:.2f}s")
```

---

## Next Steps

- **[RAG Pipeline Architecture](rag-pipeline.html)**: Learn how processed documents feed into the RAG system
- **[Element Types Guide](element-types.html)**: Understand how metadata enhances element generation
- **[API Reference](api-reference.html)**: Explore document processing endpoints

**Need Help?** Check the [troubleshooting guide](../troubleshooting/common-issues.html) or [open an issue](https://github.com/tinyrag/tinyrag/issues).

---

*This guide covers TinyRAG v1.4.1 metadata extraction capabilities. For the latest updates, visit our [documentation portal](https://knowledge.tinyrag.com).* 