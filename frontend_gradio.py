import gradio as gr
import requests

UPLOAD_URL = "https://quickrag.onrender.com/api/upload"
CHAT_URL = "https://quickrag.onrender.com/api/chat"

def upload_to_backend(file_list):
    """Sends multiple user files from the browser to Render's bulk processing engine"""
    if not file_list:
        return "⚠️ No files selected."
    
    try:
        # Build a list of file tuples for requests' multipart encoder
        files_payload = []
        opened_files = []
        
        for file in file_list:
            f_handle = open(file.name, "rb")
            opened_files.append(f_handle)
            # Structure: (form_field_name, (filename, file_data_stream, content_type))
            files_payload.append(("files", (file.name, f_handle, "application/octet-stream")))

        # Fire a single POST request containing all files
        response = requests.post(UPLOAD_URL, files=files_payload, timeout=120)
        
        # Clean up and close all file handlers safely
        for f in opened_files:
            f.close()
            
        if response.status_code == 200:
            res_data = response.json()
            return f"✅ Success! Ingested {res_data.get('total_chunks_ingested')} total chunks from {len(res_data.get('processed_files', []))} files into Pinecone Cloud."
        else:
            return f"❌ Bulk upload failed with status code: {response.status_code}"
            
    except Exception as e:
        return f"❌ Transmission Error: {str(e)}"

def predict_rag(message, history):
    try:
        response = requests.post(CHAT_URL, json={"question": message}, timeout=60)
        if response.status_code == 200:
            return response.json().get("answer", "Error reading server response.")
        return f"⚠️ Server Error {response.status_code}"
    except Exception as e:
        return f"⚠️ Connection failed: {e}"

with gr.Blocks(theme="ocean", title="QuickRAG Multi-Tenant Platform") as demo:
    gr.Markdown("# 🚀 Dynamic Bulk Cloud-Native RAG System")
    gr.Markdown("Select and upload multiple `.pdf` or `.txt` documents at once, parse them into global vector spaces, and query them simultaneously.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Bulk Document Ingestion")
            # CHANGED: Added file_count="multiple" here
            file_input = gr.File(label="Choose PDF or Text Files", file_types=[".pdf", ".txt"], file_count="multiple")
            upload_button = gr.Button("Process & Sync All to Cloud Vector Index", variant="primary")
            status_output = gr.Textbox(label="Ingestion Server Status Pipeline", placeholder="System idle...", interactive=False)
            
            upload_button.click(fn=upload_to_backend, inputs=file_input, outputs=status_output)
            
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Batch Knowledge Chat")
            gr.ChatInterface(
                fn=predict_rag,
                examples=["Synthesize data from all uploaded documents", "What are the common points between these files?"],
                textbox=gr.Textbox(placeholder="Ask anything about your data cluster...", container=False, scale=7)
            )

if __name__ == "__main__":
    demo.launch(share=True)