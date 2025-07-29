import json
from datetime import datetime
from pathlib import Path

TICKETS_FILE = Path("data/tickets.json")

def load_tickets():
    if not TICKETS_FILE.exists():
        return []
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tickets(tickets):
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2, ensure_ascii=False)

def create_ticket(user_id, username, category, text, photo=None):
    tickets = load_tickets()
    ticket = {
        "id": len(tickets) + 1,
        "user_id": user_id,
        "username": username or "Без username",
        "category": category,
        "text": text,
        "photo": photo,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    tickets.append(ticket)
    save_tickets(tickets)
    return ticket

def delete_ticket_by_user_id(user_id):
    tickets = load_tickets()
    tickets = [t for t in tickets if not (t["user_id"] == user_id and t["status"] == "open")]
    save_tickets(tickets)

def get_ticket_by_id(ticket_id: int):
    tickets = load_tickets()
    for t in tickets:
        if t["id"] == ticket_id:
            return t
    return None

def close_ticket_by_user_id(user_id):
    tickets = load_tickets()
    for t in tickets:
        if t["user_id"] == user_id and t["status"] == "open":
            t["status"] = "closed"
    save_tickets(tickets)

def get_open_tickets():
    return [t for t in load_tickets() if t["status"] == "open"]

# 👇 ДОБАВЛЕНО: архив обращений по категории
def get_tickets_by_category(category_key: str):
    tickets = load_tickets()
    return [
        t for t in tickets
        if t["category"] == category_key
    ]

# 👇 ДОБАВЛЕНО: получение последнего открытого тикета по user_id
def get_ticket_by_id_by_user_id(user_id: int):
    tickets = load_tickets()
    for t in reversed(tickets):  # Берём последний тикет этого пользователя
        if t["user_id"] == user_id and t["status"] == "open":
            return t
    return None
