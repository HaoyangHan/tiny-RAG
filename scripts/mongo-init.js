// MongoDB Initialization Script for TinyRAG
// This script runs when MongoDB container starts for the first time

// Switch to the tinyrag database
db = db.getSiblingDB('tinyrag');

// Create application user
db.createUser({
  user: 'tinyrag_user',
  pwd: 'tinyrag_password',
  roles: [
    {
      role: 'readWrite',
      db: 'tinyrag'
    }
  ]
});

// Create collections with validation schemas
db.createCollection('documents', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['filename', 'file_size', 'content_type', 'status', 'created_at'],
      properties: {
        filename: {
          bsonType: 'string',
          description: 'Document filename is required'
        },
        file_size: {
          bsonType: 'number',
          minimum: 0,
          description: 'File size must be a positive number'
        },
        content_type: {
          bsonType: 'string',
          description: 'Content type is required'
        },
        status: {
          bsonType: 'string',
          enum: ['uploading', 'processing', 'completed', 'error'],
          description: 'Status must be one of the allowed values'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created date is required'
        }
      }
    }
  }
});

db.createCollection('generations', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['document_id', 'prompt', 'status', 'created_at'],
      properties: {
        document_id: {
          bsonType: 'objectId',
          description: 'Document ID is required'
        },
        prompt: {
          bsonType: 'string',
          description: 'Prompt is required'
        },
        status: {
          bsonType: 'string',
          enum: ['pending', 'processing', 'completed', 'error'],
          description: 'Status must be one of the allowed values'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created date is required'
        }
      }
    }
  }
});

db.createCollection('document_chunks', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['document_id', 'chunk_index', 'content', 'created_at'],
      properties: {
        document_id: {
          bsonType: 'objectId',
          description: 'Document ID is required'
        },
        chunk_index: {
          bsonType: 'number',
          minimum: 0,
          description: 'Chunk index must be a non-negative number'
        },
        content: {
          bsonType: 'string',
          description: 'Chunk content is required'
        },
        embedding: {
          bsonType: 'array',
          description: 'Vector embedding for the chunk'
        },
        created_at: {
          bsonType: 'date',
          description: 'Created date is required'
        }
      }
    }
  }
});

// Create indexes for better performance
db.documents.createIndex({ 'filename': 1 });
db.documents.createIndex({ 'status': 1 });
db.documents.createIndex({ 'created_at': -1 });
db.documents.createIndex({ 'content_type': 1 });

db.generations.createIndex({ 'document_id': 1 });
db.generations.createIndex({ 'status': 1 });
db.generations.createIndex({ 'created_at': -1 });

db.document_chunks.createIndex({ 'document_id': 1 });
db.document_chunks.createIndex({ 'chunk_index': 1 });
db.document_chunks.createIndex({ 'document_id': 1, 'chunk_index': 1 });

// Create vector search index for embeddings (this would typically be done via Atlas UI)
// Note: This is a placeholder - actual vector search setup requires MongoDB Atlas
try {
  db.document_chunks.createIndex(
    { 'embedding': 'vector' },
    {
      name: 'document_embeddings_vector_index',
      vectorOptions: {
        type: 'hnsw',
        similarity: 'cosine',
        dimensions: 1536
      }
    }
  );
  print('Vector search index created successfully');
} catch (e) {
  print('Vector search index creation failed (requires MongoDB Atlas): ' + e.message);
}

// Insert sample data for testing
db.documents.insertOne({
  filename: 'sample-document.pdf',
  file_size: 1024000,
  content_type: 'application/pdf',
  status: 'completed',
  metadata: {
    pages: 10,
    language: 'en',
    title: 'Sample Document'
  },
  created_at: new Date(),
  updated_at: new Date()
});

print('TinyRAG database initialized successfully!');
print('Collections created: documents, generations, document_chunks');
print('Indexes created for optimal performance');
print('Sample data inserted for testing'); 