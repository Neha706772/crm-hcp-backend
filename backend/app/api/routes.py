from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.models.models import HCP, Interaction, FollowUp
from app.schemas.schemas import (
    HCPCreate, HCPResponse,
    InteractionCreate, InteractionUpdate, InteractionResponse,
    ChatRequest, ChatResponse,
    MaterialResponse,
)
from app.agents.hcp_agent import run_agent

router = APIRouter()


# ── HCP Endpoints ─────────────────────────────────────────────────────────────

@router.get("/hcps", response_model=List[HCPResponse])
async def list_hcps(
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(HCP))
    hcps = result.scalars().all()
    if search:
        s = search.lower()
        hcps = [h for h in hcps if s in (h.name or "").lower() or s in (h.specialty or "").lower()]
    return hcps


@router.post("/hcps", response_model=HCPResponse, status_code=201)
async def create_hcp(data: HCPCreate, db: AsyncSession = Depends(get_db)):
    hcp = HCP(**data.model_dump())
    db.add(hcp)
    await db.commit()
    await db.refresh(hcp)
    return hcp


@router.get("/hcps/{hcp_id}", response_model=HCPResponse)
async def get_hcp(hcp_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HCP).where(HCP.id == hcp_id))
    hcp = result.scalar_one_or_none()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp


# ── Interaction Endpoints ─────────────────────────────────────────────────────

@router.get("/interactions", response_model=List[InteractionResponse])
async def list_interactions(
    hcp_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Interaction).options(selectinload(Interaction.follow_ups))
    if hcp_id:
        query = query.where(Interaction.hcp_id == hcp_id)
    result = await db.execute(query.order_by(Interaction.date.desc()))
    return result.scalars().all()


@router.post("/interactions", response_model=InteractionResponse, status_code=201)
async def create_interaction(data: InteractionCreate, db: AsyncSession = Depends(get_db)):
    interaction = Interaction(**data.model_dump())
    db.add(interaction)
    await db.commit()
    # Remove db.refresh(interaction) — just re-query directly
    result = await db.execute(
        select(Interaction)
        .where(Interaction.id == interaction.id)
        .options(selectinload(Interaction.follow_ups))
    )
    return result.scalar_one()


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(interaction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Interaction)
        .where(Interaction.id == interaction_id)
        .options(selectinload(Interaction.follow_ups))
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.patch("/interactions/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: UUID,
    data: InteractionUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(interaction, field, value)

    await db.commit()
    await db.refresh(interaction)

    result2 = await db.execute(
        select(Interaction)
        .where(Interaction.id == interaction_id)
        .options(selectinload(Interaction.follow_ups))
    )
    return result2.scalar_one()


@router.delete("/interactions/{interaction_id}", status_code=204)
async def delete_interaction(interaction_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Interaction).where(Interaction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    await db.delete(interaction)
    await db.commit()


# ── AI Agent Chat Endpoint ────────────────────────────────────────────────────

@router.post("/agent/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Invoke the LangGraph agent with a natural-language message.
    The agent will decide which tools to call (log, edit, search, suggest, analyse).
    """
    try:
        history = [msg.model_dump() for msg in (request.conversation_history or [])]
        result = await run_agent(
            user_message=request.message,
            db=db,
            hcp_id=request.hcp_id,
            conversation_history=history,
        )
        return ChatResponse(
            response=result["response"],
            action_taken=result.get("action_taken"),
            interaction_id=result.get("interaction_id"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
