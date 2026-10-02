import json
import httpx
from fastapi import HTTPException
from app.db.database import settings
from app.schemas.schemas import AIAnalysis, ChangeResponse, ChatResponse
from app.services.normalization import normalize_requirement_change, normalize_ai_budget

BASE = "https://api.groq.com/openai/v1/chat/completions"
SCOPE_FALLBACK = "I can only help with this lead's sales context, requirements, interactions, properties, objections, and recommended actions."

# Deterministic guard for obviously unrelated requests. Ambiguous sales questions are allowed through.
OUT_OF_SCOPE_PATTERNS = (
    "write a python", "write code", "javascript program", "tell me a joke",
    "prime minister", "president of", "weather", "stock price", "recipe",
    "solve this math", "who won the", "translate this"
)


def is_obviously_out_of_scope(question: str) -> bool:
    normalized = " ".join(question.lower().split())
    return any(pattern in normalized for pattern in OUT_OF_SCOPE_PATTERNS)


def _call(system: str, user: str):
    if not settings.GROQ_API_KEY:
        raise HTTPException(503, "AI service is not configured. Add GROQ_API_KEY to enable AI features.")
    payload = {
        "model": settings.GROQ_MODEL,
        "temperature": 0,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
    }
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(BASE, headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise HTTPException(502, "The AI service returned an invalid response. Please retry.") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(504, "The AI service timed out. Please retry.") from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(429, "The AI service is temporarily rate-limited. Please retry shortly.") from exc
        raise HTTPException(502, "The AI service is temporarily unavailable. Please retry.") from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(502, "The AI service returned an unexpected response. Please retry.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, "The AI service is temporarily unavailable. Please retry.") from exc


def analyze_lead(context: str):
    system = """
You analyze a real-estate sales lead.

Return ONLY a valid JSON object.

The JSON MUST contain exactly these fields:

{
  "summary": "short summary of the lead",
  "intent": "customer's buying intent",
  "key_requirements": ["requirement 1", "requirement 2"],
  "objections": ["objection 1", "objection 2"],
  "recommended_next_action": "specific next action for the salesperson",
  "suggested_response": "short response the salesperson can send to the customer"
}

Rules:
- summary must be a string.
- intent must be a string.
- key_requirements must ALWAYS be an array of strings.
- objections must ALWAYS be an array of strings. Use [] if there are no objections.
- recommended_next_action must be a string.
- suggested_response must be a string.
- Use ONLY facts from the supplied context.
- Never invent age, income, family, profession, availability, property features, preferences, or conversation history.
- Consider the complete interaction history.
- When re-analyzing, generate a fresh analysis based on the current lead and latest interactions.
- Do not copy or rely on a previous AI analysis.
- Keep the response concise.
"""

    obj = _call(system, context)

    try:
        return AIAnalysis.model_validate(obj)

    except Exception as exc:
        raise HTTPException(
            502,
            "The AI service returned invalid lead analysis. Please retry."
        ) from exc


def extract_changes(current: str, interaction: str):
    system = """Extract ONLY explicit changes to the customer's CURRENT real-estate requirements. Return ONLY JSON {changes:[{field,old_value,new_value,reason}]}. Supported fields are bhk, budget, location, timeline, parking_required. Do not infer unstated changes. Budget must be returned as INR numeric value, not lakh units. BHK must be an integer list."""
    obj = _call(system, f"CURRENT PROFILE:\n{current}\n\nNEW INTERACTION:\n{interaction}")
    try:
        parsed = ChangeResponse.model_validate(obj)
        # Normalize every proposed value before it can be stored or applied.
        for change in parsed.changes:
            if change.field == "budget":
                change.new_value = normalize_ai_budget(change.new_value)
            else:
                change.new_value = normalize_requirement_change(change.field, change.new_value)
        return parsed
    except Exception as exc:
        raise HTTPException(502, "Could not safely parse requirement changes. Please review the interaction manually.") from exc


def chat(context: str, question: str):
    if is_obviously_out_of_scope(question):
        return SCOPE_FALLBACK
    system = f"""You are a lead-specific real-estate sales assistant. Answer ONLY questions about the selected lead, supplied requirements/interactions, matched properties, objections, sales actions, and suggested responses. If a requested fact is absent from the context, say exactly: 'I don't have that information in the available lead data.' Do not use outside knowledge. For unrelated questions, respond with: {SCOPE_FALLBACK}
Return ONLY valid JSON in this exact format:
{{
  "answer": "..."
}}
Do not return markdown, code fences, extra keys, or explanatory text."""
    obj = _call(system, f"LEAD CONTEXT:\n{context}\n\nQUESTION:\n{question}")
    try:
        return ChatResponse.model_validate(obj).answer.strip()
    except Exception as exc:
        raise HTTPException(502, "AI assistant returned an invalid response. Please try again.") from exc
