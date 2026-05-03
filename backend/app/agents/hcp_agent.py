"""
LangGraph Agent for HCP Interaction Management
Tools: log_interaction, edit_interaction, search_hcp, suggest_follow_up, analyze_sentiment
"""

import json
import os
from typing import TypedDict, Annotated, List, Optional, Any
from datetime import datetime
from uuid import UUID

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.models import HCP, Interaction, FollowUp, InteractionType, SentimentType
from dotenv import load_dotenv

load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="gemma2-9b-it",
        temperature=0.2,
        max_tokens=1024,
    )


# ── Agent State ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    hcp_id: Optional[str]
    db_session: Any
    last_action: Optional[str]
    interaction_id: Optional[str]


# ── Tool Factory (tools need DB access, so we build them with closure) ────────

def build_tools(db: AsyncSession):
    """Build tool functions with DB session injected via closure."""

    @tool
    async def log_interaction(
        hcp_id: str,
        interaction_type: str,
        date: str,
        topics_discussed: str,
        sentiment: str = "neutral",
        outcomes: str = "",
        attendees: str = "",
        raw_chat_input: str = "",
    ) -> str:
        """
        Log a new HCP interaction. The LLM will extract entities from natural language
        and summarise the interaction automatically. Use this when the user wants to
        record a meeting, call, or any contact with an HCP.

        Args:
            hcp_id: UUID of the HCP.
            interaction_type: One of meeting, call, email, conference, webinar.
            date: ISO date string (YYYY-MM-DD).
            topics_discussed: Free-text description of topics.
            sentiment: One of positive, neutral, negative.
            outcomes: Key outcomes or agreements reached.
            attendees: Comma-separated attendee names.
            raw_chat_input: Original text from the user's chat message.
        """
        try:
            # Use LLM to produce a concise AI summary
            llm = get_llm()
            summary_prompt = f"""
You are a life-science CRM assistant. Summarise this HCP interaction concisely for a field rep's record.
Topics: {topics_discussed}
Outcomes: {outcomes}
Sentiment: {sentiment}
Write 2-3 sentences maximum, professional tone.
"""
            summary_response = await llm.ainvoke([HumanMessage(content=summary_prompt)])
            ai_summary = summary_response.content.strip()

            attendee_list = [a.strip() for a in attendees.split(",") if a.strip()]

            # Parse date
            interaction_date = datetime.fromisoformat(date)

            interaction = Interaction(
                hcp_id=UUID(hcp_id),
                interaction_type=InteractionType(interaction_type),
                date=interaction_date,
                topics_discussed=topics_discussed,
                ai_summary=ai_summary,
                sentiment=SentimentType(sentiment),
                outcomes=outcomes,
                attendees=attendee_list,
                raw_chat_input=raw_chat_input,
            )
            db.add(interaction)
            await db.commit()
            await db.refresh(interaction)

            return json.dumps({
                "status": "success",
                "interaction_id": str(interaction.id),
                "ai_summary": ai_summary,
                "message": f"Interaction logged successfully for HCP {hcp_id}.",
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    @tool
    async def edit_interaction(
        interaction_id: str,
        field: str,
        new_value: str,
    ) -> str:
        """
        Edit a previously logged HCP interaction. Supports modifying topics_discussed,
        sentiment, outcomes, interaction_type, attendees, or date.

        Args:
            interaction_id: UUID of the interaction to edit.
            field: The field name to update.
            new_value: The new value (will be parsed appropriately).
        """
        try:
            result = await db.execute(
                select(Interaction).where(Interaction.id == UUID(interaction_id))
            )
            interaction = result.scalar_one_or_none()
            if not interaction:
                return json.dumps({"status": "error", "message": "Interaction not found."})

            allowed_fields = {
                "topics_discussed", "sentiment", "outcomes",
                "interaction_type", "attendees", "date", "time",
            }
            if field not in allowed_fields:
                return json.dumps({"status": "error", "message": f"Field '{field}' cannot be edited."})

            if field == "sentiment":
                setattr(interaction, field, SentimentType(new_value))
            elif field == "interaction_type":
                setattr(interaction, field, InteractionType(new_value))
            elif field == "attendees":
                setattr(interaction, field, [a.strip() for a in new_value.split(",")])
            elif field == "date":
                setattr(interaction, field, datetime.fromisoformat(new_value))
            else:
                setattr(interaction, field, new_value)

            interaction.updated_at = datetime.utcnow()

            # Regenerate AI summary if topics changed
            if field in ("topics_discussed", "outcomes", "sentiment"):
                llm = get_llm()
                summary_prompt = f"""
Summarise this updated HCP interaction record for a pharmaceutical field rep.
Topics: {interaction.topics_discussed}
Outcomes: {interaction.outcomes}
Sentiment: {interaction.sentiment}
2-3 sentences, professional tone.
"""
                summary_resp = await llm.ainvoke([HumanMessage(content=summary_prompt)])
                interaction.ai_summary = summary_resp.content.strip()

            await db.commit()
            return json.dumps({
                "status": "success",
                "message": f"Field '{field}' updated for interaction {interaction_id}.",
                "new_summary": getattr(interaction, "ai_summary", None),
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    @tool
    async def search_hcp(query: str) -> str:
        """
        Search for Healthcare Professionals (HCPs) by name, specialty, or hospital.
        Returns matching HCPs with their ID, name, specialty, and hospital.

        Args:
            query: Search term — partial name, specialty, or hospital name.
        """
        try:
            result = await db.execute(select(HCP))
            all_hcps = result.scalars().all()

            q = query.lower()
            matches = [
                h for h in all_hcps
                if q in (h.name or "").lower()
                or q in (h.specialty or "").lower()
                or q in (h.hospital or "").lower()
            ]

            if not matches:
                return json.dumps({"status": "not_found", "message": "No HCPs matched your query.", "results": []})

            return json.dumps({
                "status": "success",
                "results": [
                    {
                        "id": str(h.id),
                        "name": h.name,
                        "specialty": h.specialty,
                        "hospital": h.hospital,
                        "territory": h.territory,
                    }
                    for h in matches[:10]
                ],
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    @tool
    async def suggest_follow_up(interaction_id: str) -> str:
        """
        Generate AI-powered follow-up action suggestions for a completed HCP interaction.
        Uses the LLM to analyse the interaction and propose next steps.

        Args:
            interaction_id: UUID of the completed interaction.
        """
        try:
            result = await db.execute(
                select(Interaction)
                .where(Interaction.id == UUID(interaction_id))
                .options(selectinload(Interaction.hcp))
            )
            interaction = result.scalar_one_or_none()
            if not interaction:
                return json.dumps({"status": "error", "message": "Interaction not found."})

            llm = get_llm()
            prompt = f"""
You are a life-science CRM assistant helping a pharmaceutical field representative.
Based on the following HCP interaction, suggest 3 specific, actionable follow-up tasks.

HCP: {interaction.hcp.name if interaction.hcp else 'Unknown'}
Specialty: {interaction.hcp.specialty if interaction.hcp else 'Unknown'}
Interaction type: {interaction.interaction_type}
Topics discussed: {interaction.topics_discussed}
Outcomes: {interaction.outcomes}
Sentiment: {interaction.sentiment}

Return ONLY a JSON array of 3 strings, each a clear follow-up action.
Example: ["Send Phase III trial brochure by Friday", "Schedule advisory board invite", "Follow up on sample request in 2 weeks"]
"""
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Parse suggestions
            try:
                suggestions = json.loads(content)
            except Exception:
                suggestions = [s.strip().lstrip("-• ") for s in content.split("\n") if s.strip()][:3]

            # Persist AI-suggested follow-ups
            for action in suggestions:
                follow_up = FollowUp(
                    interaction_id=interaction.id,
                    action=action,
                    ai_suggested="true",
                )
                db.add(follow_up)
            await db.commit()

            return json.dumps({
                "status": "success",
                "suggestions": suggestions,
                "message": f"Generated {len(suggestions)} follow-up actions.",
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    @tool
    async def analyze_sentiment(text: str, interaction_id: Optional[str] = None) -> str:
        """
        Analyse the sentiment of an HCP interaction description using the LLM.
        Optionally updates the sentiment field on an existing interaction.

        Args:
            text: The text to analyse (topics discussed, meeting notes, etc.).
            interaction_id: Optional — if provided, updates the interaction's sentiment.
        """
        try:
            llm = get_llm()
            prompt = f"""
Analyse the sentiment of this pharmaceutical field rep interaction note.
Return ONLY a JSON object with two keys:
- "sentiment": one of "positive", "neutral", "negative"
- "reasoning": one sentence explaining why

Text: {text}
"""
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            try:
                result_data = json.loads(content)
            except Exception:
                sentiment = "neutral"
                reasoning = "Could not parse response."
                result_data = {"sentiment": sentiment, "reasoning": reasoning}

            # Optionally update the interaction
            if interaction_id:
                res = await db.execute(
                    select(Interaction).where(Interaction.id == UUID(interaction_id))
                )
                interaction = res.scalar_one_or_none()
                if interaction:
                    interaction.sentiment = SentimentType(result_data.get("sentiment", "neutral"))
                    await db.commit()

            return json.dumps({
                "status": "success",
                "sentiment": result_data.get("sentiment"),
                "reasoning": result_data.get("reasoning"),
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    return [log_interaction, edit_interaction, search_hcp, suggest_follow_up, analyze_sentiment]


# ── Graph Builder ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an intelligent CRM assistant for pharmaceutical field representatives.
You help manage interactions with Healthcare Professionals (HCPs).

You have access to these tools:
- log_interaction: Record a new meeting, call, or email with an HCP
- edit_interaction: Update an existing interaction record
- search_hcp: Find HCPs by name, specialty, or hospital
- suggest_follow_up: Generate AI-powered follow-up recommendations
- analyze_sentiment: Detect the tone/sentiment of interaction notes

Always:
1. Confirm you understood the user's intent before acting
2. Use search_hcp to find the correct HCP ID before logging
3. Provide friendly, concise responses suited to a field rep on the go
4. After logging, always offer to suggest follow-ups

When a user describes an interaction in natural language, extract:
- HCP name → use search_hcp to get the ID
- Interaction type (meeting/call/email)
- Date mentioned
- Topics and products discussed
- Sentiment (how did the HCP react?)
- Any outcomes or commitments
"""


def build_agent_graph(db: AsyncSession):
    tools = build_tools(db)
    llm = get_llm().bind_tools(tools)
    tool_node = ToolNode(tools)

    def agent_node(state: AgentState):
        messages = state["messages"]
        # Prepend system message if not already there
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        response = llm.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState):
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()


async def run_agent(
    user_message: str,
    db: AsyncSession,
    hcp_id: Optional[str] = None,
    conversation_history: Optional[List] = None,
) -> dict:
    """Entry point for the FastAPI route to invoke the LangGraph agent."""
    graph = build_agent_graph(db)

    history = []
    if conversation_history:
        for msg in conversation_history:
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            else:
                history.append(AIMessage(content=msg["content"]))

    history.append(HumanMessage(content=user_message))

    initial_state: AgentState = {
        "messages": history,
        "hcp_id": hcp_id,
        "db_session": db,
        "last_action": None,
        "interaction_id": None,
    }

    final_state = await graph.ainvoke(initial_state)
    last_message = final_state["messages"][-1]

    return {
        "response": last_message.content,
        "action_taken": final_state.get("last_action"),
        "interaction_id": final_state.get("interaction_id"),
    }
