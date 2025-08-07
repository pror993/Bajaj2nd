def apply_rules(slots, llm_decision):
    """
    slots: extracted slots dict (e.g., {"age": 46, "policy_duration": "3-month-old", ...})
    llm_decision: {"reasoning_trace": [...], "decision": "approved"|"rejected", "amount": number}
    
    Returns:
        {
            "final_decision": ...,
            "final_amount": ...,
            "rule_events": [{rule, result, notes}],
            "overriden": True/False
        }
    """
    rule_events = []
    final_decision = llm_decision["decision"]
    final_amount = llm_decision.get("amount", None)

    # Rule 1: Waiting period (example: policy duration >= 3 months)
    waiting_period_ok = None
    try:
        dur = slots.get("policy_duration", "")
        months = 0
        # Handles both "3-month-old" and "3 months"
        import re
        match = re.search(r"(\d+)[- ]?(month|mo)", dur)
        if match:
            months = int(match.group(1))
        waiting_period_ok = months >= 3
    except Exception:
        waiting_period_ok = None

    if waiting_period_ok is not None:
        if not waiting_period_ok:
            rule_events.append({
                "rule": "waiting_period",
                "result": "failed",
                "notes": "Policy duration less than required 3 months"
            })
            final_decision = "rejected"
            final_amount = 0
        else:
            rule_events.append({
                "rule": "waiting_period",
                "result": "passed",
                "notes": "Policy duration meets waiting period"
            })

    # Rule 2: Age limit (example: age <= 80)
    if "age" in slots:
        try:
            age = int(slots["age"])
            if age > 80:
                rule_events.append({
                    "rule": "age_limit",
                    "result": "failed",
                    "notes": "Claimant over age limit"
                })
                final_decision = "rejected"
                final_amount = 0
            else:
                rule_events.append({
                    "rule": "age_limit",
                    "result": "passed",
                    "notes": "Age within allowed range"
                })
        except Exception:
            rule_events.append({
                "rule": "age_limit",
                "result": "unknown",
                "notes": "Could not parse age"
            })

    # Rule 3: (Optional) Exclusion check—add your own rules
    # Example: If procedure contains "cosmetic", reject
    if "procedure" in slots and "cosmetic" in slots["procedure"].lower():
        rule_events.append({
            "rule": "procedure_exclusion",
            "result": "failed",
            "notes": "Cosmetic procedures are not covered"
        })
        final_decision = "rejected"
        final_amount = 0

    # Rule 4: (Optional) Maximum payout
    # Example: If LLM amount > 100000, cap it
    if final_amount and final_amount > 100000:
        rule_events.append({
            "rule": "max_payout_limit",
            "result": "capped",
            "notes": "Payout capped at 100000"
        })
        final_amount = 100000

    # Add more rules as needed...

    return {
        "final_decision": final_decision,
        "final_amount": final_amount,
        "rule_events": rule_events,
        "overriden": final_decision != llm_decision["decision"]
    }
