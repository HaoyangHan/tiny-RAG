# TinyRAG API

The backend API for the TinyRAG platform, providing document processing and memo generation capabilities.

## Features

- Document upload and processing
- PDF text extraction and chunking
- Vector embeddings generation
- Memo generation with citations
- RESTful API endpoints
- JWT authentication
- MongoDB integration
- Redis caching

## Prerequisites

- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+
- OpenAI API key

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```env
DEBUG=False
API_V1_STR=/api/v1
PROJECT_NAME=TinyRAG
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=tinyrag
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## Running the Application

### Development

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up --build
```

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Documents

- `POST /api/v1/documents/upload` - Upload and process a document
- `GET /api/v1/documents/` - List all documents
- `GET /api/v1/documents/{document_id}` - Get a specific document
- `DELETE /api/v1/documents/{document_id}` - Delete a document

### Memos

- `POST /api/v1/memos/` - Create a new memo
- `GET /api/v1/memos/` - List all memos
- `GET /api/v1/memos/{memo_id}` - Get a specific memo
- `DELETE /api/v1/memos/{memo_id}` - Delete a memo

## Testing

Run the test suite:

```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 