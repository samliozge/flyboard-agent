# agent/tools.py
import json
import os
from storage.store import save_ticket, save_followup

# kb.json'ı bir kere yükle, hafızada tut
# KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "kb.json")
KB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "kb.json")
with open(KB_PATH, "r", encoding="utf-8") as f:
    KB = json.load(f)

def search_kb(query: str, top_k: int = 5, filters: dict = None) -> dict:
    """KB'de keyword bazlı arama yapar."""
    query_words = query.lower().split()
    scored = []

    for entry in KB:
        text = (entry["title"] + " " + entry["content"]).lower()

        # Filter uygula
        if filters:
            if "audience" in filters:
                if entry["audience"] != filters["audience"]:
                    continue

        # Scoring
        score = sum(text.count(word) for word in query_words)

        if score > 0:
            scored.append({
                "id": entry["id"],
                "title": entry["title"],
                "score": score,
                "snippet": entry["content"][:200],
                "tags": entry["tags"]
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_k = min(top_k, 10)
    results = scored[:top_k]

    print(f"[TOOL] search_kb: '{query}' → {len(results)} sonuç")
    return {"results": results}

def create_ticket(title: str, body: str, priority: str) -> dict:
    """Yeni bir destek ticket'ı oluşturur."""
    assert priority in ("low", "medium", "high"), "Geçersiz priority"
    result = save_ticket(title, body, priority)
    print(f"[TOOL] create_ticket: {result['ticket_id']}")
    return result

def schedule_followup(datetime_iso: str, contact: str, channel: str) -> dict:
    """Bir followup planlar."""
    assert channel in ("email", "phone", "whatsapp"), "Geçersiz channel"
    result = save_followup(datetime_iso, contact, channel)
    print(f"[TOOL] schedule_followup: {result['followup_id']}")
    return result


# OpenAI'ye tanıtacağımız tool tanımları (JSON Schema)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "search_kb",
        "description": "Search the internal knowledge base when the user asks about Flyboard features, pricing, integrations, languages, onboarding, SLA, security, or troubleshooting.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "top_k": {"type": "integer", "default": 5, "maximum": 10},
                "filters": {
                    "type": "object",
                    "properties": {
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "audience": {
                            "type": "string",
                            "enum": ["customer", "internal"],
                            "description": "Filter by audience. Use 'customer' for most queries."
                        }
                    }
                }
            },
            "required": ["query"]
        }
    },
    {
        "type": "function",
        "name": "create_ticket",
        "description": "Create a support ticket when the user reports a bug, outage, or technical issue that needs human attention.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body": {"type": "string"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]}
            },
            "required": ["title", "body", "priority"]
        }
    },
    {
        "type": "function",
        "name": "schedule_followup",
        "description": "Schedule a follow-up call or message with a contact via a specific channel.",
        "parameters": {
            "type": "object",
            "properties": {
                "datetime_iso": {"type": "string", "description": "ISO 8601 datetime e.g. 2026-05-08T10:30:00"},
                "contact": {"type": "string"},
                "channel": {"type": "string", "enum": ["email", "phone", "whatsapp"]}
            },
            "required": ["datetime_iso", "contact", "channel"]
        }
    }
]

# Tool adına göre fonksiyonu çalıştıran router
TOOL_ROUTER = {
    "search_kb": search_kb,
    "create_ticket": create_ticket,
    "schedule_followup": schedule_followup
}