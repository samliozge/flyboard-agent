import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from agent.schemas import AgentRequest, AgentResponse
from agent.runner import run_agent

load_dotenv()

app = FastAPI(title="Flyboard Agent API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/agent/run", response_model=AgentResponse)
async def agent_run(request: AgentRequest):
    try:
        result = run_agent(
            task=request.task,
            customer_id=request.customer_id,
            language=request.language
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))