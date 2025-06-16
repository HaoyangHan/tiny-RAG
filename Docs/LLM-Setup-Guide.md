# TinyRAG v1.1 - LLM Setup and Usage Guide

## Overview

TinyRAG v1.1 introduces enhanced LLM capabilities with support for multiple AI providers:
- **Google Gemini**: Advanced reasoning and multimodal understanding
- **OpenAI**: Fast and reliable text generation

## Supported Models

### Google Gemini Models
- **gemini-2.0-flash-lite** (Default) - Cost-efficient with low latency
- **gemini-2.5-pro-preview-06-05** - Enhanced thinking and reasoning capabilities
- **gemini-2.5-flash-preview-05-20** - Adaptive thinking with cost efficiency

### OpenAI Models
- **gpt-4-mini-2025-04-16** (Default) - Fast and cost-effective
- **gpt-4.1-nano-2025-04-14** - Ultra-fast responses

## Environment Setup

### 1. API Keys Configuration

Create a `.env` file in your `rag-memo-api` directory with the following variables:

```env
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tinyrag

# Redis Settings
REDIS_URL=redis://localhost:6379

# LLM API Keys
OPENAI_API_KEY=sk-xxxxxxxx
GEMINI_API_KEY=sk-xxxxxxxx

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key

# Application Settings
DEBUG=False
API_V1_STR=/api/v1
PROJECT_NAME=TinyRAG
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### 2. API Endpoints

Both OpenAI and Gemini APIs are configured to use the proxy endpoint:
- **OpenAI**: `https://api.openai-proxy.org/v1`
- **Gemini**: `https://api.openai-proxy.org/google`

This configuration is handled automatically by the LLM factory.

## Usage Examples

### 1. Basic Memo Generation

```python
from services.llm_factory import llm_factory, LLMMessage

# Create messages
messages = [
    LLMMessage(role="system", content="You are a helpful assistant."),
    LLMMessage(role="user", content="Summarize this document...")
]

# Generate response with default model (Gemini 2.0 Flash Lite)
response = await llm_factory.generate_response(messages)
print(response.content)
```

### 2. Using Specific Models

```python
# Use OpenAI GPT-4 Mini
response = await llm_factory.generate_response(
    messages=messages,
    model="gpt-4-mini-2025-04-16"
)

# Use Gemini Pro for complex reasoning
response = await llm_factory.generate_response(
    messages=messages,
    model="gemini-2.5-pro-preview-06-05"
)
```

### 3. API Endpoints

#### Get Available Models
```http
GET /api/v1/memos/models
```

Response:
```json
{
  "models": {
    "openai": ["gpt-4-mini-2025-04-16", "gpt-4.1-nano-2025-04-14"],
    "gemini": ["gemini-2.0-flash-lite", "gemini-2.5-pro-preview-06-05", "gemini-2.5-flash-preview-05-20"]
  },
  "default_model": "gemini-2.0-flash-lite",
  "model_info": {
    "openai": {
      "gpt-4-mini-2025-04-16": "GPT-4 Mini - Fast and cost-effective",
      "gpt-4.1-nano-2025-04-14": "GPT-4.1 Nano - Ultra-fast responses"
    },
    "gemini": {
      "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite - Default, balanced performance",
      "gemini-2.5-pro-preview-06-05": "Gemini 2.5 Pro Preview - Advanced reasoning",
      "gemini-2.5-flash-preview-05-20": "Gemini 2.5 Flash Preview - Fast with thinking"
    }
  }
}
```

#### Create Memo with Specific Model
```http
POST /api/v1/memos/
Content-Type: application/json

{
  "title": "Project Analysis",
  "document_ids": ["doc1", "doc2"],
  "sections": ["Executive Summary", "Key Findings"],
  "model": "gemini-2.5-pro-preview-06-05"
}
```

## Model Selection Guidelines

### When to Use Gemini Models

**Gemini 2.0 Flash Lite (Default)**
- General-purpose memo generation
- Cost-sensitive applications
- Fast processing requirements

**Gemini 2.5 Pro Preview**
- Complex document analysis
- Advanced reasoning tasks
- Multi-step problem solving

**Gemini 2.5 Flash Preview**
- Tasks requiring adaptive thinking
- Balance between speed and intelligence
- Creative content generation

### When to Use OpenAI Models

**GPT-4 Mini**
- Consistent, reliable outputs
- Well-structured content
- Standard business documents

**GPT-4.1 Nano**
- Ultra-fast responses needed
- Simple summarization tasks
- High-volume processing

## Configuration Details

### LLM Factory Architecture

The `LLMFactory` class provides a unified interface for all supported models:

```python
from services.llm_factory import LLMFactory, LLMMessage

# Initialize factory
factory = LLMFactory()

# Create LLM instance
llm = factory.create_llm("gemini-2.0-flash-lite")

# Generate response
response = await llm.generate(messages, temperature=0.7)
```

### Response Format

All LLM responses follow a standardized format:

```python
class LLMResponse:
    content: str              # Generated text
    model: str               # Model used
    provider: str            # Provider (openai/gemini)
    usage: Dict[str, Any]    # Token usage statistics
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file is in the correct location
   - Verify API key format (should start with `sk-`)

2. **Model Not Available**
   - Check if the model name is correct
   - Verify API key has access to the requested model

3. **Rate Limiting**
   - Implement exponential backoff
   - Consider using different models for load balancing

### Error Handling

The LLM factory includes comprehensive error handling:

```python
try:
    response = await llm_factory.generate_response(messages)
except ValueError as e:
    # Invalid model or configuration
    print(f"Configuration error: {e}")
except Exception as e:
    # API or network error
    print(f"Generation error: {e}")
```

## Performance Optimization

### Model Selection Strategy

1. **Development**: Use default models for testing
2. **Production**: Choose models based on specific requirements:
   - Speed: Gemini 2.0 Flash Lite, GPT-4.1 Nano
   - Quality: Gemini 2.5 Pro Preview, GPT-4 Mini
   - Balance: Gemini 2.5 Flash Preview

### Caching and Rate Limiting

- Implement response caching for repeated queries
- Use different models to distribute load
- Monitor usage and costs across providers

## Migration from v1.0

If upgrading from TinyRAG v1.0:

1. Update environment variables to include `GEMINI_API_KEY`
2. Install new dependencies: `pip install -r requirements.txt`
3. Update memo generation calls to include model parameter
4. Test with different models to find optimal configuration

## Support and Resources

- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs/models)
- [OpenAI API Documentation](https://platform.openai.com/docs/overview)
- TinyRAG GitHub Repository: Issues and discussions 