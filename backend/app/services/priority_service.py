import re


def _text(value: str | None) -> str:
    return " ".join((value or "").lower().split())


def _timeline_score(timeline: str) -> int:
    t = _text(timeline)

    if not t:
        return 0

    # Very urgent
    if any(
        phrase in t
        for phrase in [
            "this week",
            "within a week",
            "immediately",
            "urgent",
            "within days",
        ]
    ):
        return 25

    # 1–3 months
    if re.search(r"\b[1-3]\s*months?\b", t):
        return 22

    # 3–6 months
    if re.search(r"\b[4-6]\s*months?\b", t):
        return 15

    # 6–12 months
    if re.search(r"\b(6|7|8|9|10|11|12)\s*\+?\s*months?\b", t):
        return 8

    # More than a year / 1+ year
    if any(
        phrase in t
        for phrase in [
            "more than a year",
            "over a year",
            "1+ year",
            "1 year",
            "12+ months",
        ]
    ):
        return 3

    # Fallback for other timelines
    return 5


def _intent_score(message: str) -> int:
    m = _text(message)

    if not m:
        return 0

    # Strong negative / low-intent signals
    if any(
        phrase in m
        for phrase in [
            "not planning to buy",
            "not planning to purchase",
            "no immediate plan",
            "no immediate plans",
            "just browsing",
            "just exploring",
            "only exploring",
            "only researching",
            "just researching",
            "maybe later",
            "not sure if i will buy",
        ]
    ):
        return 5

    # Very strong buying intent
    if any(
        phrase in m
        for phrase in [
            "ready to buy",
            "ready to purchase",
            "want to buy",
            "want to purchase",
            "planning to buy",
            "planning to purchase",
            "finalizing",
            "ready to book",
            "want to book",
        ]
    ):
        return 30

    # Strong action intent
    if any(
        phrase in m
        for phrase in [
            "schedule a site visit",
            "schedule site visit",
            "book a site visit",
            "want a site visit",
            "visit the property",
            "schedule a visit",
            "negotiate",
            "negotiation",
            "shortlist",
            "shortlisting",
        ]
    ):
        return 25

    # Moderate intent
    if any(
        phrase in m
        for phrase in [
            "looking to buy",
            "looking to purchase",
            "interested in buying",
            "interested in purchasing",
            "looking for a property",
            "looking for an apartment",
            "looking for a flat",
        ]
    ):
        return 18

    # General property interest
    if any(
        phrase in m
        for phrase in [
            "interested",
            "considering",
            "want information",
            "send details",
            "share details",
            "show me",
        ]
    ):
        return 12

    return 5


def _budget_score(budget: float | None) -> int:
    # A clearly specified positive budget is useful,
    # but having a budget alone should not make someone HOT.
    if budget is None or budget <= 0:
        return 0

    return 15


def _requirement_score(requirement: str, message: str) -> int:
    r = _text(requirement)
    m = _text(message)

    if not r:
        return 0

    score = 5

    # More concrete requirement information
    if any(
        phrase in r
        for phrase in [
            "2 bhk",
            "3 bhk",
            "4 bhk",
            "1 bhk",
        ]
    ):
        score += 3

    if any(
        word in r
        for word in [
            "nagpur",
            "civil lines",
            "wardha road",
            "manish nagar",
            "location",
        ]
    ):
        score += 3

    if any(
        word in r
        for word in [
            "parking",
            "balcony",
            "garden",
            "pool",
            "swimming",
        ]
    ):
        score += 2

    # Requirement can also be clarified through the message.
    if any(
        phrase in m
        for phrase in [
            "budget",
            "bhk",
            "location",
            "parking",
        ]
    ):
        score += 2

    return min(score, 15)


def _engagement_score(message: str) -> int:
    m = _text(message)

    if not m:
        return 0

    if any(
        phrase in m
        for phrase in [
            "site visit",
            "schedule a visit",
            "call me",
            "callback",
            "send me details",
            "share details",
            "share properties",
            "show properties",
            "availability",
            "possession",
            "negotiate",
            "price negotiation",
        ]
    ):
        return 10

    if any(
        phrase in m
        for phrase in [
            "interested",
            "tell me more",
            "more details",
            "what options",
            "which properties",
        ]
    ):
        return 6

    return 2


def calculate_priority(
    timeline: str,
    budget: float,
    requirement: str,
    message: str,
) -> tuple[int, str]:

    intent = _intent_score(message)
    timeline_points = _timeline_score(timeline)
    budget_points = _budget_score(budget)
    requirement_points = _requirement_score(requirement, message)
    engagement = _engagement_score(message)

    score = (
        intent
        + timeline_points
        + budget_points
        + requirement_points
        + engagement
    )

    score = min(score, 100)

    if score >= 80:
        priority = "HOT"
    elif score >= 50:
        priority = "WARM"
    else:
        priority = "COLD"

    return score, priority