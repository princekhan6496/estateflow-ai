from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120))
    bhk: Mapped[list] = mapped_column(JSON, default=list)
    budget: Mapped[float] = mapped_column(Float)
    timeline: Mapped[str] = mapped_column(String(80))
    parking_required: Mapped[bool] = mapped_column(Boolean, default=False)
    property_requirement: Mapped[str] = mapped_column(Text)
    customer_message: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(10), default="COLD")
    lead_score: Mapped[int] = mapped_column(Integer, default=0)
    ai_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    ai_analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    interactions = relationship("Interaction", back_populates="lead", cascade="all, delete-orphan")

class Property(Base):
    __tablename__ = "properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    property_code: Mapped[str] = mapped_column(String(30), unique=True)
    project_name: Mapped[str] = mapped_column(String(120))
    developer: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(120))
    bhk: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    carpet_area: Mapped[int] = mapped_column(Integer)
    parking_available: Mapped[bool] = mapped_column(Boolean)
    possession_date: Mapped[str] = mapped_column(String(50))
    floor: Mapped[int] = mapped_column(Integer)
    total_floors: Mapped[int] = mapped_column(Integer)
    amenities: Mapped[list] = mapped_column(JSON, default=list)
    availability: Mapped[str] = mapped_column(String(50), default="Available")
    description: Mapped[str] = mapped_column(Text)

class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(30))
    note: Mapped[str] = mapped_column(Text)
    ai_extracted_changes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    customer_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    lead = relationship("Lead", back_populates="interactions")

class LeadProperty(Base):
    __tablename__ = "lead_properties"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"))
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    match_score: Mapped[int] = mapped_column(Integer)
    match_reasons: Mapped[list] = mapped_column(JSON, default=list)
    mismatch_reasons: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(30), default="Recommended")
    customer_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
