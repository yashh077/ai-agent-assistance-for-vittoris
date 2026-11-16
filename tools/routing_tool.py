"""Intelligent Official Routing & Warm Transfer Tool for Vittoris AI Voice Agent."""
from typing import Dict, List, Optional
import sqlite3
import config

OFFICIAL_EXPERTS = [
    {
        "id": "uday",
        "name": "Uday Zayn",
        "role": "Founder & Lead AI Architect",
        "email": "uday@vittoris.com",
        "extension": "Ext 101",
        "avatar": "👨‍💼",
        "specialties": [
            "strategy", "pricing", "cost", "contract", "enterprise", "roadmap", 
            "quote", "acquisition", "pay per appointment", "audit", "commercial"
        ],
        "default_status": "IN_MEETINGS", # Can be dynamically overridden
        "greeting_template": "Hello {name}, this is Uday Zayn. Our AI assistant briefed me on your requirements. I'm here to review your enterprise AI roadmap."
    },
    {
        "id": "sarah",
        "name": "Sarah Chen",
        "role": "Head of Enterprise Integrations",
        "email": "sarah@vittoris.com",
        "extension": "Ext 102",
        "avatar": "👩‍💻",
        "specialties": [
            "server", "api", "database", "vector", "infrastructure", "latency", 
            "500", "document", "pdf", "invoice", "extraction", "pipeline", "backend"
        ],
        "default_status": "AVAILABLE", # Available for transfer simulation
        "greeting_template": "Hi {name}, this is Sarah from Integrations. The agent just forwarded your diagnostic logs. Let's resolve this server and pipeline issue right now."
    },
    {
        "id": "marcus",
        "name": "Marcus Vance",
        "role": "Senior Solutions Engineer",
        "email": "marcus@vittoris.com",
        "extension": "Ext 103",
        "avatar": "👨‍🔧",
        "specialties": [
            "voice", "call", "audio", "sip", "telephony", "whatsapp", "bot", 
            "drop", "jitter", "vapi", "retell", "twilio", "calendar sync"
        ],
        "default_status": "AVAILABLE",
        "greeting_template": "Hey {name}, Marcus here from the Voice Systems engineering team. I see the telephony telemetry on my monitor—let me adjust the stream buffer for you."
    }
]


def get_all_officials_live_status() -> List[Dict]:
    """Retrieves live status of all officials from SQLite DB or default state."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT current_status FROM officials_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    global_status = row[0] if row else config.DEFAULT_OFFICIALS_STATUS
    
    roster = []
    for exp in OFFICIAL_EXPERTS:
        # If global status is OUT_OF_OFFICE or AFTER_HOURS, all are unavailable
        if global_status in ["OUT_OF_OFFICE", "AFTER_HOURS"]:
            status = global_status
        elif global_status == "AVAILABLE":
            status = "AVAILABLE"
        else:
            status = exp["default_status"]
            
        roster.append({
            "id": exp["id"],
            "name": exp["name"],
            "role": exp["role"],
            "email": exp["email"],
            "extension": exp["extension"],
            "avatar": exp["avatar"],
            "specialties": exp["specialties"],
            "status": status,
            "is_available": (status == "AVAILABLE")
        })
    return roster


def match_best_official(query: str) -> Dict:
    """Matches a customer query to the official with the highest domain relevance."""
    query_lower = query.lower()
    roster = get_all_officials_live_status()
    
    best_match = roster[0] # Default to Uday Zayn
    max_score = 0
    
    for official in roster:
        score = sum(1 for keyword in official["specialties"] if keyword in query_lower)
        if score > max_score:
            max_score = score
            best_match = official
            
    return best_match


def execute_warm_transfer(
    official_id: str, 
    customer_name: str, 
    customer_email: str = "", 
    issue_summary: str = "",
    diagnostics_context: str = ""
) -> Dict:
    """
    Executes a warm transfer protocol:
    If the official is AVAILABLE -> bridges the call with a live briefing.
    If the official is UNAVAILABLE -> generates an autonomous fallback voice explanation.
    """
    roster = get_all_officials_live_status()
    official = next((o for o in roster if o["id"] == official_id), roster[0])
    
    caller_display_name = customer_name if customer_name and customer_name != "Customer" else "there"
    
    if official["is_available"]:
        # Find expert greeting
        expert_data = next((e for e in OFFICIAL_EXPERTS if e["id"] == official["id"]), OFFICIAL_EXPERTS[0])
        greeting = expert_data["greeting_template"].format(name=caller_display_name)
        
        return {
            "transfer_status": "CONNECTED",
            "official": official,
            "voice_announcement": (
                f"I found the perfect specialist for you. {official['name']}, our {official['role']}, "
                f"is currently online and available. I am bridging your line to {official['extension']} right now."
            ),
            "official_greeting": greeting,
            "handoff_dossier": {
                "caller": customer_name,
                "email": customer_email,
                "issue_summary": issue_summary,
                "diagnostics": diagnostics_context,
                "timestamp": "Now"
            }
        }
    else:
        return {
            "transfer_status": "OFFICIAL_UNAVAILABLE",
            "official": official,
            "voice_announcement": (
                f"{official['name']}, our {official['role']}, is currently {official['status'].replace('_', ' ').lower()} "
                f"and unable to take a live call right now. However, I can resolve this autonomously for you right away, "
                f"or lock in a priority slot on their calendar. Would you like me to book that or solve it directly?"
            ),
            "fallback_recommendation": "AUTONOMOUS_RESOLUTION_OR_BOOKING"
        }
