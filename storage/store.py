# storage/store.py
# Ticket ve followup'ları bellekte tutuyoruz (in-memory)
# Gerçek projede bu bir veritabanı olurdu

tickets = {}
followups = {}
ticket_counter = 0
followup_counter = 0

def save_ticket(title: str, body: str, priority: str) -> dict:
    global ticket_counter
    ticket_counter += 1
    ticket_id = f"TICK-{ticket_counter:06d}"  # TICK-000001 formatı
    tickets[ticket_id] = {
        "title": title,
        "body": body,
        "priority": priority,
        "status": "created"
    }
    print(f"[STORE] Ticket kaydedildi: {ticket_id}")
    return {"ticket_id": ticket_id, "status": "created"}

def save_followup(datetime_iso: str, contact: str, channel: str) -> dict:
    global followup_counter
    followup_counter += 1
    followup_id = f"FUP-{followup_counter:06d}"  # FUP-000001 formatı
    followups[followup_id] = {
        "datetime_iso": datetime_iso,
        "contact": contact,
        "channel": channel
    }
    print(f"[STORE] Followup kaydedildi: {followup_id}")
    return {"scheduled": True, "followup_id": followup_id}