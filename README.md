
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

=======
 AI-First CRM – HCP Interaction Module
An AI-powered Customer Relationship Management system for Life Sciences field representatives to log and manage interactions with Healthcare Professionals (HCPs).
---
 Project Overview
This system allows pharmaceutical sales reps to log HCP interactions via:
Structured Form – fill in fields manually
AI Chat Interface – describe the interaction in natural language and let the AI extract and log all details automatically
The AI agent (powered by LangGraph + Groq) understands natural language, summarizes interactions, suggests follow-ups, and analyses sentiment.
---
 Tech Stack
Layer	Technology
Frontend	React 19, Redux Toolkit, Vite
Backend	Python, FastAPI, Uvicorn
AI Agent	LangGraph
LLM	Groq – `gemma2-9b-it`
Database	PostgreSQL (asyncpg + SQLAlchemy async)
Font	Google Inter
---
📁 Project Structure
>>>>>>> 6b3d7ce6f3aa092a93697c925870cde8f907b77d
```
crm-hcp/
├── backend/
│   ├── app/
<<<<<<< HEAD
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
=======
│   │   ├── main.py               # FastAPI app entry point
│   │   ├── api/
│   │   │   └── routes.py         # All API endpoints
│   │   ├── models/
│   │   │   └── models.py         # SQLAlchemy DB models
│   │   ├── schemas/
│   │   │   └── schemas.py        # Pydantic request/response schemas
│   │   ├── db/
│   │   │   └── database.py       # Async DB connection
│   │   └── agents/
│   │       └── hcp_agent.py      # LangGraph AI agent + tools
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx              # React entry point
│   │   ├── components/
│   │   │   └── LogInteractionScreen.jsx  # Main UI component
│   │   └── store/
│   │       └── store.js          # Redux store + async thunks
│   ├── package.json
│   └── .env
└── README.md
```
---
 Setup Instructions
Prerequisites
Python 3.10+
Node.js 18+
PostgreSQL database
Groq API key (free at https://console.groq.com)
---
Backend Setup
```bash
# 1. Navigate to backend
cd crm-hcp/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
```
Create `backend/.env` with:
```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/crm_hcp
GROQ_API_KEY=your_groq_api_key_here
```
```bash
# 6. Start the backend server
uvicorn app.main:app --reload
```
Backend runs at: `http://localhost:8000`  
API Docs available at: `http://localhost:8000/docs`
---
Frontend Setup
```bash
# 1. Navigate to frontend
cd crm-hcp/frontend

# 2. Install dependencies
npm install

# 3. Create .env file
```
Create `frontend/.env` with:
```env
VITE_API_URL=http://localhost:8000/api/v1
```
```bash
# 4. Start the frontend dev server
npm run dev
```
Frontend runs at: `http://localhost:5173`
---
 LangGraph AI Agent – 5 Tools
The LangGraph agent acts as an intelligent orchestrator. Based on the user's message, it decides which tool to invoke.
Tool 1:  Log Interaction
Captures interaction data from a natural language message.  
The LLM extracts: HCP name, interaction type, date, topics discussed, sentiment, outcomes.  
Example: "Met Dr. Riya today at HC1, discussed Product X efficacy, she was positive"  
→ Agent extracts all fields and saves to database automatically.
Tool 2:  Edit Interaction
Modifies an existing logged interaction.  
Example: "Update the last interaction's sentiment to negative"  
→ Agent finds the interaction and patches the relevant fields via the API.
Tool 3:  Search HCP
Searches the database for healthcare professionals by name or specialty.  
Example: "Find cardiologists in the APS territory"  
→ Agent queries the HCP table and returns matching results.
Tool 4:  Suggest Follow-ups
Analyses the interaction context and suggests actionable next steps.  
Example: After logging a meeting → Agent suggests "Schedule follow-up in 2 weeks", "Send Phase III trial PDF"  
→ Suggestions are displayed in the UI and can be saved.
Tool 5:  Analyse Sentiment
Detects the HCP's sentiment from the interaction description using the LLM.  
Example: "She seemed hesitant about the pricing but liked the efficacy data"  
→ Agent classifies as `neutral` and explains the reasoning.
---
 API Endpoints
HCP Endpoints
Method	Endpoint	Description
GET	`/api/v1/hcps`	List all HCPs (with optional `?search=`)
POST	`/api/v1/hcps`	Create a new HCP
GET	`/api/v1/hcps/{id}`	Get a specific HCP
Interaction Endpoints
Method	Endpoint	Description
GET	`/api/v1/interactions`	List all interactions (filter by `?hcp_id=`)
POST	`/api/v1/interactions`	Create a new interaction
GET	`/api/v1/interactions/{id}`	Get a specific interaction
PATCH	`/api/v1/interactions/{id}`	Update an interaction
DELETE	`/api/v1/interactions/{id}`	Delete an interaction
AI Agent Endpoint
Method	Endpoint	Description
POST	`/api/v1/agent/chat`	Send a message to the LangGraph AI agent
---
 Database Models
HCP
`id` (UUID), `name`, `specialty`, `hospital`, `email`, `phone`, `territory`, `created_at`
Interaction
`id` (UUID), `hcp_id` (FK), `interaction_type`, `date`, `time`, `attendees` (JSON), `topics_discussed`, `ai_summary`, `materials_shared` (JSON), `samples_distributed` (JSON), `sentiment`, `outcomes`, `raw_chat_input`, `created_at`
FollowUp
`id` (UUID), `interaction_id` (FK), `action`, `due_date`, `is_completed`, `ai_suggested`, `created_at`
---
 Screenshots
> Frontend running at `http://localhost:5173` showing the Log Interaction form and AI Chat panel side by side.
---
Author
Built as part of Round 1 Assignment – AI-First CRM HCP Module  
Stack: React + FastAPI + LangGraph + Groq + PostgreSQL
>>>>>>> 6b3d7ce6f3aa092a93697c925870cde8f907b77d
