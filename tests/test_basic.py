# tests/test_basic.py
import pytest
from agent.tools import search_kb, create_ticket, schedule_followup
from agent.schemas import AgentRequest

# ===== TOOL TESTS =====

def test_search_kb_pricing():
    """Pricing query returns KB-006?"""
    result = search_kb("pricing model")
    ids = [r["id"] for r in result["results"]]
    assert "KB-006" in ids
    assert result["results"][0]["score"] > 0

def test_search_kb_hubspot():
    """HubSpot query returns relevant KB entries?"""
    result = search_kb("HubSpot writeback error")
    ids = [r["id"] for r in result["results"]]
    assert any(id in ids for id in ["KB-004", "KB-015", "KB-018"])

def test_search_kb_languages():
    """Language query returns KB-002?"""
    result = search_kb("supported languages")
    ids = [r["id"] for r in result["results"]]
    assert "KB-002" in ids

def test_search_kb_top_k():
    """top_k limit works correctly?"""
    result = search_kb("integration", top_k=2)
    assert len(result["results"]) <= 2

def test_search_kb_empty():
    """Query with no results returns empty list?"""
    result = search_kb("xyzxyzxyz123456")
    assert result["results"] == []

def test_create_ticket_high():
    """High priority ticket created correctly?"""
    result = create_ticket("Test ticket", "Test body", "high")
    assert result["status"] == "created"
    assert result["ticket_id"].startswith("TICK-")

def test_create_ticket_low():
    """Low priority ticket created correctly?"""
    result = create_ticket("Test ticket", "Test body", "low")
    assert result["status"] == "created"
    assert result["ticket_id"].startswith("TICK-")

def test_create_ticket_invalid_priority():
    """Invalid priority raises error?"""
    with pytest.raises(AssertionError):
        create_ticket("Test", "Test", "urgent")

def test_schedule_followup_whatsapp():
    """WhatsApp followup created correctly?"""
    result = schedule_followup("2026-05-08T10:30:00", "Marta", "whatsapp")
    assert result["scheduled"] == True
    assert result["followup_id"].startswith("FUP-")

def test_schedule_followup_email():
    """Email followup created correctly?"""
    result = schedule_followup("2026-05-08T10:30:00", "Ali", "email")
    assert result["scheduled"] == True
    assert result["followup_id"].startswith("FUP-")

def test_schedule_followup_invalid_channel():
    """Invalid channel raises error?"""
    with pytest.raises(AssertionError):
        schedule_followup("2026-05-08T10:30:00", "Marta", "telegram")

# ===== SCHEMA TESTS =====

def test_agent_request_valid():
    """Valid request parsed correctly?"""
    req = AgentRequest(task="Test task")
    assert req.task == "Test task"
    assert req.customer_id is None
    assert req.language is None

def test_agent_request_full():
    """All fields parsed correctly?"""
    req = AgentRequest(task="Test", customer_id="C123", language="es")
    assert req.customer_id == "C123"
    assert req.language == "es"

# ===== ORCHESTRATION LOOP TEST =====

def test_orchestration_loop_hubspot():
    """
    Orchestration loop test: HubSpot ticket scenario.
    Mocks OpenAI so no real API call is made.
    Verifies: search_kb is called, create_ticket is called, ticket ID returned.
    """
    from unittest.mock import patch, MagicMock
    from agent.runner import run_agent

    # 1. iteration: OpenAI returns function_call for search_kb
    mock_search_output = MagicMock()
    mock_search_output.type = "function_call"
    mock_search_output.name = "search_kb"
    mock_search_output.arguments = '{"query": "HubSpot writeback error", "top_k": 5}'
    mock_search_output.call_id = "call_001"

    mock_response_1 = MagicMock()
    mock_response_1.output = [mock_search_output]

    # 2. iteration: OpenAI returns function_call for create_ticket
    mock_ticket_output = MagicMock()
    mock_ticket_output.type = "function_call"
    mock_ticket_output.name = "create_ticket"
    mock_ticket_output.arguments = '{"title": "HubSpot failing", "body": "Cannot write back", "priority": "high"}'
    mock_ticket_output.call_id = "call_002"

    mock_response_2 = MagicMock()
    mock_response_2.output = [mock_ticket_output]

    # 3. iteration: OpenAI returns final message
    mock_content = MagicMock()
    mock_content.text = "I have searched the KB and opened ticket TICK-000001."

    mock_message_output = MagicMock()
    mock_message_output.type = "message"
    mock_message_output.content = [mock_content]

    mock_response_3 = MagicMock()
    mock_response_3.output = [mock_message_output]

    with patch("agent.runner.client") as mock_client:
        mock_client.responses.create.side_effect = [
            mock_response_1,
            mock_response_2,
            mock_response_3,
        ]

        result = run_agent(task="HubSpot writeback failing, open high priority ticket")

    # Assertions
    assert result.final_answer != ""
    assert result.trace_id != ""
    assert result.metrics.openai_calls == 3

    tool_names = [t.name for t in result.tool_calls]
    assert "search_kb" in tool_names
    assert "create_ticket" in tool_names

    ticket_result = next(t for t in result.tool_calls if t.name == "create_ticket")
    assert ticket_result.result["ticket_id"].startswith("TICK-")
    assert ticket_result.result["status"] == "created"