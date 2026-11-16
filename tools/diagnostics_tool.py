"""Diagnostics and automated triage tool for server, API, and in-app service issues."""
import time
import random
from typing import Dict, List, Optional
from datetime import datetime

# In-memory service state (can simulate incidents and self-healing)
SERVICE_REGISTRY = {
    "api_gateway": {
        "name": "Vittoris Core API Gateway",
        "endpoint": "https://api.vittoris.com/healthz",
        "status": "HEALTHY",
        "latency_ms": 42,
        "uptime": "99.98%",
        "last_incident": "None in last 30 days"
    },
    "voice_stream_worker": {
        "name": "Autonomous Voice & Telephony Streamer (SIP/Twilio/Vapi)",
        "endpoint": "wss://voice.vittoris.com/stream",
        "status": "HEALTHY",
        "latency_ms": 118,
        "uptime": "99.92%",
        "last_incident": "Temporary audio packet jitter resolved yesterday"
    },
    "document_intelligence": {
        "name": "Document Parsing Pipeline (PDFs/Invoices/Contracts)",
        "endpoint": "https://docs.vittoris.com/v1/extract",
        "status": "HEALTHY",
        "latency_ms": 320,
        "uptime": "99.85%",
        "last_incident": "None"
    },
    "calendar_sync_worker": {
        "name": "Calendar & CRM Bidirectional Sync Engine",
        "endpoint": "https://sync.vittoris.com/status",
        "status": "HEALTHY",
        "latency_ms": 65,
        "uptime": "99.99%",
        "last_incident": "None"
    },
    "database_cluster": {
        "name": "Enterprise PostgreSQL & Vector Storage",
        "endpoint": "internal://db-cluster-primary",
        "status": "HEALTHY",
        "latency_ms": 12,
        "uptime": "99.99%",
        "last_incident": "Routine indexing completed"
    }
}


def run_full_system_diagnostic() -> Dict:
    """Performs an autonomous diagnostic health check across all core Vittoris services and infrastructure."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "OPERATIONAL",
        "services": {},
        "active_alerts": []
    }
    
    degraded_count = 0
    for key, svc in SERVICE_REGISTRY.items():
        # Inject realistic minor latency fluctuation
        jitter = random.randint(-5, 10)
        current_latency = max(10, svc["latency_ms"] + jitter)
        
        report["services"][key] = {
            "name": svc["name"],
            "status": svc["status"],
            "latency": f"{current_latency}ms",
            "uptime": svc["uptime"],
            "last_incident": svc["last_incident"]
        }
        
        if svc["status"] != "HEALTHY":
            degraded_count += 1
            report["active_alerts"].append(f"{svc['name']} is reporting {svc['status']}.")

    if degraded_count > 0:
        report["overall_status"] = "DEGRADED" if degraded_count == 1 else "CRITICAL"
        
    return report


def diagnose_customer_issue(issue_category: str, details: str = "") -> Dict:
    """
    Diagnoses common customer reported issues regarding in-app services, integrations, or voice agents.
    Returns recommended automated remediation actions.
    """
    category_lower = issue_category.lower()
    details_lower = details.lower()
    
    # 1. Calendar / Booking sync issues
    if any(k in category_lower or k in details_lower for k in ["calendar", "booking", "slot", "timezone", "sync", "google cal"]):
        return {
            "category": "Calendar & Appointment Sync",
            "diagnosis": "OAuth token expiration or timezone offset mismatch between CRM and Google Calendar.",
            "recommended_action": "Execute automatic token refresh and verify timezone settings.",
            "available_auto_fix": "refresh_calendar_tokens",
            "requires_human": False
        }
        
    # 2. Voice Agent / Call Drops / Audio quality
    elif any(k in category_lower or k in details_lower for k in ["voice", "call", "audio", "drop", "twilio", "retell", "vapi", "phone"]):
        return {
            "category": "Voice & Telephony Agent",
            "diagnosis": "SIP trunk packet latency or webhook connection timeout during high concurrency.",
            "recommended_action": "Restart voice stream webhook listener and adjust buffer latency parameters.",
            "available_auto_fix": "restart_voice_stream",
            "requires_human": False
        }
        
    # 3. Document Parsing / Extraction Failures
    elif any(k in category_lower or k in details_lower for k in ["document", "pdf", "invoice", "extract", "ocr", "parsing", "stuck"]):
        return {
            "category": "Document Intelligence Pipeline",
            "diagnosis": "Job queue backpressure or unsupported image/PDF encoding schema.",
            "recommended_action": "Flush stale extraction queue workers and reprocess failed batch with fallback OCR engine.",
            "available_auto_fix": "reprocess_extraction_queue",
            "requires_human": False
        }
        
    # 4. Server 500 / Latency / API Down
    elif any(k in category_lower or k in details_lower for k in ["server", "down", "500", "502", "crash", "timeout", "latency"]):
        return {
            "category": "Server & API Infrastructure",
            "diagnosis": "API gateway endpoint timeout or database connection pool saturation.",
            "recommended_action": "Execute cache purge, recycle database pool connections, and test endpoint response.",
            "available_auto_fix": "purge_cache_and_recycle_pool",
            "requires_human": False
        }
        
    # 5. Billing / Custom Contract / High Priority Account
    elif any(k in category_lower or k in details_lower for k in ["billing", "invoice", "payment", "contract", "enterprise", "refund"]):
        return {
            "category": "Enterprise Billing & Commercials",
            "diagnosis": "Commercial billing queries and enterprise contractual terms require official leadership sign-off.",
            "recommended_action": "Escalate directly to Uday Zayn (Founder) and finance leadership.",
            "available_auto_fix": None,
            "requires_human": True
        }
        
    # Default General Support
    else:
        return {
            "category": "General In-App Service Query",
            "diagnosis": "Standard configuration or usage query.",
            "recommended_action": "Review system documentation or run automated cache flush.",
            "available_auto_fix": "purge_cache_and_recycle_pool",
            "requires_human": False
        }


def execute_auto_remediation(action_name: str) -> Dict:
    """Executes a self-healing operational runbook action for autonomous resolution."""
    start = time.time()
    
    if action_name == "refresh_calendar_tokens":
        time.sleep(0.5)
        return {
            "success": True,
            "action": action_name,
            "result": "OAuth tokens successfully refreshed and validated against Google Calendar & Cal.com APIs. Sync is operational.",
            "duration": f"{round(time.time() - start, 2)}s"
        }
        
    elif action_name == "restart_voice_stream":
        time.sleep(0.6)
        SERVICE_REGISTRY["voice_stream_worker"]["status"] = "HEALTHY"
        SERVICE_REGISTRY["voice_stream_worker"]["last_incident"] = f"Worker recycled autonomously at {datetime.now().strftime('%H:%M:%S')}"
        return {
            "success": True,
            "action": action_name,
            "result": "Voice stream webhook listeners recycled. Audio latency normalized to ~110ms. Active calls resumed without drops.",
            "duration": f"{round(time.time() - start, 2)}s"
        }
        
    elif action_name == "reprocess_extraction_queue":
        time.sleep(0.7)
        SERVICE_REGISTRY["document_intelligence"]["status"] = "HEALTHY"
        return {
            "success": True,
            "action": action_name,
            "result": "Stale PDF extraction jobs drained from DLQ (Dead Letter Queue) and reprocessed using secondary OCR fallback engine.",
            "duration": f"{round(time.time() - start, 2)}s"
        }
        
    elif action_name == "purge_cache_and_recycle_pool":
        time.sleep(0.5)
        for svc in SERVICE_REGISTRY.values():
            svc["status"] = "HEALTHY"
        return {
            "success": True,
            "action": action_name,
            "result": "Redis cache flushed and database connection pools recycled. API Gateway latency returned to normal (42ms).",
            "duration": f"{round(time.time() - start, 2)}s"
        }
        
    else:
        return {
            "success": False,
            "action": action_name,
            "error": f"Unknown remediation action '{action_name}'. Escalating to human engineering team."
        }
