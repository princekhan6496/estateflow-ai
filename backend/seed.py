from sqlalchemy import select, delete
from app.db.database import SessionLocal
from app.models.models import Lead, Property, LeadProperty
from app.services.priority_service import calculate_priority
from app.services.matching_service import match_property

PROJECTS = [
    ('Green Heights','UrbanNest','Nagpur',2,6200000,950,True),
    ('Green Heights','UrbanNest','Nagpur',3,8800000,1250,True),
    ('Skyline Residency','Apex Build','Nagpur',3,8400000,1180,True),
    ('Riverstone','Civic Homes','Wardha Road',4,9800000,1550,True),
    ('Palm Court','Nova Living','Manish Nagar',2,5800000,900,False),
    ('Palm Court','Nova Living','Manish Nagar',3,7600000,1180,True),
    ('Metro View','Axis Realty','Nagpur',2,5400000,870,True),
    ('Metro View','Axis Realty','Nagpur',3,7900000,1160,True),
    ('Lakeview Enclave','BlueStone','Besa',3,8600000,1200,True),
    ('Lakeview Enclave','BlueStone','Besa',4,10400000,1500,True),
    ('Central Park','Maven','Civil Lines',2,7200000,920,True),
    ('Central Park','Maven','Civil Lines',3,9100000,1280,True),
]

SAMPLES = [
    ('Rahul Khan','Nagpur',[3],9000000,'3 months',True,'Family apartment','Looking for a 3 BHK in Nagpur. Parking is mandatory and I want to visit soon.'),
    ('Amit Sharma','Manish Nagar',[2,3],8000000,'1-3 months',True,'2 or 3 BHK','Need a good apartment close to work.'),
    ('Sneha Patel','Besa',[3],9500000,'6 months',True,'3 BHK','Exploring options, not urgent.'),
    ('Neha Verma','Wardha Road',[2],6500000,'1 month',False,'2 BHK','Ready to shortlist this week.'),
    ('Arjun Mehta','Civil Lines',[3],10000000,'3 months',True,'Premium 3 BHK','Please share serious options.'),
    ('Priya Shah','Nagpur',[2],6000000,'6+ months',False,'2 BHK','Just researching prices.'),
    ('Karan Joshi','Nagpur',[4],11000000,'2 months',True,'4 BHK','Need more space and parking.'),
    ('Riya Singh','Besa',[3,4],10000000,'3 months',True,'3 or 4 BHK','Interested in visiting properties.'),
]


def recompute(db, lead):
    existing = {row.property_id: row.status for row in db.scalars(select(LeadProperty).where(LeadProperty.lead_id == lead.id)).all()}
    db.execute(delete(LeadProperty).where(LeadProperty.lead_id == lead.id))
    for prop in db.scalars(select(Property)).all():
        score, reasons, mismatches = match_property(lead, prop)
        if score >= 45:
            db.add(LeadProperty(
                lead_id=lead.id,
                property_id=prop.id,
                match_score=score,
                match_reasons=reasons,
                mismatch_reasons=mismatches,
                status=existing.get(prop.id, 'Recommended'),
            ))


def seed():
    db = SessionLocal()
    try:
        # Idempotent upsert by stable demo property code.
        for i in range(4):
            for j, item in enumerate(PROJECTS):
                project, developer, location, bhk, price, area, parking = item
                code = f'RE-{i+1}{j+1:02d}'
                prop = db.scalar(select(Property).where(Property.property_code == code))
                values = dict(property_code=code, project_name=project, developer=developer, location=location, bhk=bhk,
                              price=price + i * 300000, carpet_area=area, parking_available=parking,
                              possession_date='2027', floor=(j % 8) + 1, total_floors=12,
                              amenities=['Gym', 'Clubhouse', 'Security'], availability='Available',
                              description=f'{bhk} BHK residence at {project} in {location}.')
                if prop:
                    for key, value in values.items():
                        setattr(prop, key, value)
                else:
                    db.add(Property(**values))
        db.flush()

        for sample in SAMPLES:
            name, location, bhk, budget, timeline, parking, requirement, message = sample
            lead = db.scalar(select(Lead).where(Lead.name == name))
            score, priority = calculate_priority(timeline, budget, requirement, message)
            values = dict(name=name, location=location, bhk=bhk, budget=budget, timeline=timeline,
                          parking_required=parking, property_requirement=requirement, customer_message=message,
                          lead_score=score, priority=priority)
            if lead:
                for key, value in values.items():
                    setattr(lead, key, value)
            else:
                lead = Lead(**values)
                db.add(lead)
                db.flush()

        db.commit()

        # Matching is deterministic and does not call Groq.
        for lead in db.scalars(select(Lead)).all():
            recompute(db, lead)
        db.commit()
        print('Seed complete:', db.query(Property).count(), 'properties,', db.query(Lead).count(), 'leads,', db.query(LeadProperty).count(), 'matches')
    finally:
        db.close()


if __name__ == '__main__':
    seed()
