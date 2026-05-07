# tests/test_basic.py
from agent.tools import search_kb, create_ticket, schedule_followup

def test_search_kb_pricing():
    """search_kb pricing sorusunda KB-006 döndürüyor mu?"""
    result = search_kb("pricing model")
    ids = [r["id"] for r in result["results"]]
    assert "KB-006" in ids, f"KB-006 bulunamadı! Sonuçlar: {ids}"
    print("✅ test_search_kb_pricing geçti")

def test_search_kb_hubspot():
    """search_kb HubSpot sorusunda KB-004 veya KB-015 döndürüyor mu?"""
    result = search_kb("HubSpot writeback error")
    ids = [r["id"] for r in result["results"]]
    assert any(id in ids for id in ["KB-004", "KB-015", "KB-018"]), \
        f"HubSpot KB'leri bulunamadı! Sonuçlar: {ids}"
    print("✅ test_search_kb_hubspot geçti")

def test_create_ticket():
    """create_ticket TICK- formatında ID döndürüyor mu?"""
    result = create_ticket("Test ticket", "Test body", "high")
    assert result["status"] == "created"
    assert result["ticket_id"].startswith("TICK-")
    print(f"✅ test_create_ticket geçti: {result['ticket_id']}")

def test_schedule_followup():
    """schedule_followup FUP- formatında ID döndürüyor mu?"""
    result = schedule_followup("2026-05-08T10:30:00", "Marta", "whatsapp")
    assert result["scheduled"] == True
    assert result["followup_id"].startswith("FUP-")
    print(f"✅ test_schedule_followup geçti: {result['followup_id']}")