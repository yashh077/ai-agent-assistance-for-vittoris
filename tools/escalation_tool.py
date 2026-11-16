"""Autonomous Escalation & Ticket Dispatcher Tool for Official Interventions."""
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import config

def init_escalation_db():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS escalation_tickets (
        id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT,
        urgency TEXT NOT NULL,
        category TEXT NOT NULL,
        summary TEXT NOT NULL,
        diagnostics_context TEXT,
        assigned_official TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'DISPATCHED_TO_OFFICIAL',
        created_at TEXT NOT NULL,
        resolution_notes TEXT
    )
    """)
    conn.commit()
    conn.close()

init_escalation_db()


def dispatch_official_escalation(
    customer_name: str,
    customer_email: str,
    issue_summary: str,
    urgency: str = "HIGH",
    category: str = "Enterprise Architecture & Official Review",
    diagnostics_context: str = "",
    customer_phone: str = ""
) -> Dict:
    """
    Autonomously generates an Executive Incident Dossier and dispatches an emergency ticket 
    to Vittoris officials when their manual intervention or approval is required.
    """
    ticket_id = f"VIT-ESC-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.now().isoformat()
    
    # Route to appropriate official based on category
    assigned_official = "Uday Zayn (Founder & Lead Architect)"
    if "integration" in category.lower() or "infrastructure" in category.lower():
        assigned_official = "Sarah Chen (Head of Enterprise Integrations)"
    elif "voice" in category.lower() or "app" in category.lower():
        assigned_official = "Marcus Vance (Senior Solutions Engineer)"
        
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO escalation_tickets (id, customer_name, customer_email, customer_phone, urgency, category, summary, diagnostics_context, assigned_official, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'DISPATCHED_TO_OFFICIAL', ?)
    """, (ticket_id, customer_name, customer_email, customer_phone, urgency, category, issue_summary, diagnostics_context, assigned_official, created_at))
    conn.commit()
    conn.close()
    
    # Estimated response time based on urgency
    sla_map = {
        "CRITICAL": "Within 1 hour (emergency pager active)",
        "HIGH": "Within 2-4 hours",
        "MEDIUM": "Within 1 business day",
        "LOW": "Within 2 business days"
    }
    estimated_sla = sla_map.get(urgency.upper(), "Within 4 hours")
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "assigned_official": assigned_official,
        "urgency": urgency.upper(),
        "category": category,
        "created_at": created_at,
        "estimated_sla": estimated_sla,
        "message": (
            f"Escalation ticket {ticket_id} has been registered and autonomously dispatched to {assigned_official}. "
            f"Even though officials are currently away or in meetings, our automated pager has logged your incident "
            f"with all diagnostic context. Expected response: {estimated_sla}."
        )
    }


def list_escalation_tickets() -> List[Dict]:
    """Retrieves all escalation tickets logged for officials."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, customer_email, customer_phone, urgency, category, summary, diagnostics_context, assigned_official, status, created_at FROM escalation_tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    tickets = []
    for r in rows:
        tickets.append({
            "id": r[0],
            "customer_name": r[1],
            "customer_email": r[2],
            "customer_phone": r[3],
            "urgency": r[4],
            "category": r[5],
            "summary": r[6],
            "diagnostics_context": r[7],
            "assigned_official": r[8],
            "status": r[9],
            "created_at": r[10]
        })
    return tickets
