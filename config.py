"""Configuration and settings for Vittoris AI Autonomous Agent System."""
import os
from datetime import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "vittoris_data.db")

COMPANY_NAME = "Vittoris AI"
COMPANY_WEBSITE = "https://vittoris.com"
COMPANY_EMAIL = "contact@vittoris.com"

# Official Business Hours (Eastern Time / UTC-5)
BUSINESS_HOURS_START = time(9, 0)   # 09:00 AM
BUSINESS_HOURS_END = time(18, 0)     # 06:00 PM
BUSINESS_DAYS = [0, 1, 2, 3, 4]      # Monday to Friday (0 = Mon, 4 = Fri)

# Officials Current Availability Mode
# Options: "AVAILABLE", "IN_MEETINGS", "OUT_OF_OFFICE", "AFTER_HOURS"
DEFAULT_OFFICIALS_STATUS = "IN_MEETINGS"

OFFICIALS_DIRECTORY = [
    {
        "name": "Uday Zayn",
        "role": "Founder & Lead AI Architect",
        "email": "uday@vittoris.com",
        "department": "Executive & AI Architecture",
        "status": "In Client Strategy Meetings"
    },
    {
        "name": "Sarah Chen",
        "role": "Head of Enterprise Integrations",
        "email": "sarah@vittoris.com",
        "department": "Integrations & Infrastructure",
        "status": "Deploying Client Pipelines"
    },
    {
        "name": "Marcus Vance",
        "role": "Senior Solutions Engineer",
        "email": "marcus@vittoris.com",
        "department": "Voice Agents & In-App Systems",
        "status": "Unavailable (After Hours / On Call)"
    }
]

SUPPORTED_SERVICES = {
    "voice_agents": {
        "title": "Autonomous Conversational & Voice Agents",
        "description": "24/7 human-grade inbound/outbound voice bots and chat setters integrated with telephony (Twilio/SIP), WhatsApp, Web, Meta, and Google Business.",
        "typical_sla": "Instant / 24/7 autonomous response"
    },
    "appointment_acquisition": {
        "title": "Pay-Per-Appointment Lead Generation Engine",
        "description": "Performance-based acquisition systems that automatically prospect, qualify, and book qualified meetings directly into sales calendars.",
        "typical_sla": "Automated instant booking"
    },
    "custom_infrastructure": {
        "title": "Custom AI Operational Infrastructure",
        "description": "Tailored enterprise backend automation, syncing data between CRMs, ERPs, databases, and custom business pipelines.",
        "typical_sla": "Custom deployment sprint (2-4 weeks)"
    },
    "document_intelligence": {
        "title": "Enterprise Document Intelligence Pipelines",
        "description": "Automated parsing, extraction, and validation of PDFs, invoices, receipts, vendor contracts, and unstructured legal docs.",
        "typical_sla": "Sub-second processing per document"
    },
    "diagnostic_audit": {
        "title": "AI Opportunity & Workflow Diagnostic Audit",
        "description": "Deep-dive audit into pipeline leakage, manual labor bottlenecks, and operational costs to engineer ROI-focused AI architectures.",
        "typical_sla": "Initial diagnostic completed in 3 business days"
    }
}
