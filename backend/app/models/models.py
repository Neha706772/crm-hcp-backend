from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
import enum

Base = declarative_base()


class InteractionType(str, enum.Enum):
    meeting = "meeting"
    call = "call"
    email = "email"
    conference = "conference"
    webinar = "webinar"


class SentimentType(str, enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class HCP(Base):
    __tablename__ = "hcps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(50))
    territory = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hcp_id = Column(UUID(as_uuid=True), ForeignKey("hcps.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    time = Column(String(10))
    attendees = Column(JSON, default=list)
    topics_discussed = Column(Text)
    ai_summary = Column(Text)
    materials_shared = Column(JSON, default=list)
    samples_distributed = Column(JSON, default=list)
    sentiment = Column(Enum(SentimentType), default=SentimentType.neutral)
    outcomes = Column(Text)
    raw_chat_input = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    hcp = relationship("HCP", back_populates="interactions")
    follow_ups = relationship("FollowUp", back_populates="interaction")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = Column(UUID(as_uuid=True), ForeignKey("interactions.id"), nullable=False)
    action = Column(Text, nullable=False)
    due_date = Column(DateTime(timezone=True))
    is_completed = Column(String(5), default="false")
    ai_suggested = Column(String(5), default="false")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    interaction = relationship("Interaction", back_populates="follow_ups")


class Material(Base):
    __tablename__ = "materials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    material_type = Column(String(100))
    description = Column(Text)
    file_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))