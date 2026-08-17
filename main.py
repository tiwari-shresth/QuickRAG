import os
import io
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from langchain_pinecone import PineconeVectorStore
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pypdf

load_dotenv()

# 1. Initialize FastAPI Application
app = FastAPI(
    title="Cloud RAG API Backend",
    description="A production-ready FastAPI endpoint serving document contexts from Pinecone."
)

# 2. Configure Cloud Vector Storage
index_name = "rag-implementation"
embedding_model = MistralAIEmbeddings(model="mistral-embed")

vectorstore = PineconeVectorStore(
    index_name=index_name,
    embedding=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 7}
)

# 3. Setup Language Model Pipeline
llm = ChatMistralAI(model="mistral-small-2506")

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant.
Use ONLY the provided context to answer the question.
If the answer is not present in the context, say: "I could not find the answer in the document."
"""
    ),
    (
        "human",
        """Context:
{context}

Question:
{question}
"""
    )
])

# 4. Define Data Structure for Incoming API Requests
class ChatQuery(BaseModel):
    question: str

# 5. Define API Endpoints
@app.get("/")
def read_root():
    return {"message": "Cloud RAG Engine is active and running!"}

@app.post("/api/chat")
async def chat_endpoint(payload: ChatQuery):
    """
    Accepts a JSON payload containing a 'question' string, retrieves context 
    from the cloud vector DB, and returns the synthesized answer.
    """
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        # Retrieve context over the cloud interface
        docs = retriever.invoke(payload.question)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Compile final LLM chain prompt
        final_prompt = prompt.invoke({
            "context": context,
            "question": payload.question
        })
        
        # Invoke generation model
        response = llm.invoke(final_prompt)
        
        return {
            "question": payload.question,
            "answer": response.content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Accepts multiple user-uploaded documents, extracts text from all of them,
    chunks them, and batches them into the live Pinecone index.
    """
    try:
        all_chunks = []
        processed_files = []

        for file in files:
            contents = await file.read()
            text = ""

            # Extract text based on file type
            if file.filename.endswith(".txt"):
                text = contents.decode("utf-8")
            elif file.filename.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""
            else:
                # Skip unsupported files
                continue

            if not text.strip():
                continue

            # Chunk the extracted text dynamically
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text(text)
            all_chunks.extend(chunks)
            processed_files.append(file.filename)

        if not all_chunks:
            raise HTTPException(status_code=400, detail="No readable text found in any of the uploaded files.")

        # Upsert ALL combined chunks into your live cloud Pinecone Vectorstore instance
        vectorstore.add_texts(all_chunks)
        
        return {
            "status": "success", 
            "message": f"Successfully processed {len(processed_files)} files.",
            "processed_files": processed_files,
            "total_chunks_ingested": len(all_chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk ingestion failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)