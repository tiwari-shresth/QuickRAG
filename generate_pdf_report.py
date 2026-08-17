import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header (Skip on Page 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "QuickRAG: Cloud-Native RAG Implementation Project Technical Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, footer_text)
        self.drawString(54, 36, "Confidential - GenAI Project Documentation")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 8.5 * 72 - 54, 48)
        
        self.restoreState()

def build_pdf(filename="QuickRAG_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    PRIMARY = colors.HexColor("#1E3A8A")   # Deep Navy Blue
    SECONDARY = colors.HexColor("#0D9488") # Teal Accent
    DARK_TEXT = colors.HexColor("#1F2937") # Charcoal Text
    LIGHT_BG = colors.HexColor("#F8FAFC")  # Light Gray
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=DARK_TEXT,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        backColor=LIGHT_BG,
        borderColor=BORDER_COLOR,
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=body_style,
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # Title Block
    story.append(Paragraph("QuickRAG: Production Cloud-Native RAG Platform", title_style))
    story.append(Paragraph("System Architecture, Code Review, Trade-off Analysis & Deployment Report", subtitle_style))
    story.append(Paragraph("<b>Live Hugging Face Space:</b> <font color='#0D9488'><u>https://huggingface.co/spaces/shresthtiwari/QuickRAG</u></font><br/><b>Live Render FastAPI Backend:</b> <font color='#0D9488'><u>https://quickrag.onrender.com</u></font>", ParagraphStyle('DeployLinks', parent=body_style, fontSize=9, leading=13, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=12))

    # Section 1: How to Introduce to an Interviewer
    story.append(Paragraph("1. Interviewer Pitch & Technical Defense Script", h1_style))
    story.append(Paragraph("<b>Realistic 60-Second Elevator Pitch (Zero Fluff, Technical Focus):</b>", h2_style))
    
    pitch_text = (
        "<i>\"QuickRAG is an enterprise-grade Retrieval-Augmented Generation platform designed to eliminate LLM hallucinations "
        "and contextual boundaries when querying multi-format document clusters. "
        "The system decouples document processing from LLM synthesis using a cloud-native architecture: "
        "FastAPI serves async endpoints, document embeddings are dynamically chunked using RecursiveCharacterTextSplitter and vectorized with Mistral AI (1024 dimensions), "
        "and vectors are stored in Pinecone Cloud for scalable ANN similarity search. "
        "On the front end, a Gradio interface allows users to perform multi-file bulk uploads and interactive knowledge retrieval. "
        "I specifically engineered rate-limit safe batch throttling for vector upserts and implemented deterministic system prompts to enforce strict context-grounded responses.\"</i>"
    )
    
    callout_data = [[Paragraph(pitch_text, callout_style)]]
    callout_table = Table(callout_data, colWidths=[7.0 * inch])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDFA")),
        ('BORDER', (0,0), (-1,-1), 1, SECONDARY),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Anticipated Interviewer Cross-Questions & Instant Technical Responses:</b>", h2_style))
    qa_pairs = [
        ("Q1: How do you prevent LLM hallucinations when context is missing?",
         "We enforce strict prompt grounding using system directives ('Use ONLY provided context. If missing, respond: I could not find the answer in the document'). Temperature is kept low, and context retrieval defaults to top k=7 cosine similarity chunks."),
        ("Q2: Why use RecursiveCharacterTextSplitter over simple CharacterSplitter?",
         "Simple CharacterSplitter splits blindly on character length, often truncating sentences mid-word or breaking logical paragraphs. Recursive character splitting tries [\"\\n\\n\", \"\\n\", \" \", \"\"] in order, preserving structural paragraph and sentence boundary semantics."),
        ("Q3: How do you handle API rate limits during bulk document ingestion?",
         "In vector store/DB.py, we implemented chunk-level batching (batch_size=50) with a 3-second sleep delay between API calls to prevent HTTP 429 exceptions on API free tiers."),
        ("Q4: Why select Mistral AI (mistral-embed / mistral-small) over OpenAI?",
         "Mistral provides top-tier 1024-dimensional dense embeddings with open-weights efficiency, significantly lower latency and cost per 1M tokens compared to OpenAI text-embedding-ada-002, while offering superior instruction compliance for precise context lookup.")
    ]
    for q, a in qa_pairs:
        story.append(Paragraph(f"<b>{q}</b>", bullet_style))
        story.append(Paragraph(f"<i>{a}</i>", ParagraphStyle('Ans', parent=body_style, leftIndent=25, spaceAfter=6)))

    story.append(Spacer(1, 10))

    # Section 2: Codebase Architecture & File Walkthrough
    story.append(Paragraph("2. Project Architecture & File-by-File Walkthrough", h1_style))
    story.append(Paragraph(
        "The project follows a modular 4-tier RAG pipeline: <b>Ingestion Tier</b> (PDF/Text extraction) &rarr; "
        "<b>Vectorization Tier</b> (Text chunking & Mistral Embeddings) &rarr; <b>Retrieval Tier</b> (Pinecone Cloud Vector Search) &rarr; "
        "<b>Synthesis Tier</b> (FastAPI / Gradio / Streamlit + Mistral LLM).", body_style
    ))

    arch_table_data = [
        [Paragraph("<b>File / Module</b>", body_style), Paragraph("<b>Role & Responsibility</b>", body_style), Paragraph("<b>Key Technologies</b>", body_style)],
        [Paragraph("<code>main.py</code>", code_style), Paragraph("Production FastAPI backend deployed on <b>Render Cloud</b> (<code>https://quickrag.onrender.com</code>). Serves <code>/api/chat</code> and <code>/api/upload</code> endpoints.", body_style), Paragraph("FastAPI, Pydantic, PineconeVectorStore, MistralAI", body_style)],
        [Paragraph("<code>app.py</code>", code_style), Paragraph("Local Streamlit UI demonstration with PDF drag-and-drop, Chroma local vector database creation, and MMR retrieval.", body_style), Paragraph("Streamlit, Chroma DB, MistralAIEmbeddings", body_style)],
        [Paragraph("<code>frontend_gradio.py</code>", code_style), Paragraph("Multi-tenant web dashboard deployed on <b>Hugging Face Spaces</b> (<code>https://huggingface.co/spaces/shresthtiwari/QuickRAG</code>). Connects browser file uploads to Render REST API.", body_style), Paragraph("Gradio, Requests (Multipart Upload)", body_style)],
        [Paragraph("<code>vector store/DB.py</code>", code_style), Paragraph("Standalone ingestion pipeline script. Scans <code>document loaders/</code> directory, parses PDFs/TXTs, chunks, and uploads to Pinecone.", body_style), Paragraph("LangChain PyPDFLoader, TextLoader, Pinecone", body_style)],
        [Paragraph("<code>create_database.py</code>", code_style), Paragraph("Script for building local Chroma vector database persisted in <code>chroma_db/</code>.", body_style), Paragraph("Chroma, LangChain, MistralAIEmbeddings", body_style)],
        [Paragraph("<code>retrievers/*</code>", code_style), Paragraph("Exploratory retrieval modules showcasing Arxiv API fetching (<code>arixv.py</code>), MMR diversity (<code>mmr.py</code>), and MultiQuery expansion (<code>multiquery.py</code>).", body_style), Paragraph("LangChain Retrievers, HuggingFaceEmbeddings", body_style)],
    ]

    t_arch = Table(arch_table_data, colWidths=[1.4 * inch, 3.8 * inch, 1.8 * inch])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 12))

    # Section 3: Technology Choices & Trade-Off Analysis
    story.append(Paragraph("3. Technology Choices & Alternatives Analysis", h1_style))
    
    tech_choices = [
        ("FastAPI vs. Flask / Django", 
         "FastAPI was selected for native async endpoint support, automatic request payload validation via Pydantic, and OpenAPI spec generation. Flask lacks built-in async validation, while Django adds unnecessary ORM overhead for vector microservices."),
        ("Pinecone Cloud vs. Local Chroma DB", 
         "Pinecone provides zero-management cloud vector index persistence with sub-100ms ANN vector lookups across millions of vectors. Chroma was used for offline prototyping, but lacks serverless cluster auto-scaling required for multi-tenant production."),
        ("Mistral AI vs. OpenAI", 
         "Mistral's <code>mistral-embed</code> model delivers dense 1024-dimensional semantic embeddings with high accuracy and lower cost/latency than OpenAI. Combined with <code>mistral-small-2506</code>, it offers superior cost-to-performance ratio."),
        ("RecursiveCharacterTextSplitter vs. Fixed Chunking", 
         "Recursive splitting systematically maintains context integrity by honoring document structural hierarchies (paragraphs &rarr; sentences &rarr; words). Overlap of 200 characters prevents semantic loss across chunk boundaries.")
    ]
    for tech, desc in tech_choices:
        story.append(Paragraph(f"<b>{tech}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 10))

    # Section 4: Fixes Implemented & Project Verification
    story.append(Paragraph("4. Code Verification & Key Fixes Implemented", h1_style))
    story.append(Paragraph("During project audit and verification, key code defects were identified and corrected:", body_style))

    fixes = [
        ("Fix 1: FastAPI Control Flow & Endpoint Registration Order",
         "In <code>main.py</code>, the <code>/api/upload</code> endpoint definition was placed below <code>if __name__ == '__main__':</code> and contained duplicate imports. Moving all route definitions before uvicorn startup ensures proper endpoint binding upon import."),
        ("Fix 2: Vector Persistence in Ingestion Endpoint",
         "In <code>main.py</code>'s <code>/api/upload</code> route, document ingestion was parsing chunks but commenting out <code>vectorstore.add_texts(all_chunks)</code>. We enabled live vector upserts to Pinecone, allowing uploaded files to instantly update context."),
        ("Fix 3: Embedding Model Mismatch & API Key Consistency",
         "In <code>app.py</code> and <code>create_database.py</code>, <code>OpenAIEmbeddings()</code> was hardcoded, causing runtime authentication errors because <code>OPENAI_API_KEY</code> was missing from <code>.env</code>. We standardized all scripts to <code>MistralAIEmbeddings(model=\"mistral-embed\")</code>."),
        ("Fix 4: API Throttling & Rate-Limit Safeguards",
         "In <code>vector store/DB.py</code>, bulk chunk uploads were refactored into batch size of 50 chunks with a 3-second throttle delay, avoiding HTTP 429 Rate Limit errors during large PDF processing.")
    ]
    for title, desc in fixes:
        story.append(Paragraph(f"<b>&check; {title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 10))

    # Section 5: Standard Project Q&A
    story.append(Paragraph("5. Core Project Questions & Technical Breakdown", h1_style))

    qna_data = [
        ("• Why did you build it?",
         "To engineer a production-ready, cloud-native RAG microservice that allows organizations to query unstructured PDF/TXT knowledge repositories with sub-second latency and zero hallucination."),
        ("• What problem does it solve?",
         "It resolves LLM context token limitations and knowledge cutoffs by dynamically retrieving domain-specific document snippets and injecting them into generation prompts."),
        ("• Which technologies did you use?",
         "Python 3.10+, FastAPI, LangChain, Pinecone Vector DB, Mistral AI (Embeddings & LLM), PyPDF, Pydantic, Gradio, Streamlit, and Python-dotenv."),
        ("• What challenges did you face?",
         "Overcoming free-tier rate limits during bulk vector ingestion (solved via batching and sleep intervals), handling PDF text extraction edge cases, and coordinating REST API contract compatibility with Gradio multi-part file uploads."),
        ("• What would you improve?",
         "Implement Hybrid Search (Sparse BM25 + Dense Vectors), Cohere Re-ranking for top-k precision, Pinecone Namespace isolation for per-user sessions, and asynchronous background ingestion using Celery and Redis.")
    ]
    for q, a in qna_data:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))

    story.append(Spacer(1, 10))

    # Section 6: Future Architectural Roadmap
    story.append(Paragraph("6. Architectural Roadmap & Future Upgrades", h1_style))
    roadmap_items = [
        "<b>Hybrid Vector Search:</b> Combine dense vector similarity (Mistral) with sparse keyword matching (BM25) via Reciprocal Rank Fusion (RRF) for specialized domain jargon.",
        "<b>Context Re-Ranking:</b> Integrate a re-ranker model (e.g., Cohere Rerank or BGE-Reranker) to evaluate retrieved candidates and pass only the top 3 high-confidence chunks to the LLM.",
        "<b>Asynchronous Worker Pipeline:</b> Offload heavy PDF parsing and vector calculation to Redis Task Queues and Celery workers to keep FastAPI endpoints non-blocking.",
        "<b>Multi-Tenant Session Isolation:</b> Dynamically allocate Pinecone namespaces per user session ID, preventing cross-tenant document context leaks."
    ]
    for item in roadmap_items:
        story.append(Paragraph(f"&bull; {item}", bullet_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=10))
    story.append(Paragraph("<i>Report generated automatically by Antigravity AI - QuickRAG Technical System Audit</i>", ParagraphStyle('FootNote', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748B"), alignment=1)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    build_pdf()
