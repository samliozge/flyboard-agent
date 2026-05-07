# Flyboard Agent API

A tool-using AI agent that routes user requests to the correct operational outcome using OpenAI's Responses API.

## Built With
- Python + FastAPI
- OpenAI Responses API (tool/function calling)
- Claude (Anthropic) — used as coding assistant

## Project Structure
flyboard-agent/
├── main.py # FastAPI app
├── agent/
│ ├── runner.py # Agentic loop
│ ├── tools.py # search_kb, create_ticket, schedule_followup
│ └── schemas.py # Pydantic models
├── data/
│ └── kb.json # Knowledge base
├── storage/
│ └── store.py # In-memory storage
└── tests/
└── test_basic.py # Tests

## Setup

### 1. Clone and install
git clone <repo-url>
cd flyboard-agent
python -m venv venv
venv\Scripts\activate # Windows
pip install fastapi uvicorn openai python-dotenv pytest httpx

### 2. Configure environment
cp .env.example .env
 Add your OpenAI API key to .env:
 OPENAI_API_KEY=sk-...
 OPENAI_MODEL=gpt-4o

### 3. Run
uvicorn main:app --reload

### 4. Test
pytest tests/test_basic.py -v

## Endpoints

### POST /v1/agent/run
```json
{
  "task": "string",
  "customer_id": "optional string",
  "language": "optional string"
}
```

### GET /health
Returns `{"status": "ok"}`

## Example Requests

### 1. Pricing question
```json
{"task": "Give me the pricing model at a high level"}
```

### 2. CRM writeback
```json
{"task": "How does CRM writeback work and how long does it take to set up?"}
```

### 3. HubSpot ticket
```json
{"task": "We are failing to write back to HubSpot since this morning. Can you open a high priority ticket?"}
```

### 4. Schedule follow-up
```json
{"task": "Schedule a follow-up call with Marta tomorrow at 10:30 CET via WhatsApp to discuss custom SLA."}
```

### 5. Spanish request
```json
{"task": "En que idiomas funciona y que incluye el onboarding?"}
```

## How It Works

1. User sends a task to `POST /v1/agent/run`
2. Agent sends task + tool definitions to OpenAI
3. OpenAI decides which tool(s) to call
4. Agent executes tool(s) and sends results back to OpenAI
5. Loop continues until OpenAI produces a final answer
6. Agent returns final answer + tool call trace + metrics
