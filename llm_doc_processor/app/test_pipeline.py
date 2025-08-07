from core.intake import extract_slots
from core.ingest import ingest_document, build_faiss_index
from core.retrieval import retrieve_relevant_segments
from core.llm import summarize_clauses, decide_with_chain_of_thought

if __name__ == "__main__":
    sample_query = "46-year-old male, knee surgery in Pune, 3-month-old insurance policy"
    slots = extract_slots(sample_query)
    print("Extracted slots:", slots)

    file_path = "data/HDFHLIP23024V072223.pdf"
    segments, embeddings = ingest_document(file_path)
    print("Extracted segments:", segments[:5])
    print("Embeddings shape:", embeddings.shape)
    index = build_faiss_index(embeddings)
    print("FAISS index built.")

    results = retrieve_relevant_segments(sample_query, top_k=3)
    for res in results:
        print(res)

    summaries = summarize_clauses(results)
    for summ in summaries:
        print(summ)

    decision = decide_with_chain_of_thought(summaries, slots, domain="insurance")
    print("Reasoning and decision:", decision)