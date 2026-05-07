# agent/runner.py
import os
import json
import time
import uuid
from openai import OpenAI
from dotenv import load_dotenv
from agent.tools import TOOL_DEFINITIONS, TOOL_ROUTER
from agent.schemas import AgentResponse, ToolCall, Metrics

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_ITERATIONS = 6

def run_agent(task: str, customer_id: str = None, language: str = None) -> AgentResponse:
    trace_id = str(uuid.uuid4())
    start_time = time.time()
    openai_calls = 0
    tool_calls_log = []

    print(f"\n[AGENT] trace_id={trace_id}")
    print(f"[AGENT] task={task}")

    system_prompt = """You are a helpful support agent for Flyboard, an AI voice agent platform.
You have access to tools to search the knowledge base, create tickets, and schedule follow-ups.
Always search the knowledge base before answering questions about Flyboard.
If you don't know something, say so and offer to create a ticket.
Respond in the same language as the user's message."""

    # Responses API'de input listesi
    input_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]

    for iteration in range(MAX_ITERATIONS):
        print(f"[AGENT] iteration={iteration + 1}")

        t0 = time.time()
        response = client.responses.create(
            model=MODEL,
            input=input_messages,
            tools=TOOL_DEFINITIONS
        )
        openai_calls += 1
        print(f"[AGENT] openai_call={openai_calls} latency={int((time.time()-t0)*1000)}ms")

        # Output'u işle
        tool_calls_in_response = []
        final_text = None

        for item in response.output:
            if item.type == "message":
                for content in item.content:
                    if hasattr(content, "text"):
                        final_text = content.text
            elif item.type == "function_call":
                tool_calls_in_response.append(item)

        # Tool yok → final cevap
        if not tool_calls_in_response:
            latency_ms = (time.time() - start_time) * 1000
            print(f"[AGENT] final_answer geldi, latency={int(latency_ms)}ms")
            return AgentResponse(
                trace_id=trace_id,
                final_answer=final_text or "",
                tool_calls=tool_calls_log,
                metrics=Metrics(
                    latency_ms=round(latency_ms, 2),
                    model=MODEL,
                    openai_calls=openai_calls
                )
            )

        # Tool'ları çalıştır
        tool_results = []
        for tool_call in tool_calls_in_response:
            tool_name = tool_call.name
            arguments = json.loads(tool_call.arguments)
            call_id = tool_call.call_id

            print(f"[TOOL] çağrılıyor: {tool_name}({arguments})")
            t0 = time.time()

            func = TOOL_ROUTER[tool_name]
            result = func(**arguments)

            tool_latency = int((time.time() - t0) * 1000)
            print(f"[TOOL] tamamlandı: {tool_name} latency={tool_latency}ms")

            tool_calls_log.append(ToolCall(
                name=tool_name,
                arguments=arguments,
                result=result
            ))

            tool_results.append({
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            })

        # Responses API: output + tool results birlikte gönder
        input_messages = input_messages + list(response.output) + tool_results

    # Max iterasyon
    return AgentResponse(
        trace_id=trace_id,
        final_answer="Max iterasyon aşıldı, lütfen tekrar deneyin.",
        tool_calls=tool_calls_log,
        metrics=Metrics(
            latency_ms=round((time.time() - start_time) * 1000, 2),
            model=MODEL,
            openai_calls=openai_calls
        )
    )