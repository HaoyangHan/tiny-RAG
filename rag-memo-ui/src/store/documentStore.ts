import { create } from 'zustand';
import { Document } from '@/types';

interface DocumentState {
  documents: Document[];
  selectedDocument: Document | null;
  isLoading: boolean;
  error: string | null;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  selectDocument: (document: Document | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  documents: [],
  selectedDocument: null,
  isLoading: false,
  error: null,
  addDocument: (document) =>
    set((state) => ({
      documents: [...state.documents, document],
    })),
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
      selectedDocument:
        state.selectedDocument?.id === id ? null : state.selectedDocument,
    })),
  selectDocument: (document) =>
    set({
      selectedDocument: document,
    }),
  setLoading: (isLoading) =>
    set({
      isLoading,
    }),
  setError: (error) =>
    set({
      error,
    }),
})); 