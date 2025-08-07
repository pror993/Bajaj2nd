import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assert GEMINI_API_KEY, "GEMINI_API_KEY not set in .env file"

# Set the API key for the Gemini SDK
genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-1.5-flash"  # or "gemini-1.5-pro"

def call_gemini(prompt, system="You are a helpful assistant. Always reply in valid JSON."):
    # Prepend the system prompt to the user prompt
    full_prompt = f"{system}\n{prompt}"
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(
        full_prompt,
        safety_settings={
            'HATE_SPEECH': 'block_none',
            'HARASSMENT': 'block_none',
            'SEXUAL': 'block_none',
            'DANGEROUS': 'block_none',
        },
        generation_config={
            "max_output_tokens": 512,
            "temperature": 0.2,
        }
    )
    try:
        return response.text.strip()
    except AttributeError:
        return response.candidates[0].text.strip()

def summarize_clauses(segments):
    """
    segments: list of dicts, e.g. [{clause_id, text, score}]
    Returns: list of dicts [{clause_id, summary}]
    """
    summaries = []
    for seg in segments:
        prompt = f"""Given the following insurance policy clause, write a one-sentence summary of the core rule or exclusion, in valid JSON as:
{{
  "clause_id": {seg['clause_id']},
  "summary": "<one-sentence summary>"
}}
Clause:
\"\"\"
{seg['text']}
\"\"\"
"""
        out = call_gemini(prompt)
        try:
            data = json.loads(out)
            summaries.append(data)
        except Exception:
            # If Gemini gives non-JSON, wrap manually
            summaries.append({
                "clause_id": seg["clause_id"],
                "summary": out
            })
    return summaries

def decide_with_chain_of_thought(summaries, slots, domain="insurance"):
    """
    Input:
        summaries: [{clause_id, summary}, ...]
        slots: extracted slot dict (e.g., {age: 46, procedure: "knee surgery", ...})
        domain: e.g., "insurance"
    Output:
        {
          "reasoning_trace": [...],
          "decision": "approved"|"rejected",
          "amount": int|null
        }
    """
    prompt = f"""
You are a decision engine for {domain} claims.
Given these extracted slot values (facts about the case):

{slots}

And the following clause summaries (policy rules or exclusions):

{summaries}

1. List your reasoning steps as an array, referencing clause_ids and slot facts.
2. Output your final decision as "approved" or "rejected".
3. Output the amount (numeric payout, or null if not applicable).

Return ONLY valid JSON as:
{{
  "reasoning_trace": [ "..." ],
  "decision": "approved"|"rejected",
  "amount": <number|null>
}}
"""
    out = call_gemini(prompt)
    import json
    try:
        result = json.loads(out)
    except Exception:
        result = {"reasoning_trace": [out], "decision": "unknown", "amount": None}
    return result

# Example usage:
if __name__ == "__main__":
    segments = [
        {"clause_id": 1, "text": "This policy does not cover knee surgery within 3 months of policy issue.", "score": 0.95},
        {"clause_id": 2, "text": "Pre-existing conditions are excluded from this insurance policy for 2 years.", "score": 0.89},
    ]
    print(summarize_clauses(segments))

