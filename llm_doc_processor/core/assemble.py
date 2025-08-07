def build_final_response(query, domain, slots, retrieved, summaries, decision, rules):
    return {
        "query": query,
        "domain": domain,
        "slots": slots,
        "retrieved_clauses": retrieved,
        "summaries": summaries,
        "reasoning_trace": decision.get("reasoning_trace", []),
        "llm_decision": {
            "decision": decision.get("decision"),
            "amount": decision.get("amount")
        },
        "rules": rules
    }
