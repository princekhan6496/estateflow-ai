from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.db.database import get_db
from app.models.models import Lead, Property, Interaction, LeadProperty
from app.schemas.schemas import LeadCreate, LeadPatch, InteractionCreate, ChatRequest
from app.services.priority_service import calculate_priority
from app.services.matching_service import match_property
from app.services.ai_service import analyze_lead, extract_changes, chat
from app.services.normalization import normalize_budget, normalize_ai_budget, normalize_requirement_change, ALLOWED_REQUIREMENT_FIELDS

router = APIRouter(prefix="/api")
VALID_STATUSES = {"Recommended", "Shortlisted", "Shared", "Site Visit Scheduled", "Visited", "Interested", "Not Interested"}


def lead_context(db: Session, lead: Lead) -> str:
    interactions = db.scalars(select(Interaction).where(Interaction.lead_id == lead.id).order_by(Interaction.created_at)).all()
    matches = db.scalars(select(LeadProperty).where(LeadProperty.lead_id == lead.id).order_by(LeadProperty.match_score.desc()).limit(5)).all()
    props = {p.id: p for p in db.scalars(select(Property).where(Property.id.in_([m.property_id for m in matches]))).all()} if matches else {}
    return (
        f"Lead: {lead.name}\n"
        f"Current requirements: BHK={lead.bhk}; budget INR={lead.budget}; parking_required={lead.parking_required}; "
        f"location={lead.location}; timeline={lead.timeline}; property_requirement={lead.property_requirement}\n"
        f"Customer message: {lead.customer_message}\n"
        f"Analysis: {lead.ai_analysis or 'not analyzed'}\n"
        f"Interactions: {[{'type': i.type, 'note': i.note} for i in interactions]}\n"
        f"Matched properties: {[{'code': props[m.property_id].property_code, 'project': props[m.property_id].project_name, 'price_inr': props[m.property_id].price, 'score': m.match_score, 'reasons': m.match_reasons, 'mismatches': m.mismatch_reasons} for m in matches if m.property_id in props]}"
    )


def recompute(db: Session, lead: Lead):
    existing = {row.property_id: row.status for row in db.scalars(select(LeadProperty).where(LeadProperty.lead_id == lead.id)).all()}
    db.execute(delete(LeadProperty).where(LeadProperty.lead_id == lead.id))
    properties = db.scalars(select(Property)).all()
    for prop in properties:
        score, reasons, mismatches = match_property(lead, prop)
        if score >= 45:
            db.add(LeadProperty(
                lead_id=lead.id,
                property_id=prop.id,
                match_score=score,
                match_reasons=reasons,
                mismatch_reasons=mismatches,
                status=existing.get(prop.id, "Recommended"),
            ))


@router.get('/health')
def health():
    return {'status': 'ok'}


@router.get('/leads')
def list_leads(db: Session = Depends(get_db)):
    return db.scalars(select(Lead).order_by(Lead.lead_score.desc(), Lead.created_at.desc())).all()


@router.post('/leads')
def create_lead(data: LeadCreate, db: Session = Depends(get_db)):
    budget = normalize_budget(data.budget)
    score, priority = calculate_priority(data.timeline, budget, data.property_requirement, data.customer_message)
    lead = Lead(**data.model_dump(exclude={"budget"}), budget=budget, lead_score=score, priority=priority)
    db.add(lead)
    db.flush()
    recompute(db, lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get('/leads/{lead_id}')
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, 'Lead not found')
    return lead


@router.patch('/leads/{lead_id}')
def patch_lead(lead_id: int, data: LeadPatch, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, 'Lead not found')
    values = data.model_dump(exclude_none=True)
    if "budget" in values:
        values["budget"] = normalize_budget(values["budget"])
    if "bhk" in values:
        values["bhk"] = normalize_requirement_change("bhk", values["bhk"])
    for key, value in values.items():
        setattr(lead, key, value)
    lead.lead_score, lead.priority = calculate_priority(lead.timeline, lead.budget, lead.property_requirement, lead.customer_message)
    recompute(db, lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get('/leads/{lead_id}/interactions')
def interactions(lead_id: int, db: Session = Depends(get_db)):
    if not db.get(Lead, lead_id):
        raise HTTPException(404, 'Lead not found')
    return db.scalars(select(Interaction).where(Interaction.lead_id == lead_id).order_by(Interaction.created_at.desc())).all()


@router.post('/leads/{lead_id}/interactions')
def add_interaction(lead_id: int, data: InteractionCreate, db: Session = Depends(get_db)):
    if not db.get(Lead, lead_id):
        raise HTTPException(404, 'Lead not found')
    item = Interaction(lead_id=lead_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post('/leads/{lead_id}/analyze')
def analyze(lead_id: int, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, 'Lead not found')
    result = analyze_lead(lead_context(db, lead))
    lead.ai_analysis = result.model_dump()
    lead.ai_analyzed_at = datetime.utcnow()
    db.commit()
    return result


@router.post('/leads/{lead_id}/chat')
def lead_chat(lead_id: int, data: ChatRequest, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, 'Lead not found')
    return {'answer': chat(lead_context(db, lead), data.message)}


@router.post('/leads/{lead_id}/extract-requirement-changes')
def changes(lead_id: int, interaction_id: int = Query(...), db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    interaction = db.get(Interaction, interaction_id)
    if not lead or not interaction or interaction.lead_id != lead_id:
        raise HTTPException(404, 'Lead or interaction not found')
    try:
        result = extract_changes(lead_context(db, lead), interaction.note)
    except HTTPException:
        raise
    interaction.ai_extracted_changes = result.model_dump()
    db.commit()
    return result


@router.post('/leads/{lead_id}/apply-requirement-changes')
def apply_changes(lead_id: int, interaction_id: int = Query(...), db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    interaction = db.get(Interaction, interaction_id)
    if not lead or not interaction or interaction.lead_id != lead_id:
        raise HTTPException(404, 'Lead or interaction not found')

    changes = (interaction.ai_extracted_changes or {}).get('changes', [])
    if not isinstance(changes, list):
        raise HTTPException(422, 'No valid proposed requirement changes are available.')

    try:
        normalized_changes = []
        for change in changes:
            field = change.get('field')
            if field not in ALLOWED_REQUIREMENT_FIELDS:
                raise ValueError(f"Unsupported requirement field: {field}")
            new_value = normalize_ai_budget(change.get('new_value')) if field == 'budget' else normalize_requirement_change(field, change.get('new_value'))
            normalized_changes.append((field, new_value))
    except (TypeError, AttributeError, ValueError) as exc:
        raise HTTPException(422, f'Proposed requirement change failed validation: {exc}') from exc

    for field, value in normalized_changes:
        setattr(lead, field, value)

    lead.lead_score, lead.priority = calculate_priority(lead.timeline, lead.budget, lead.property_requirement, lead.customer_message)
    recompute(db, lead)
    db.commit()
    db.refresh(lead)
    return {'lead': lead, 'message': 'Profile updated and recommendations refreshed.'}


@router.get('/leads/{lead_id}/matches')
def matches(lead_id: int, db: Session = Depends(get_db)):
    if not db.get(Lead, lead_id):
        raise HTTPException(404, 'Lead not found')
    rows = db.scalars(select(LeadProperty).where(LeadProperty.lead_id == lead_id).order_by(LeadProperty.match_score.desc()).limit(20)).all()
    return [
        {
            'id': r.id,
            'lead_id': r.lead_id,
            'property_id': r.property_id,
            'match_score': r.match_score,
            'match_reasons': r.match_reasons,
            'mismatch_reasons': r.mismatch_reasons,
            'status': r.status,
            'property': db.get(Property, r.property_id),
        }
        for r in rows
    ]


@router.patch('/leads/{lead_id}/properties/{property_id}')
def update_property_status(lead_id: int, property_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    if status not in VALID_STATUSES:
        raise HTTPException(422, f'Invalid property status. Allowed: {sorted(VALID_STATUSES)}')
    if not db.get(Lead, lead_id):
        raise HTTPException(404, 'Lead not found')
    if not db.get(Property, property_id):
        raise HTTPException(404, 'Property not found')
    row = db.scalar(select(LeadProperty).where(LeadProperty.lead_id == lead_id, LeadProperty.property_id == property_id))
    if not row:
        raise HTTPException(404, 'Lead-property match not found')
    row.status = status
    db.commit()
    db.refresh(row)
    return row


@router.get('/properties')
def properties(search: str | None = None, bhk: int | None = None, max_price: float | None = None, location: str | None = None, parking: bool | None = None, db: Session = Depends(get_db)):
    q = select(Property)
    if search:
        q = q.where((Property.property_code.ilike(f'%{search}%')) | (Property.project_name.ilike(f'%{search}%')))
    if bhk:
        q = q.where(Property.bhk == bhk)
    if max_price:
        q = q.where(Property.price <= normalize_budget(max_price))
    if location:
        q = q.where(Property.location.ilike(f'%{location}%'))
    if parking is not None:
        q = q.where(Property.parking_available == parking)
    return db.scalars(q.order_by(Property.price)).all()


@router.get('/properties/{property_id}')
def property_detail(property_id: int, db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, 'Property not found')
    return prop


@router.get('/properties/{property_id}/matching-leads')
def matching_leads(property_id: int, db: Session = Depends(get_db)):
    if not db.get(Property, property_id):
        raise HTTPException(404, 'Property not found')
    rows = db.scalars(select(LeadProperty).where(LeadProperty.property_id == property_id).order_by(LeadProperty.match_score.desc())).all()
    return [{'id': r.id, 'lead_id': r.lead_id, 'property_id': r.property_id, 'match_score': r.match_score, 'status': r.status, 'lead': db.get(Lead, r.lead_id)} for r in rows]
