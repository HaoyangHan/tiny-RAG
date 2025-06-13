## Final Design Document: Enterprise Memo Generation RAG System
BM25
### 6. Recap of Our Design Process

As a team of GenAI architects and data scientists, we have progressed from a high-level concept to a detailed, actionable blueprint. Here's what we accomplished:

1.  **Established a Core Skeleton:** We began by outlining the fundamental components (API, Ingestion, RAG Engine, Databases) and their interactions, ensuring a solid architectural base.
2.  **Incorporated Advanced Capabilities:** We methodically integrated enterprise-grade features, treating them as modular services:
    *   **Multi-format Document Parsing:** Handling everything from PDFs to images with OCR/Vision models.
    *   **Advanced RAG Techniques:** Adding Query Transformation for better retrieval and Metadata Filtering for precision.
    *   **Robust Evaluation:** Designing a hybrid system with both human feedback and automated LLM-as-a-Judge evaluation.
    *   **Enhanced UX:** Allowing editable prompts and ensuring source attribution (citations) for trust and auditability.
3.  **Solidified Engineering Choices:** We selected specific, proven technologies (`FastAPI`, `Dramatiq`, `Redis`, `Beanie`, `LlamaIndex`) and designed a non-blocking, asynchronous workflow to ensure the system is responsive and scalable.
4.  **Designed for the User:** We created mockups and API flows that prioritize a clean, intuitive user experience, from document upload to reviewing the final, cited memo.
5.  **Made it Actionable:** This final document translates the architecture into tangible artifacts: a complete system diagram, a project plan via Jira Epics, and a recommended repository structure with setup instructions.

This comprehensive design provides a clear path forward to build a state-of-the-art, secure, and highly valuable RAG capability for a large financial institution.

---
### 1. Complete System Architecture Diagram (Mermaid)

pass

### 2. SVG Workflow

pass

### 3. Detailed Design Markdown

This section provides the implementation-level details for each component.

#### 3.1. Component Deep Dive

##### 3.1.1. Frontend (`rag-memo-ui`)
*   **Technology:** React or Vue.js, TypeScript, Vite, TailwindCSS.
*   **Responsibilities:**
    *   Provide the UI for project management, document upload, and memo generation (as per the wireframe).
    *   Handle user authentication (e.g., JWT tokens).
    *   Interact with the backend via REST API calls.
    *   Implement asynchronous polling for generation status.
    *   Render the final memo, including interactive citations (e.g., hover-to-view source text).
    *   Provide a UI for the "Prompt Engineering Studio" for power users.

##### 3.1.2. API Gateway (`rag-memo-api`)
*   **Technology:** FastAPI, Pydantic, Python 3.11+.
*   **Responsibilities:**
    *   Serve as the single entry point for the frontend.
    *   Handle request validation using Pydantic.
    *   Orchestrate calls by enqueuing tasks to Dramatiq rather than executing them directly.
    *   Manage database connections.
*   **Key Endpoints:**
    *   `POST /documents/upload`: Accepts a file, creates a `Document` entry in Mongo, and enqueues `process_document_ingestion` task. Returns a `document_id`.
    *   `POST /generate`: Accepts `{document_id, element_id, modified_prompt}`. Creates an `ElementGeneration` entry with `status="pending"`, enqueues `run_rag_generation` task. Returns `202 Accepted` with a `generation_id` and a status polling URL.
    *   `GET /generations/{generation_id}`: Fetches the result of a generation. If still pending, returns current status.
    *   CRUD endpoints for `/projects` and `/elements` (prompts).

##### 3.1.3. Asynchronous Layer (`rag-memo-api`)
*   **Technology:** Dramatiq, Redis.
*   **Responsibilities:**
    *   Execute all long-running, resource-intensive tasks without blocking the API.
*   **Actors (Tasks):**
    *   `process_document_ingestion(document_id)`:
        1.  Fetches document from storage.
        2.  Uses the `DocumentParsingService` to get text and metadata.
        3.  Uses the `CoreRAGEngine` to chunk, embed, and store in the Vector DB.
        4.  Updates the `Document` status in MongoDB to "completed" or "failed".
    *   `run_rag_generation(generation_id, document_id, modified_prompt)`:
        1.  Updates generation status to "processing".
        2.  Calls `QueryTransformationService` to create a concise query.
        3.  Uses `CoreRAGEngine` to retrieve relevant nodes using the concise query.
        4.  Uses `CoreRAGEngine` to call the LLM with the *original* `modified_prompt` and retrieved context.
        5.  Extracts citations from the response's source nodes.
        6.  Saves the final output, context, and citations to the `ElementGeneration` document.
        7.  Updates status to "completed".
        8.  (Optional) Enqueues `run_llm_as_judge` task.

##### 3.1.4. Core Services (Modules within `rag-memo-api`)
*   **Document Parsing Service:**
    *   Uses a factory pattern based on file extension/MIME type.
    *   Integrates `LlamaIndex`'s `SimpleDirectoryReader` with a custom `file_extractor` dictionary mapping file types to parsing functions.
    *   For images/scanned PDFs, it will call a multi-modal model (e.g., `LlamaIndex`'s `GeminiMultiModal`) to perform OCR and description.
*   **Core RAG Engine:**
    *   The central LlamaIndex logic.
    *   **Indexing:** Encapsulates the `IngestionPipeline` which includes `SentenceSplitter`, `MetadataExtractor`, and the `EmbeddingModel`.
    *   **Retrieval:** Instantiates `VectorStoreIndex.from_vector_store()` and creates a retriever (`as_retriever()`). This is where `MetadataFilters` will be applied.
    *   **Synthesis:** Uses a `ResponseSynthesizer` to combine the prompt and context. This provides control over how the final prompt is built and allows access to `source_nodes` for citation.
*   **Evaluation Service:**
    *   Contains logic for `LLM-as-a-Judge`.
    *   Constructs a detailed prompt with a rubric (e.g., evaluating for faithfulness, relevance, clarity) and sends the query, context, and generated answer to a powerful LLM for scoring.
    *   Integrates with frameworks like `RAGAs` for standardized metric calculation.

#### 3.2. Data Models (`rag-memo-core-lib` or `rag-memo-api`)

The Beanie ODM models are central to the application's data structure. (Re-stating from v2.0 for completeness).

```python
# models.py
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

# Models for Project, Document, Element, ElementGeneration, Evaluation
# as defined previously.
# ...
```

### 4. Epics for Jira Tickets

This project can be broken down into the following high-level epics for agile development.

*   **EPIC-1: Foundation & DevOps Setup**
    *   *User Story:* As a DevOps Engineer, I need to set up the GitHub repositories, Dockerfiles, and a `docker-compose` environment for local development (FastAPI, Redis, Mongo, Workers).
    *   *User Story:* As a Backend Developer, I need to initialize the FastAPI application with basic health check endpoints and configure settings management (e.g., using Pydantic's `BaseSettings`).

*   **EPIC-2: Core Ingestion Pipeline**
    *   *User Story:* As a Data Scientist, I need to implement the Document Parsing Service to handle text-based PDFs and DOCX files.
    *   *User Story:* As a Backend Developer, I need to create the `/documents/upload` endpoint and the `process_document_ingestion` Dramatiq actor.
    *   *User Story:* As a Data Scientist, I need to integrate the multi-modal vision model for parsing images and scanned PDFs.
    *   *User Story:* As a Data Scientist, I need to implement metadata extraction (e.g., keywords, dates) during the ingestion pipeline.

*   **EPIC-3: End-to-End RAG Generation Flow**
    *   *User Story:* As a Backend Developer, I need to implement the asynchronous `/generate` endpoint and the `run_rag_generation` actor.
    *   *User Story:* As a Data Scientist, I need to implement the Query Transformation Service to create concise queries for retrieval.
    *   *User Story:* As a Data Scientist, I need to implement the core retrieval and generation logic using LlamaIndex.
    *   *User Story:* As a Backend Developer, I need to implement citation/source attribution by extracting data from LlamaIndex's `source_nodes`.

*   **EPIC-4: Frontend UI/UX**
    *   *User Story:* As a Frontend Developer, I need to build the main workspace layout with panels for documents, the prompt editor, and the results.
    *   *User Story:* As a Frontend Developer, I need to implement the document upload functionality.
    *   *User Story:* As a Frontend Developer, I need to implement the generation flow, including prompt editing, submitting the request, and polling for results.
    *   *User Story:* As a Frontend Developer, I need to render the final memo with clickable citations that reveal source information.

*   **EPIC-5: Evaluation & Prompt Engineering**
    *   *User Story:* As a Backend Developer, I need to create an endpoint and data model for submitting human feedback (ratings).
    *   *User Story:* As a Data Scientist, I need to implement the LLM-as-a-Judge Evaluation Service as an asynchronous task.
    *   *User Story:* As a Frontend Developer, I need to build the UI for the "Prompt Engineering Studio" where prompts can be tested and compared.

### 5. GitHub Repository Structure

For a project of this scale in an enterprise setting, separating the frontend and backend is a standard best practice. A third repository for shared code can prevent duplication.

**1. `rag-memo-api` (Backend)**
*   **Purpose:** Houses the FastAPI application, Dramatiq workers, and all core backend logic.
*   **`README.md`:**
    ```markdown
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
    ```

**2. `rag-memo-ui` (Frontend)**
*   **Purpose:** The user-facing web application.
*   **`README.md`:**
    ```markdown
    # RAG Memo Generation - Frontend UI

    This repository contains the frontend application built with React/Vue.js. It provides the user interface for interacting with the RAG system.

    **Tech Stack:**
    - Node.js
    - React / Vue.js
    - TypeScript
    - Vite
    - TailwindCSS

    **Setup & Installation:**
    1. Clone the repository: `git clone ...`
    2. Install dependencies: `npm install`
    3. Set up environment variables by copying `.env.local.example` to `.env.local` and setting the `VITE_API_BASE_URL`.

    **Running the Application:**
    - `npm run dev`
    ```

**3. (Optional but Recommended) `rag-memo-core-lib`**
*   **Purpose:** A shared Python library to hold code used by both the API and potentially other services (like standalone scripts or a future admin dashboard). This is ideal for the Beanie data models.
*   **`README.md`:**
    ```markdown
    # RAG Memo Generation - Core Library

    This repository contains the shared core library for the RAG Memo project. It primarily holds the Pydantic/Beanie data models to ensure consistency across the platform.

    **Installation:**
    This package can be installed in other projects (like `rag-memo-api`) in editable mode for local development:
    `pip install -e /path/to/rag-memo-core-lib`
    ```