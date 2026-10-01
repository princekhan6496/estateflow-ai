from datetime import date
import re
from app.models.models import Property, Lead


def _deadline_year(timeline: str) -> int | None:
    text = timeline.lower().strip()
    if "immediate" in text or "this week" in text:
        months = 1
    else:
        match = re.search(r"(\d+)\s*(?:-|to)?\s*(\d+)?\s*months?", text)
        if not match:
            return None
        months = int(match.group(2) or match.group(1))
    today = date.today()
    total_month = today.month - 1 + months
    return today.year + total_month // 12


def _possession_year(value: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", value or "")
    return int(match.group(1)) if match else None


def match_property(lead: Lead, prop: Property):
    score = 0
    reasons: list[str] = []
    mismatches: list[str] = []

    if prop.price <= lead.budget:
        score += 30
        reasons.append("Within budget")
    else:
        mismatches.append("Above budget")

    if prop.bhk in (lead.bhk or []):
        score += 25
        reasons.append("BHK matches")
    else:
        mismatches.append(f"BHK {prop.bhk} not in current preference")

    lead_location = lead.location.lower().strip()
    prop_location = prop.location.lower().strip()
    if lead_location in prop_location or prop_location in lead_location:
        score += 20
        reasons.append("Preferred location")
    else:
        mismatches.append("Location differs")

    if not lead.parking_required:
        score += 15
        reasons.append("Parking requirement is flexible")
    elif prop.parking_available:
        score += 15
        reasons.append("Parking available")
    else:
        mismatches.append("Parking required but unavailable")

    deadline_year = _deadline_year(lead.timeline)
    possession_year = _possession_year(prop.possession_date)
    if deadline_year is not None and possession_year is not None:
        if possession_year <= deadline_year:
            score += 10
            reasons.append("Possession fits the stated timeline")
        else:
            mismatches.append("Possession is later than the stated timeline")
    else:
        mismatches.append("Possession timeline could not be verified")

    return score, reasons, mismatches
