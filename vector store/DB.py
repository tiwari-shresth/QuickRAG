import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore  # Switched to Pinecone
from langchain_mistralai import MistralAIEmbeddings
import time  # NEW: For adding rate limit delays
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# 1. Setup paths relative to this script
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
docs_directory = os.path.join(root_dir, "document loaders")

# 2. Define Index Name
index_name = "rag-implementation"

# 3. Initialize Mistral Embeddings (1024 dimensions)
embedding_model = MistralAIEmbeddings(model="mistral-embed")

all_documents = []

print("--- Starting Automated Cloud Ingestion Pipeline ---")
print(f"[SCANNER] Scanning directory: '{docs_directory}' for files...")

if not os.path.exists(docs_directory):
    print(f"[ERROR] Directory '{docs_directory}' does not exist!")
    exit()

for filename in os.listdir(docs_directory):
    file_path = os.path.join(docs_directory, filename)
    if os.path.isdir(file_path):
        continue
        
    ext = filename.split('.')[-1].lower()
    
    try:
        if ext == "pdf":
            print(f"[LOADER] Found PDF -> Processing: {filename}")
            loader = PyPDFLoader(file_path)
            all_documents.extend(loader.load())
        elif ext == "txt":
            print(f"[LOADER] Found Text File -> Processing: {filename}")
            loader = TextLoader(file_path)
            all_documents.extend(loader.load())
    except Exception as e:
        print(f"[ERROR] Failed to process file {filename}: {str(e)}")

# 4. Split documents into semantic chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,       # Tuned chunk size
    chunk_overlap=400       # Tuned overlap
)
chunks = text_splitter.split_documents(all_documents)
print(f"[SPLITTER] Split files into {len(chunks)} total text chunks.")

# 5. INITIALIZE PINECONE BLANK STRUCTURE
print(f"[EMBEDDING] Connecting to Cloud Pinecone Index: '{index_name}'...")
vectorstore = PineconeVectorStore(
    index_name=index_name,
    embedding=embedding_model
)

# 6. RATE-LIMIT SAFE UPLOAD: Loop through chunks in small batches
batch_size = 50  # Smaller batch size to safe-guard Mistral's free rate limits
total_chunks = len(chunks)

print(f"[UPLOAD] Starting throttled batch upload of {total_chunks} chunks to prevent 429 Errors...")

for i in range(0, total_chunks, batch_size):
    batch = chunks[i:i + batch_size]
    print(f"  -> Processing chunks {i + 1} to {min(i + batch_size, total_chunks)} of {total_chunks}...")
    
    # Upload smaller groups cleanly
    vectorstore.add_documents(documents=batch)
    
    # Introduce a short cooling-off period to prevent hitting rate limits
    if i + batch_size < total_chunks:
        print("     [THROTTLE] Sleeping for 3 seconds to preserve free-tier API limits...")
        time.sleep(3)

print("--- Cloud Database successfully built and synchronized safely! ---")