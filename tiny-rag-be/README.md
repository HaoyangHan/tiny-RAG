    # RAG Memo Generation - API & Backend Services

    This repository contains the backend for the enterprise memo generation system. It includes the FastAPI API gateway, Dramatiq asynchronous task workers, and all core business logic for document ingestion, RAG, and evaluation.

    **Tech Stack:**
    - Python 3.11+
    - FastAPI
    - Dramatiq & Redis
    - LlamaIndex
    - Beanie (MongoDB ODM)
    - Pydantic

    **Setup & Installation:**
    1. Clone the repository: `git clone ...`
    2. Create and activate a virtual environment: `python -m venv venv && source venv/bin/activate`
    3. Install dependencies: `pip install -r requirements.txt`
    4. Set up environment variables by copying `.env.example` to `.env` and filling in the values (DB URI, LLM API Keys, etc.).

    **Running the Application:**
    - **API Server:** `uvicorn api.main:app --reload`
    - **Dramatiq Workers:** `dramatiq workers.actors`