import os
import uuid
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from agent.schemas import AgentRequest, AgentResponse
from agent.runner import run_agent

load_dotenv()

app = FastAPI(title="Flyboard Agent API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/agent/run")
async def agent_run(request: AgentRequest):
    trace_id = str(uuid.uuid4())
    try:
        result = run_agent(
            task=request.task,
            customer_id=request.customer_id,
            language=request.language
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail={"trace_id": trace_id, "error": str(e)}
        )