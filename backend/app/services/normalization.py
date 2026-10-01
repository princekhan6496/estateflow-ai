from typing import Any

ALLOWED_REQUIREMENT_FIELDS = {
    "bhk",
    "budget",
    "location",
    "timeline",
    "parking_required",
}


def normalize_budget(value: Any) -> float:
    """Canonical API/database budget representation: INR."""
    if isinstance(value, bool):
        raise ValueError("Budget must be numeric")
    if isinstance(value, str):
        cleaned = value.strip().replace("₹", "").replace(",", "")
        if cleaned.upper().endswith("L"):
            raise ValueError("API budget must be INR; convert lakh input before sending")
        amount = float(cleaned)
    else:
        amount = float(value)
    if amount <= 0:
        raise ValueError("Budget must be greater than zero")
    return amount


def normalize_ai_budget(value: Any) -> float:
    """Normalize an AI proposal to INR; small numeric values are treated as lakh."""
    if isinstance(value, bool):
        raise ValueError("Budget must be numeric")
    if isinstance(value, str):
        cleaned = value.strip().replace("₹", "").replace(",", "").upper()
        if cleaned.endswith("L"):
            amount = float(cleaned[:-1]) * 100000
        else:
            amount = float(cleaned)
    else:
        amount = float(value)
    if amount <= 0:
        raise ValueError("Budget must be greater than zero")
    if amount < 100000:
        amount *= 100000
    return amount


def display_lakh(value: float) -> str:
    return f"₹{value / 100000:.1f}L".replace(".0L", "L")


def normalize_bhk(value: Any) -> list[int]:
    if not isinstance(value, list) or not value:
        raise ValueError("BHK must be a non-empty integer list")
    result = sorted({int(x) for x in value})
    if any(x <= 0 or x > 10 for x in result):
        raise ValueError("BHK values are out of range")
    return result


def normalize_requirement_change(field: str, value: Any) -> Any:
    if field not in ALLOWED_REQUIREMENT_FIELDS:
        raise ValueError(f"Unsupported requirement field: {field}")
    if field == "bhk":
        return normalize_bhk(value)
    if field == "budget":
        return normalize_budget(value)
    if field == "parking_required":
        if not isinstance(value, bool):
            raise ValueError("parking_required must be boolean")
        return value
    if field in {"location", "timeline"}:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip()
    raise ValueError(f"Unsupported requirement field: {field}")
