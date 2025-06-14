import { create } from 'zustand';
import { AuthState, DocumentState, MemoState, User, Document, Memo } from '@/types';

// Auth Store
export const useAuthStore = create<AuthState & {
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  setUser: (user) => set({ user, isAuthenticated: true }),
  setToken: (token) => set({ token }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
}));

// Document Store
export const useDocumentStore = create<DocumentState & {
  setDocuments: (documents: Document[]) => void;
  setSelectedDocument: (selectedDocument: Document | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
}>((set) => ({
  documents: [],
  selectedDocument: null,
  isLoading: false,
  error: null,
  setDocuments: (documents) => set({ documents }),
  setSelectedDocument: (selectedDocument) => set({ selectedDocument }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
    })),
}));

// Memo Store
export const useMemoStore = create<MemoState & {
  setMemos: (memos: Memo[]) => void;
  setSelectedMemo: (selectedMemo: Memo | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  addMemo: (memo: Memo) => void;
  removeMemo: (id: string) => void;
  updateMemo: (id: string, updatedMemo: Partial<Memo>) => void;
}>((set) => ({
  memos: [],
  selectedMemo: null,
  isLoading: false,
  error: null,
  setMemos: (memos) => set({ memos }),
  setSelectedMemo: (selectedMemo) => set({ selectedMemo }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  addMemo: (memo) => set((state) => ({ memos: [...state.memos, memo] })),
  removeMemo: (id) =>
    set((state) => ({
      memos: state.memos.filter((memo) => memo.id !== id),
    })),
  updateMemo: (id, updatedMemo) =>
    set((state) => ({
      memos: state.memos.map((memo) =>
        memo.id === id ? { ...memo, ...updatedMemo } : memo
      ),
    })),
})); 