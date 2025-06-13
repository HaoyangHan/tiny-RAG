# RAG Memo Generation - Monorepo

This repository contains the complete system for enterprise memo generation, including both backend services and frontend UI. The backend handles document ingestion, retrieval-augmented generation (RAG), and evaluation, while the frontend provides an intuitive user interface for interacting with the system.

## Structure

- **tiny-rag-be:** Backend services built with FastAPI and Dramatiq.
- **tiny-rag-fe:** Frontend application built with React/Vue.js.

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- Dramatiq & Redis
- LlamaIndex
- Beanie (MongoDB ODM)
- Pydantic

### Frontend
- Node.js
- React / Vue.js
- TypeScript
- Vite
- TailwindCSS

## Setup & Installation

### Backend
1. Navigate to the backend directory: `cd tiny-rag-be`
2. Create and activate a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up environment variables by copying `.env.example` to `.env` and filling in the values (DB URI, LLM API Keys, etc.).

### Frontend
1. Navigate to the frontend directory: `cd tiny-rag-fe`
2. Install dependencies: `npm install`
3. Set up environment variables by copying `.env.local.example` to `.env.local` and setting the `VITE_API_BASE_URL`.

## Running the Application

### Backend
- **API Server:** `uvicorn api.main:app --reload`
- **Dramatiq Workers:** `dramatiq workers.actors`

### Frontend
- **Development Server:** `npm run dev`

## Notes
Ensure both backend and frontend services are running for full functionality. The frontend communicates with the backend via the API gateway.