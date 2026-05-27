import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_pinecone import PineconeVectorStore
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

# 5. Define the Live Web Endpoint
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

# Root health-check endpoint for cloud platform deployment
@app.get("/")
def read_root():
    return {"message": "Cloud RAG Engine is active and running!"}

    # ... (Keep all your existing FastAPI app and endpoint code exactly the same)

if __name__ == "__main__":
    import uvicorn
    # Render automatically injects an environment variable called PORT.
    # We read that, fallback to 8000 if local, and bind to 0.0.0.0
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


from fastapi import UploadFile, File, HTTPException
import io

# Make sure to install pypdf if handling PDFs: pip install pypdf
# directly import your text splitter and pinecone vectorstore setup here 
# (e.g., from langchain_text_splitters import RecursiveCharacterTextSplitter)

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a user-uploaded document, extracts text, chunks it, 
    and streams vector embeddings directly into the live Pinecone index.
    """
    try:
        # 1. Read file bytes into memory
        contents = await file.read()
        text = ""

        # 2. Extract text based on file type
        if file.filename.endswith(".txt"):
            text = contents.decode("utf-8")
        elif file.filename.endswith(".pdf"):
            import pypdf
            pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .txt or .pdf")

        if not text.strip():
            raise HTTPException(status_code=400, detail="The uploaded file contains no readable text.")

        # 3. Chunk the extracted text dynamically
        # Using the exact configuration from your local ingestion phase
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)

        # 4. Upsert chunks into your live cloud Pinecone Vectorstore instance
        # vectorstore.add_texts(chunks) 
        
        return {
            "status": "success", 
            "message": f"Successfully processed {file.filename}.",
            "chunks_ingested": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")