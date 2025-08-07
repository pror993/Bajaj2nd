import spacy
import re

# Load spaCy's English model only once (global)
nlp = spacy.load("en_core_web_sm")

# Example slot patterns - extend as needed!
SLOT_PATTERNS = {
    "age": r"\b(\d{2})[- ]?(year[- ]old|yrs?|y/o)\b",
    "gender": r"\b(male|female|m|f)\b",
    "procedure": r"(knee|hip|bypass|cataract|surgery|replacement|fracture|angioplasty)[\w\s-]*",
    "location": r"in ([A-Za-z\s]+)",
    "policy_duration": r"(\d+)[- ]?(month|year|yr|mo)[s]?\b"
}

def extract_slots(text):
    slots = {}
    doc = nlp(text)

    # Regex extraction (simple demo—improve as needed)
    for slot, pattern in SLOT_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if slot == "age":
                slots["age"] = int(match.group(1))
            elif slot == "policy_duration":
                slots["policy_duration"] = match.group(0)
            else:
                slots[slot] = match.group(1) if match.groups() else match.group(0)

    # (Optional) Use spaCy NER for location, procedure, etc. if regex misses
    # e.g. look for GPE (places)
    if "location" not in slots:
        for ent in doc.ents:
            if ent.label_ == "GPE":
                slots["location"] = ent.text

    # Add more rules as you wish!
    return slots
