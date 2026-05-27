# QuickRAG 🚀

A high-performance, cloud-native Document Intelligence platform that allows users to upload multiple files simultaneously and chat with their unstructured data in real time.

---
**🔗 Check it Out!!!:** [Interact with QuickRAG on Hugging Face](https://huggingface.co/spaces/shresthtiwari/QuickRAG)

## 📌 Executive Summary

### What It Is
QuickRAG is a fully decoupled, modular, end-to-end RAG pipeline. It provides a clean, user-friendly workspace where anyone can drop complex documents and immediately extract insights through an interactive AI chat interface.

### What It Solves (The Problem)
Traditional keyword search fails when querying large, complex enterprise documents (like PDFs, reports, or research papers). Extracting specific contextual knowledge manually is time-consuming, while standard LLMs suffer from a lack of private data access and generate "hallucinations" when answering specific technical queries.

### How It Solves It (The Solution)
QuickRAG solves this by building a coordinated, live cloud RAG pipeline:
1. **Bulk Ingestion:** Users upload multiple documents (`.pdf`, `.txt`) at once through a lightweight web interface.
2. **Vector Space Processing:** The backend extracts raw text, segments it into semantic chunks, and transforms it into high-dimensional vector embeddings.
3. **Cloud Memory Storage:** These embeddings are indexed directly into a cloud-native, serverless vector database.
4. **Contextual Synthesis:** When a user asks a question, the platform performs a semantic similarity search to retrieve the exact matching reference blocks and passes them to a state-of-the-art LLM to generate accurate, source-backed answers instantly.

---

## System Architecture

The platform is engineered using a **decoupled microservices architecture** to ensure high availability, separate compute workloads, and independent scalability across the RAG pipeline.


┌────────────────────────┐      File Stream      ┌─────────────────────────┐
│     Client Layer       │──────────────────────>│      Compute Layer      │
│ (Hugging Face Spaces)  │<──────────────────────│    (FastAPI / Render)   │
└────────────────────────┘     JSON Response     └─────────────────────────┘
▲                                                 │
│                                                 │ Upsert / Query
│ Direct Chat Stream                              ▼
│                                    ┌─────────────────────────┐
└────────────────────────────────────│   Vector Database Core  │
│    (Pinecone Cloud)     │
└─────────────────────────┘

* **Frontend UI (Hugging Face Spaces):** Built using **Gradio**, providing an intuitive asynchronous interface for multi-file uploading and interactive message streaming.
* **Backend API Engine (Render):** Powered by **FastAPI** to manage asynchronous routing, batch multi-part file parsing (`pypdf`), and token-efficient semantic chunking (`langchain-text-splitters`) inside the core RAG pipeline.
* **Vector Intelligence Cluster (Pinecone Serverless):** A cloud vector database handling real-time indexing and fast cosine-similarity matching.
* **LLM Core (Mistral AI):** Handles contextual synthesis to generate fluid, natural-language responses backed by strict document retrieval grounding.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Pinecone Cloud Account & API Key
* Mistral AI API Key

### 1. Backend Installation & Setup
Navigate to your backend directory and set up your virtual environment:

```bash
# Clone the repository
git clone [https://github.com/your-username/QuickRAG.git](https://github.com/your-username/QuickRAG.git)
cd QuickRAG

# Install dependencies
pip install -r requirements.txt
```

### Create a .env file in the root directory and add your credentials:
PINECONE_API_KEY=your_pinecone_key_here
MISTRAL_API_KEY=your_mistral_key_here

### Run the FastAPI production server locally:
* python main.py
* The API interactive documentation will be available live at http://localhost:10000/docs

## 2. Frontend Interface Setup
### Launch the user interface dashboard on your local machine:
* pip install gradio requests
* python frontend_gradio.py

### 📊 Performance & Impact Metrics
* Simultaneous Multi-File Batching: Optimized server-side network ingestion streams to process multiple cross-format files concurrently.
* Low Latency Processing: Reduced end-to-end vector pipeline cold-starts to under 2.5 seconds per contextual query.
* Zero-Hallucination Guardrails: Implemented a rigid retrieval-augmented threshold ensuring the model only synthesizes answers strictly explicitly stated inside your data cluster.
