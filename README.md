# AI-First CRM – HCP Module (Log Interaction Screen)

A full-stack CRM application for pharmaceutical field representatives to log interactions with Healthcare Professionals (HCPs) via a structured form or a conversational AI chat interface.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Redux Toolkit |
| Backend | Python 3.11 + FastAPI |
| AI Agent | LangGraph 0.2 |
| LLM | Groq — `gemma2-9b-it` |
| Database | PostgreSQL (async via SQLAlchemy + asyncpg) |
| Font | Google Inter |

---

## Project Structure

```
crm-hcp/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── hcp_agent.py       # LangGraph agent + 5 tools
│   │   ├── api/
│   │   │   └── routes.py          # FastAPI REST endpoints
│   │   ├── db/
│   │   │   └── database.py        # Async SQLAlchemy engine
│   │   ├── models/
│   │   │   └── models.py          # ORM models (HCP, Interaction, FollowUp, Material)
│   │   ├── schemas/
│   │   │   └── schemas.py         # Pydantic request/response schemas
│   │   └── main.py                # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── public/
    │   └── index.html
    ├── src/
    │   ├── components/
    │   │   └── LogInteractionScreen.jsx   # Main screen (form + chat)
    │   ├── store/
    │   │   └── store.js                   # Redux store + slices
    │   └── index.js
    └── package.json
```

---

## LangGraph Agent — 5 Tools

### 1. `log_interaction`
Captures HCP interaction data from form or natural-language chat input.
- Extracts entities (HCP, date, type, topics, sentiment) using the LLM
- Auto-generates a concise AI summary via `gemma2-9b-it`
- Persists structured record to PostgreSQL

### 2. `edit_interaction`
Modifies a previously logged interaction.
- Supports editing: topics, sentiment, outcomes, type, date, attendees
- Regenerates AI summary if core fields change

### 3. `search_hcp`
Finds HCPs by name, specialty, or hospital.
- Returns matched HCP IDs for use in logging
- Enables the agent to resolve HCP names mentioned in chat

### 4. `suggest_follow_up`
Generates 3 AI-powered follow-up action suggestions per interaction.
- Analyses interaction topics, outcomes, and HCP specialty
- Persists suggestions as `FollowUp` records (flagged `ai_suggested=true`)

### 5. `analyze_sentiment`
Classifies the tone of an interaction description.
- Returns: `positive`, `neutral`, or `negative` + reasoning
- Optionally updates the sentiment field on an existing interaction

---

## LangGraph Agent Flow

```
User message
    ↓
[Agent Node] ← System prompt + conversation history
    ↓ (has tool calls?)
 YES → [Tool Node] → executes 1+ tools → back to Agent
  NO → Final AI response returned to user
```

The agent uses a **ReAct loop**: it reasons, selects a tool, observes the result, then reasons again — repeating until it has enough information to respond.

---

## Setup Instructions

### Backend

```bash
cd backend
cp .env.example .env
# Fill in GROQ_API_KEY and DATABASE_URL

pip install -r requirements.txt

# Start PostgreSQL and create the database:
# createdb crm_hcp

uvicorn app.main:app --reload --port 8000
```

Tables are auto-created on first startup via SQLAlchemy.

### Frontend

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000/api/v1 npm start
```

App runs at http://localhost:3000

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/hcps` | List / search HCPs |
| POST | `/api/v1/hcps` | Create HCP |
| GET | `/api/v1/interactions` | List interactions |
| POST | `/api/v1/interactions` | Create interaction (form) |
| PATCH | `/api/v1/interactions/{id}` | Update interaction |
| DELETE | `/api/v1/interactions/{id}` | Delete interaction |
| POST | `/api/v1/agent/chat` | LangGraph agent chat |
| GET | `/health` | Health check |

---

## Environment Variables

```
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/crm_hcp
ENVIRONMENT=development
```

---

## Architecture Overview

```
React (Form + Chat UI)
    ↕ REST API
FastAPI
    ↕ invoke
LangGraph Agent
    ↕ tools
PostgreSQL    Groq LLM (gemma2-9b-it)
```

The LangGraph agent acts as an orchestrator — it interprets natural language from the chat panel and decides which tool(s) to invoke. The form panel submits directly to the REST API, bypassing the agent for speed.
