def calculate_priority(timeline: str, budget: float, requirement: str, message: str) -> tuple[int, str]:
    t = timeline.lower()
    score = 0
    if "week" in t or "month" in t and any(x in t for x in ["1", "2", "3"]): score += 30
    elif "3" in t or "4" in t or "5" in t or "6" in t: score += 20
    else: score += 5
    if budget and budget > 0: score += 15
    if requirement.strip(): score += 15
    strong = ["buy", "purchase", "ready", "final", "urgent", "visit", "this week", "immediately"]
    if any(x in message.lower() for x in strong): score += 20
    if "parking" in message.lower() or "location" in message.lower(): score += 5
    if score >= 80: return min(score, 100), "HOT"
    if score >= 65: return score, "WARM"
    return score, "COLD"
