
from fastapi import FastAPI, UploadFile, File, Body
from pydantic import BaseModel
import shutil
import os

from core.intake import extract_slots
from core.ingest import ingest_document, build_faiss_index
from core.retrieval import retrieve_relevant_segments
from core.llm import summarize_clauses, decide_with_chain_of_thought
from core.rules import apply_rules
from core.assemble import build_final_response
from core.utils import save_query_result, load_query_result

app = FastAPI()

DOCS_DIR = "data"
os.makedirs(DOCS_DIR, exist_ok=True)

# Ingest endpoint
@app.post("/ingest_document")
def ingest_document_api(file: UploadFile = File(...)):
    file_ext = file.filename.split(".")[-1]
    save_path = os.path.join(DOCS_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    segments, embeddings = ingest_document(save_path)
    index = build_faiss_index(embeddings)  # For demo, overwrites for latest doc
    return {"doc_id": file.filename, "segments_count": len(segments)}

# Query & store output
class QueryRequest(BaseModel):
    query: str
    domain: str = "insurance"

@app.post("/process_query")
def process_query(req: QueryRequest):
    slots = extract_slots(req.query)
    retrieved = retrieve_relevant_segments(req.query, top_k=5)
    summaries = summarize_clauses(retrieved)
    decision = decide_with_chain_of_thought(summaries, slots, domain=req.domain)
    rules = apply_rules(slots, decision)
    response = build_final_response(
        req.query, req.domain, slots, retrieved, summaries, decision, rules
    )
    query_id = save_query_result(response)
    return {"query_id": query_id}

# View endpoints
@app.get("/get_summaries/{query_id}")
def get_summaries(query_id: str):
    result = load_query_result(query_id)
    return {"summaries": result["summaries"]}

@app.get("/get_chain_of_thought/{query_id}")
def get_chain_of_thought(query_id: str):
    result = load_query_result(query_id)
    return {
        "reasoning_trace": result.get("reasoning_trace"),
        "llm_decision": result.get("llm_decision")
    }

@app.get("/get_rules/{query_id}")
def get_rules(query_id: str):
    result = load_query_result(query_id)
    return {"rules": result.get("rules")}

@app.get("/get_full_result/{query_id}")
def get_full_result(query_id: str):
    return load_query_result(query_id)
