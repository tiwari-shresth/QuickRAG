import streamlit as st
import tempfile
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Clean environment variables defensively
if os.environ.get("MISTRAL_API_KEY"):
    os.environ["MISTRAL_API_KEY"] = os.environ["MISTRAL_API_KEY"].strip("'\" ")

st.set_page_config(page_title="RAG Book Assistant", page_icon="📚", layout="wide")

st.title("📚 QuickRAG - Document QA Assistant")
st.write("Upload a PDF document to create a clean vector database and ask precise questions.")

# Sidebar for database management
with st.sidebar:
    st.header("⚙️ Database Management")
    if st.button("🗑️ Clear Vector Database"):
        if os.path.exists("chroma_db"):
            try:
                embeddings = MistralAIEmbeddings(model="mistral-embed")
                vstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
                vstore.delete_collection()
                st.success("Vector database collection cleared! Upload a new document to start fresh.")
            except Exception as e:
                st.warning(f"Cleared database state: {e}")
            st.rerun()
        else:
            st.info("No active vector database found.")

uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    st.success(f"📄 '{uploaded_file.name}' uploaded successfully!")

    if st.button("🚀 Process Document & Build Vector DB"):
        with st.spinner("Extracting text, chunking, and embedding with Mistral AI..."):
            embeddings = MistralAIEmbeddings(model="mistral-embed")
            
            # Safely delete existing collection via API without corrupting SQLite handles
            if os.path.exists("chroma_db"):
                try:
                    old_vstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
                    old_vstore.delete_collection()
                except Exception:
                    pass

            loader = PyPDFLoader(file_path)
            docs = loader.load()

            valid_docs = [doc for doc in docs if doc.page_content and doc.page_content.strip()]

            if not valid_docs:
                st.error("No readable text found in the uploaded PDF!")
            else:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                chunks = splitter.split_documents(valid_docs)

                vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=embeddings,
                    persist_directory="chroma_db"
                )
                st.success(f"✅ Vector database created successfully with {len(chunks)} chunks!")

    try:
        os.remove(file_path)
    except Exception:
        pass

if os.path.exists("chroma_db"):
    embeddings = MistralAIEmbeddings(model="mistral-embed")
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    llm = ChatMistralAI(model="mistral-small-2506")

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert technical AI assistant.
Use ONLY the provided context below to answer the user's question accurately and concisely.
If the answer is not present in the provided context, respond strictly with:
"I could not find the answer in the uploaded document."

Context:
{context}
"""
        ),
        (
            "human",
            "Question: {question}"
        )
    ])

    st.divider()
    st.subheader("💬 Ask Questions From Your Document")

    query = st.text_input("Enter your question about the uploaded document:")

    if query:
        with st.spinner("Searching document & synthesizing answer..."):
            docs = retriever.invoke(query)

            if not docs:
                st.warning("No matching context found in the document.")
            else:
                context = "\n\n---\n\n".join([doc.page_content for doc in docs])

                final_prompt = prompt.invoke({
                    "context": context,
                    "question": query
                })

                response = llm.invoke(final_prompt)

                st.write("### 🤖 AI Answer")
                st.write(response.content)

                with st.expander("🔍 View Retrieved Context Chunks (Top Matches)"):
                    for i, doc in enumerate(docs):
                        page_num = doc.metadata.get("page", "N/A")
                        st.markdown(f"**Chunk {i+1} (Page {page_num}):**")
                        st.info(doc.page_content)