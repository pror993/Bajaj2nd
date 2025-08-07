import pdfplumber
from docx import Document
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

def pdf_to_segments(pdf_path):
    segments = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                paras = [p.strip() for p in text.split('\n\n') if p.strip()]
                segments.extend(paras)
    return segments

def docx_to_segments(docx_path):
    doc = Document(docx_path)
    return [para.text.strip() for para in doc.paragraphs if para.text.strip()]

def ingest_document(file_path):
    ext = file_path.lower().split('.')[-1]
    if ext == "pdf":
        segments = pdf_to_segments(file_path)
    elif ext == "docx":
        segments = docx_to_segments(file_path)
    else:
        raise ValueError("Unsupported file type")
    # Generate embeddings
    embeddings = EMBED_MODEL.encode(segments)
    # Save segments + embeddings (for demo: numpy arrays + .txt)
    os.makedirs("models", exist_ok=True)
    np.save("models/embeddings.npy", embeddings)
    with open("models/segments.txt", "w", encoding="utf8") as f:
        for seg in segments:
            f.write(seg + "\n")
    return segments, embeddings

def build_faiss_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))
    faiss.write_index(index, "models/faiss.index")
    return index
