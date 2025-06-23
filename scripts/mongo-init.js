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

// Create collections without strict validation (Beanie handles validation)
db.createCollection('documents');
db.createCollection('generations');
db.createCollection('document_chunks');
db.createCollection('users');

// Create indexes for better performance
db.documents.createIndex({ 'user_id': 1 });
db.documents.createIndex({ 'filename': 1 });
db.documents.createIndex({ 'status': 1 });
db.documents.createIndex({ 'created_at': -1 });
db.documents.createIndex({ 'content_type': 1 });

db.generations.createIndex({ 'user_id': 1 });
db.generations.createIndex({ 'status': 1 });
db.generations.createIndex({ 'created_at': -1 });

db.document_chunks.createIndex({ 'document_id': 1 });
db.document_chunks.createIndex({ 'chunk_index': 1 });
db.document_chunks.createIndex({ 'document_id': 1, 'chunk_index': 1 });

db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 }, { unique: true });
db.users.createIndex({ 'role': 1 });

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

print('TinyRAG database initialized successfully!');
print('Collections created: documents, generations, document_chunks, users');
print('Indexes created for optimal performance');
print('Schema validation handled by Beanie models'); 