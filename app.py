"""Flask Web Application & API Server for Vittoris AI Autonomous Agent."""
import os
import uuid
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

import config
from agent_engine import VittorisAutonomousAgent
from tools.calendar_tool import (
    get_available_slots,
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
    list_all_appointments,
    get_officials_availability,
    set_officials_status
)
from tools.diagnostics_tool import (
    run_full_system_diagnostic,
    diagnose_customer_issue,
    execute_auto_remediation
)
from tools.escalation_tool import (
    dispatch_official_escalation,
    list_escalation_tickets
)
from tools.routing_tool import (
    get_all_officials_live_status,
    execute_warm_transfer,
    match_best_official
)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

agent = VittorisAutonomousAgent()


@app.route("/")
def index():
    return render_template("index.html", company_name=config.COMPANY_NAME)


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    data = request.json or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    
    if not message:
        return jsonify({"error": "Message is required"}), 400
        
    response = agent.process_message(session_id, message)
    response["session_id"] = session_id
    return jsonify(response)


@app.route("/api/slots", methods=["GET"])
def get_slots():
    days = int(request.args.get("days", 5))
    slots = get_available_slots(days_ahead=days)
    return jsonify({"slots": slots})


@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    appointments = list_all_appointments()
    return jsonify({"appointments": appointments})


@app.route("/api/appointments/book", methods=["POST"])
def book_apt_endpoint():
    data = request.json or {}
    res = book_appointment(
        customer_name=data.get("name", ""),
        customer_email=data.get("email", ""),
        slot_time=data.get("slot_time", ""),
        service_type=data.get("service_type", "AI Strategy Consultation"),
        customer_phone=data.get("phone", ""),
        notes=data.get("notes", "")
    )
    return jsonify(res)


@app.route("/api/diagnostics", methods=["GET"])
def diagnostics_endpoint():
    report = run_full_system_diagnostic()
    return jsonify(report)


@app.route("/api/diagnostics/remediate", methods=["POST"])
def remediate_endpoint():
    data = request.json or {}
    action = data.get("action", "purge_cache_and_recycle_pool")
    res = execute_auto_remediation(action)
    return jsonify(res)


@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    tickets = list_escalation_tickets()
    return jsonify({"tickets": tickets})


@app.route("/api/officials/status", methods=["GET", "POST"])
def officials_status_endpoint():
    if request.method == "POST":
        data = request.json or {}
        new_status = data.get("status", "AVAILABLE")
        notice = data.get("notice", "")
        res = set_officials_status(new_status, notice)
        return jsonify(res)
    else:
        status_info = get_officials_availability()
        return jsonify(status_info)


@app.route("/api/officials/roster", methods=["GET"])
def officials_roster_endpoint():
    roster = get_all_officials_live_status()
    return jsonify({"officials": roster})


@app.route("/api/voice/transfer", methods=["POST"])
def voice_transfer_endpoint():
    data = request.json or {}
    official_id = data.get("official_id", "")
    customer_name = data.get("name", "Client")
    customer_email = data.get("email", "")
    issue = data.get("issue", "General Consultation")
    
    if not official_id:
        best = match_best_official(issue)
        official_id = best["id"]
        
    res = execute_warm_transfer(
        official_id=official_id,
        customer_name=customer_name,
        customer_email=customer_email,
        issue_summary=issue
    )
    return jsonify(res)


if __name__ == "__main__":
    print(f"🚀 Starting {config.COMPANY_NAME} Autonomous Agent Server on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
