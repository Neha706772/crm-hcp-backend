from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from app.models.models import InteractionType, SentimentType


# ── HCP Schemas ──────────────────────────────────────────────────────────────

class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    territory: Optional[str] = None

class HCPCreate(BaseModel):
    name: str                        # only name is truly required
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    territory: Optional[str] = None



class HCPResponse(HCPBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ── Interaction Schemas ───────────────────────────────────────────────────────

class FollowUpCreate(BaseModel):
    action: str
    due_date: Optional[datetime] = None
    ai_suggested: bool = False


class FollowUpResponse(BaseModel):  # don't inherit FollowUpCreate
    id: UUID
    interaction_id: UUID
    action: str
    due_date: Optional[datetime] = None
    ai_suggested: str   # matches DB String column
    is_completed: str   # matches DB String column
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionCreate(BaseModel):
    hcp_id: UUID
    interaction_type: InteractionType
    date: datetime
    time: Optional[str] = None
    attendees: Optional[List[str]] = []
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[Any]] = []
    samples_distributed: Optional[List[Any]] = []
    sentiment: Optional[SentimentType] = SentimentType.neutral
    outcomes: Optional[str] = None
    raw_chat_input: Optional[str] = None


class InteractionUpdate(BaseModel):
    interaction_type: Optional[InteractionType] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    attendees: Optional[List[str]] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[Any]] = None
    samples_distributed: Optional[List[Any]] = None
    sentiment: Optional[SentimentType] = None
    outcomes: Optional[str] = None


class InteractionResponse(BaseModel):
    id: UUID
    hcp_id: UUID
    interaction_type: InteractionType
    date: datetime
    time: Optional[str]
    attendees: List[Any]
    topics_discussed: Optional[str]
    ai_summary: Optional[str]
    materials_shared: List[Any]
    samples_distributed: List[Any]
    sentiment: SentimentType
    outcomes: Optional[str]
    raw_chat_input: Optional[str]
    created_at: datetime
    follow_ups: List[FollowUpResponse] = []

    class Config:
        from_attributes = True


# ── Chat / Agent Schemas ──────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    hcp_id: Optional[str] = None
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    action_taken: Optional[str] = None
    interaction_id: Optional[str] = None
    suggested_follow_ups: Optional[List[str]] = []


# ── Material Schemas ──────────────────────────────────────────────────────────

class MaterialResponse(BaseModel):
    id: UUID
    name: str
    material_type: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True
