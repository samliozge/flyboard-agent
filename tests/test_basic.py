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