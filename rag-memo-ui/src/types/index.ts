export interface DocumentMetadata {
  filename: string;
  content_type: string;
  size: number;
  upload_date: string;
  processed: boolean;
  error?: string;
}

export interface DocumentChunk {
  text: string;
  page_number: number;
  chunk_index: number;
  embedding?: number[];
}

export interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error?: string;
}

export interface DocumentUploadResponse {
  document: Document;
  message: string;
}

export interface DocumentError {
  message: string;
  code: string;
  details?: unknown;
}

export interface MemoSection {
  title: string;
  content: string;
  citations: string[];
}

export interface Memo {
  id: string;
  user_id: string;
  title: string;
  sections: MemoSection[];
  document_ids: string[];
  created_at: string;
  updated_at: string;
  status: 'completed' | 'processing' | 'failed';
  error?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface DocumentState {
  documents: Document[];
  selectedDocument: Document | null;
  isLoading: boolean;
  error: string | null;
}

export interface MemoState {
  memos: Memo[];
  selectedMemo: Memo | null;
  isLoading: boolean;
  error: string | null;
} 