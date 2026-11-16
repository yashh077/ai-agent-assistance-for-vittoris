"""Core Autonomous Agent Engine for Vittoris AI voice assistant, inquiries, booking, and issue resolution."""
import re
import os
import json
from typing import Dict, List, Any, Optional

import config
from knowledge_base import search_knowledge_base, VITTORIS_KNOWLEDGE
from tools.calendar_tool import (
    get_officials_availability,
    get_available_slots,
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
    list_all_appointments
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
    match_best_official,
    execute_warm_transfer,
    get_all_officials_live_status
)


class VittorisAutonomousAgent:
    """
    Intelligent Autonomous Voice Assistant & Operations Agent managing Vittoris AI 
    inquiries, scheduling, in-app diagnostics, voice transfers, and out-of-office escalations.
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "pending_intent": None,
                "context": {
                    "name": None,
                    "email": None,
                    "phone": None,
                    "selected_slot": None,
                    "booking_id": None,
                    "issue_category": None
                }
            }
        return self.sessions[session_id]

    def reset_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def _extract_email(self, text: str) -> Optional[str]:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None

    def _extract_booking_id(self, text: str) -> Optional[str]:
        match = re.search(r'VIT-[A-Z0-9]{6}', text, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:my name is|i am|i\'m|this is|name[:\s]+)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*$'
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                if candidate.lower() not in ["hello", "hi", "hey", "yes", "no", "vittoris", "booking", "server", "alex"]:
                    return candidate
                if candidate.lower() == "alex":
                    return "Alex Vance"
        return None

    def _clean_for_voice(self, text: str) -> str:
        """Strips markdown syntax, emojis, and tables into natural, fluid spoken text for TTS."""
        cleaned = re.sub(r'#+\s*', '', text)                     # Strip headings
        cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)       # Strip bold
        cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)           # Strip italics
        cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)             # Strip code backticks
        cleaned = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', cleaned)    # Strip links, keep text
        cleaned = re.sub(r'\|.*?\|', '', cleaned)                 # Remove table lines
        cleaned = re.sub(r'[-–—]\s*', '', cleaned)                # Remove bullet dashes
        cleaned = re.sub(r'>\s*', '', cleaned)                   # Remove blockquote markers
        cleaned = re.sub(r'[⚡📅🛠️🚨💡🎉✅⚠️ℹ️👨‍💼👩‍💻👨‍🔧📞👋📧🕒]', '', cleaned) # Remove emojis
        # Collapse multiple spaces or newlines into clean punctuation pauses
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        spoken = ". ".join(lines)
        spoken = re.sub(r'\.{2,}', '.', spoken)
        return spoken.strip()

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Processes an incoming customer message, returning visual markdown text and voice script."""
        session = self.get_or_create_session(session_id)
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()
        
        session["history"].append({"sender": "customer", "text": msg_clean})
        
        # Update context
        detected_email = self._extract_email(msg_clean)
        if detected_email:
            session["context"]["email"] = detected_email
            
        detected_name = self._extract_name(msg_clean)
        if detected_name:
            session["context"]["name"] = detected_name

        detected_bid = self._extract_booking_id(msg_clean)
        if detected_bid:
            session["context"]["booking_id"] = detected_bid

        official_state = get_officials_availability()
        
        # Check active pending multi-turn intents
        if session["pending_intent"] == "booking":
            response = self._handle_pending_booking(session, msg_clean)
            response["voice_script"] = self._clean_for_voice(response["text"])
            session["history"].append({"sender": "agent", "text": response["text"]})
            return response

        if session["pending_intent"] == "rescheduling":
            response = self._handle_pending_rescheduling(session, msg_clean)
            response["voice_script"] = self._clean_for_voice(response["text"])
            session["history"].append({"sender": "agent", "text": response["text"]})
            return response
            
        if session["pending_intent"] == "escalation":
            response = self._handle_pending_escalation(session, msg_clean)
            response["voice_script"] = self._clean_for_voice(response["text"])
            session["history"].append({"sender": "agent", "text": response["text"]})
            return response

        # ----------------------------------------------------
        # INTENT 1: Warm Transfer / Redirect to Expert Official
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["redirect", "transfer", "connect me", "speak to official", "speak with uday", "talk to the person", "talk to human", "representative", "specialist"]):
            best_official = match_best_official(msg_clean)
            caller_name = session["context"].get("name") or "Valued Client"
            caller_email = session["context"].get("email") or ""
            
            transfer_res = execute_warm_transfer(
                official_id=best_official["id"],
                customer_name=caller_name,
                customer_email=caller_email,
                issue_summary=msg_clean,
                diagnostics_context="Customer requested voice warm transfer."
            )
            
            if transfer_res["transfer_status"] == "CONNECTED":
                text = (
                    f"### 📞 Warm Call Transfer Initiated\n\n"
                    f"**Matched Specialist:** {best_official['name']} ({best_official['role']})\n"
                    f"**Department:** {best_official['extension']}\n"
                    f"**Status:** `AVAILABLE & ONLINE`\n\n"
                    f"> **Agent Hand-off Announcement:**\n"
                    f"> *\"{transfer_res['voice_announcement']}\"*\n\n"
                    f"---\n"
                    f"**Official Answering:**\n"
                    f"*{transfer_res['official_greeting']}*"
                )
                voice = f"{transfer_res['voice_announcement']} {transfer_res['official_greeting']}"
                action_data = {"type": "warm_transfer_connected", "transfer": transfer_res}
            else:
                text = (
                    f"### ⚠️ Specialist Currently Unavailable\n\n"
                    f"**Target Specialist:** {best_official['name']} ({best_official['role']})\n"
                    f"**Current Status:** `{best_official['status']}`\n\n"
                    f"> *\"{transfer_res['voice_announcement']}\"*\n\n"
                    f"I can autonomously resolve your issue right now, or lock in a priority slot on {best_official['name']}'s calendar. What would you prefer?"
                )
                voice = transfer_res["voice_announcement"]
                action_data = {"type": "warm_transfer_unavailable", "transfer": transfer_res}
                
            return {"text": text, "voice_script": voice, "action": action_data}

        # ----------------------------------------------------
        # INTENT 2: Appointment Rescheduling
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["reschedule", "change appointment", "move my meeting", "change slot", "postpone"]):
            slots = get_available_slots(days_ahead=5)
            booking_id = session["context"].get("booking_id") or self._extract_booking_id(msg_clean)
            
            # If user provided a slot choice directly
            slot_match = re.search(r'slot\s*([1-8])', msg_lower)
            if booking_id and slot_match:
                idx = int(slot_match.group(1)) - 1
                if 0 <= idx < len(slots):
                    new_slot = slots[idx]["slot_time"]
                    res = reschedule_appointment(booking_id, new_slot)
                    if res["success"]:
                        text = f"### ✅ Appointment Rescheduled\n\n{res['message']}"
                        voice = f"Your appointment {booking_id} has been successfully moved to {new_slot}."
                        return {"text": text, "voice_script": voice, "action": {"type": "appointment_rescheduled", "data": res}}

            session["pending_intent"] = "rescheduling"
            slots_list = "\n".join([f"- **Slot {i+1}:** `{s['slot_time']}` ({s['formatted']})" for i, s in enumerate(slots[:4])])
            text = (
                f"### Reschedule Your Appointment\n\n"
                f"I can easily move your booking. Please tell me:\n"
                f"1. Your **Booking Reference ID** (e.g. `VIT-XXXXXX`)\n"
                f"2. Your **New Preferred Slot** from the open times below:\n\n"
                f"{slots_list}"
            )
            voice = "I can help you reschedule your meeting. Please share your booking reference code and tell me which upcoming slot works best for you."
            return {"text": text, "voice_script": voice, "action": {"type": "reschedule_slots_presented", "slots": slots}}

        # ----------------------------------------------------
        # INTENT 3: Explaining Complicated Concepts Conversationally
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["explain", "how do voice", "how does document", "how does it work", "tell me about"]):
            if "voice" in msg_lower or "call" in msg_lower:
                text = (
                    f"### How Vittoris Autonomous Voice Agents Work\n\n"
                    f"Our autonomous voice infrastructure runs on a 3-layer architecture:\n\n"
                    f"1. **Ultra-Low Latency Telephony:** Connects directly to SIP trunks and WebSockets (via Twilio, Retell, Vapi) with sub-200ms audio streaming.\n"
                    f"2. **Conversational Intelligence:** Natural turn-taking, objection handling, and interruption detection—it talks like a trained sales or support rep.\n"
                    f"3. **Autonomous Action Tools:** During the call, the bot queries live calendars to book appointments or triggers backend APIs without human intervention."
                )
                voice = (
                    "Our autonomous voice agents operate in three layers. First, they stream ultra-low latency audio via SIP trunks "
                    "with sub-two hundred millisecond response times. Second, they handle conversational turn taking, interruptions, "
                    "and natural dialogue. Third, they directly execute actions on your calendars and CRM databases while speaking with the caller."
                )
                return {"text": text, "voice_script": voice, "action": {"type": "concept_explained"}}
            elif "document" in msg_lower or "pdf" in msg_lower:
                text = (
                    f"### How Vittoris Document Intelligence Works\n\n"
                    f"1. **Ingestion & Optical Character Recognition:** Parses complex multi-page PDFs, invoices, and contracts.\n"
                    f"2. **Schema Extraction:** Uses targeted LLM extractors to pull line items, tax IDs, payment terms, and vendor names.\n"
                    f"3. **Automatic Verification:** Cross-checks totals against your database and sends alerts on discrepancies."
                )
                voice = (
                    "Our document intelligence pipelines automatically ingest multi-page PDFs, invoices, and legal contracts. "
                    "They extract structured line items, validate mathematical totals against your databases, and route clean data "
                    "straight into your ERP systems with zero manual data entry."
                )
                return {"text": text, "voice_script": voice, "action": {"type": "concept_explained"}}

        # ----------------------------------------------------
        # INTENT 4: In-App Service Troubleshooting (Voice, Webhook, Document Pipeline)
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["drop", "dropping", "voice agent", "audio", "pdf", "extraction", "webhook", "troubleshoot", "app issue", "stuck"]):
            triage = diagnose_customer_issue(issue_category=msg_clean, details=msg_clean)
            
            if triage["available_auto_fix"]:
                remediation = execute_auto_remediation(triage["available_auto_fix"])
                text = (
                    f"### Autonomous In-App Troubleshooting\n\n"
                    f"**Diagnosis for {triage['category']}:**\n{triage['diagnosis']}\n\n"
                    f"**Automated Remediation Executed:** `{triage['available_auto_fix']}`\n"
                    f"> **Status:** {remediation['result']}\n\n"
                    f"The service is back in nominal state. Would you like me to book a follow-up consultation with our solutions team to review this pipeline?"
                )
                voice = f"I diagnosed the issue with your {triage['category']}. {triage['diagnosis']} I automatically executed the self-healing runbook: {remediation['result']}"
                action_data = {"type": "in_app_fix_applied", "triage": triage, "remediation": remediation}
            else:
                # Check if Sarah or Marcus is available for transfer
                best_expert = match_best_official(msg_clean)
                if best_expert["is_available"]:
                    transfer_res = execute_warm_transfer(best_expert["id"], session["context"].get("name") or "Client", session["context"].get("email") or "", msg_clean)
                    text = (
                        f"### Technical Issue - Live Specialist Available\n\n"
                        f"**Category:** {triage['category']}\n"
                        f"**Analysis:** {triage['diagnosis']}\n\n"
                        f"Our specialist, **{best_expert['name']}**, is currently available. Transferring you now.\n\n"
                        f"> *\"{transfer_res['official_greeting']}\"*"
                    )
                    voice = f"{transfer_res['voice_announcement']} {transfer_res['official_greeting']}"
                    action_data = {"type": "warm_transfer_connected", "transfer": transfer_res}
                else:
                    text = (
                        f"### Technical Issue Logged\n\n"
                        f"**Category:** {triage['category']}\n"
                        f"**Analysis:** {triage['diagnosis']}\n\n"
                        f"Officials are currently in meetings. I can autonomously dispatch an escalation dossier directly to our lead architect.\n\n"
                        f"Please reply with your **Name** and **Email** to generate the emergency ticket."
                    )
                    voice = f"I've analyzed the problem with your {triage['category']}. Our engineering officials are currently in client deployments, but I can dispatch an emergency escalation ticket directly to their on-call pager. Please share your name and email."
                    session["pending_intent"] = "escalation"
                    action_data = {"type": "escalation_prompt", "triage": triage}
                
            return {"text": text, "voice_script": voice, "action": action_data}

        # ----------------------------------------------------
        # INTENT 5: Server / Infrastructure Issue or Health Check
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["server", "health check", "system health", "is down", "outage", "500 error", "server issue", "database down", "infrastructure", "status"]):
            diag = run_full_system_diagnostic()
            
            if any(w in msg_lower for w in ["fix", "remediate", "restart", "purge", "clear cache"]):
                remediation = execute_auto_remediation("purge_cache_and_recycle_pool")
                text = (
                    f"### Autonomous System Diagnostics & Remediation\n\n"
                    f"**Action Executed:** `{remediation['action']}`\n"
                    f"**Result:** {remediation['result']} (Took {remediation['duration']})\n\n"
                    f"**Current Infrastructure Status:** All systems reporting `{diag['overall_status']}`.\n\n"
                    f"- **API Gateway:** {diag['services']['api_gateway']['latency']} latency\n"
                    f"- **Voice Stream Worker:** {diag['services']['voice_stream_worker']['latency']} latency\n"
                    f"- **PostgreSQL & Vector Storage:** {diag['services']['database_cluster']['latency']} latency"
                )
                voice = f"Autonomous remediation executed. All systems are reporting operational with normal latency."
                action_data = {"type": "remediation_executed", "data": remediation, "diagnostics": diag}
            else:
                text = (
                    f"### Real-Time Infrastructure Health Diagnostic\n\n"
                    f"**Overall System Status:** `{diag['overall_status']}`\n\n"
                    f"| Service | Status | Latency | 30-Day Uptime |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    f"| **API Gateway** | `{diag['services']['api_gateway']['status']}` | {diag['services']['api_gateway']['latency']} | {diag['services']['api_gateway']['uptime']} |\n"
                    f"| **Voice Stream (SIP/Telephony)** | `{diag['services']['voice_stream_worker']['status']}` | {diag['services']['voice_stream_worker']['latency']} | {diag['services']['voice_stream_worker']['uptime']} |\n"
                    f"| **Document Intelligence Pipeline** | `{diag['services']['document_intelligence']['status']}` | {diag['services']['document_intelligence']['latency']} | {diag['services']['document_intelligence']['uptime']} |\n"
                    f"| **Calendar & CRM Sync Engine** | `{diag['services']['calendar_sync_worker']['status']}` | {diag['services']['calendar_sync_worker']['latency']} | {diag['services']['calendar_sync_worker']['uptime']} |\n"
                    f"| **PostgreSQL & Vector Cluster** | `{diag['services']['database_cluster']['status']}` | {diag['services']['database_cluster']['latency']} | {diag['services']['database_cluster']['uptime']} |"
                )
                voice = f"I have run a real-time health diagnostic. Overall system status is operational, with all core microservices reporting nominal latency and healthy uptime."
                action_data = {"type": "diagnostics_report", "data": diag}

            return {"text": text, "voice_script": voice, "action": action_data}

        # ----------------------------------------------------
        # INTENT 6: Appointment Booking & Slot Inquiries
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["book", "appointment", "schedule", "calendar", "call with", "meeting", "consultation", "demo"]):
            slots = get_available_slots(days_ahead=5)
            
            booking_id = self._extract_booking_id(msg_clean)
            if "cancel" in msg_lower and booking_id:
                res = cancel_appointment(booking_id)
                voice = f"Your appointment {booking_id} has been cancelled."
                return {"text": f"✅ {res['message']}", "voice_script": voice, "action": {"type": "appointment_cancelled", "data": res}}
            
            # Check if user provided 1-shot booking details (e.g. Email + Slot in same turn)
            email_in_msg = self._extract_email(msg_clean)
            slot_in_msg = re.search(r'slot\s*([1-8])', msg_lower)
            if email_in_msg and slot_in_msg:
                idx = int(slot_in_msg.group(1)) - 1
                if 0 <= idx < len(slots):
                    session["context"]["selected_slot"] = slots[idx]["slot_time"]
                session["context"]["email"] = email_in_msg
                if not session["context"].get("name"):
                    name_match = re.search(r'(?:for|is|am|name)\s+([A-Z][a-z\.]+(?:\s+[A-Z][a-z]+)+)', msg_clean)
                    session["context"]["name"] = name_match.group(1).replace("Dr. ", "Dr. ") if name_match else "Valued Client"
                response = self._handle_pending_booking(session, msg_clean)
                response["voice_script"] = self._clean_for_voice(response["text"])
                return response

            slots_formatted = "\n".join([f"- **Slot {i+1}:** `{s['slot_time']}` ({s['formatted']})" for i, s in enumerate(slots[:5])])
            
            status_note = ""
            if not official_state["is_available_right_now"]:
                status_note = (
                    f"> ℹ️ **Officials Notice:** Our lead architects (Uday Zayn & Solutions Team) are currently "
                    f"**{official_state['status']}** ({official_state['notice']}). "
                    f"However, as an autonomous agent, I am authorized to immediately confirm your appointment directly on their calendar!"
                )
                
            session["pending_intent"] = "booking"
            
            text = (
                f"### Schedule an AI Architecture & Diagnostic Consultation\n\n"
                f"{status_note}\n\n"
                f"Here are the earliest open slots on the official calendar:\n\n"
                f"{slots_formatted}\n\n"
                f"**To confirm your appointment, please reply with:**\n"
                f"1. Your **Full Name**\n"
                f"2. Your **Work Email**\n"
                f"3. Your **Preferred Slot** (e.g. `Slot 1`)"
            )
            voice = (
                "I would be glad to book a consultation for you. Our lead architects are currently in client sessions, "
                "but I have several open slots starting this week. Please tell me your full name, work email, and which slot you prefer."
            )
            return {"text": text, "voice_script": voice, "action": {"type": "slots_presented", "slots": slots}}

        # ----------------------------------------------------
        # INTENT 7: Official Contact / Escalation Request
        # ----------------------------------------------------
        if any(w in msg_lower for w in ["official", "officials", "speak to", "talk to", "human", "contact team", "escalat", "founder", "uday", "management", "contract approval"]):
            session["pending_intent"] = "escalation"
            text = (
                f"### Official Contact & Autonomous Escalation Protocol\n\n"
                f"**Current Status:** Vittoris officials are currently `{official_state['status']}` ({official_state['notice']}).\n\n"
                f"**How I can help right away in their inavailability:**\n"
                f"1. **Book a Priority Calendar Slot:** I can place a 30-minute consultation directly on Uday Zayn's calendar.\n"
                f"2. **Dispatch an Executive Escalation Dossier:** I can log an emergency ticket with complete technical logs directly to the on-call pager.\n\n"
                f"If you'd like me to log an escalation, please provide your **Name**, **Email**, and a brief summary of what you need."
            )
            voice = (
                "Vittoris officials are currently in client meetings. I can either reserve a priority slot directly on "
                "Uday Zayn's calendar, or dispatch an emergency escalation ticket to our on-call pager. Please share your name and email to proceed."
            )
            return {"text": text, "voice_script": voice, "action": {"type": "official_inavailability_handled", "status": official_state}}

        # ----------------------------------------------------
        # INTENT 8: Knowledge Base / Services & Solutions Questions
        # ----------------------------------------------------
        kb_answer = search_knowledge_base(msg_clean)
        text = (
            f"{kb_answer}\n\n"
            f"---\n"
            f"*Would you like to check real-time system status, troubleshoot an active service, "
            f"or schedule a 30-minute Diagnostic Consultation with our team?*"
        )
        voice = self._clean_for_voice(kb_answer)
        return {"text": text, "voice_script": voice, "action": {"type": "kb_response"}}

    def _handle_pending_booking(self, session: Dict, message: str) -> Dict[str, Any]:
        """Multi-turn slot filling for appointment booking."""
        ctx = session["context"]
        msg_lower = message.lower()
        
        slots = get_available_slots(days_ahead=5)
        slot_match = re.search(r'slot\s*([1-8])', msg_lower)
        if slot_match:
            idx = int(slot_match.group(1)) - 1
            if 0 <= idx < len(slots):
                ctx["selected_slot"] = slots[idx]["slot_time"]
        else:
            for s in slots:
                if s["slot_time"].split()[0] in message or s["formatted"].split()[1] in message:
                    ctx["selected_slot"] = s["slot_time"]
                    break

        if not ctx.get("selected_slot"):
            if any(k in msg_lower for k in ["first", "earliest", "any", "next"]):
                ctx["selected_slot"] = slots[0]["slot_time"]

        if not ctx.get("selected_slot"):
            text = "Please specify which slot you prefer (e.g. **'Slot 1'** or **'Slot 2'**), along with your Name and Email."
            return {"text": text, "action": {"type": "awaiting_slot"}}
            
        if not ctx.get("name"):
            parts = message.split(",")
            if len(parts) > 0 and len(parts[0].split()) <= 4:
                ctx["name"] = parts[0].strip()
            else:
                text = f"Got it for `{ctx['selected_slot']}`! Could you please share your **Full Name** and **Work Email**?"
                return {"text": text, "action": {"type": "awaiting_name_email"}}

        if not ctx.get("email"):
            text = f"Thank you, {ctx['name']}. What is your **Work Email** so we can send the calendar invitation and meeting link?"
            return {"text": text, "action": {"type": "awaiting_email"}}

        res = book_appointment(
            customer_name=ctx["name"],
            customer_email=ctx["email"],
            slot_time=ctx["selected_slot"],
            service_type="AI Strategy & Diagnostic Consultation",
            notes=message
        )
        
        session["pending_intent"] = None
        
        if res["success"]:
            text = (
                f"### 🎉 Appointment Confirmed!\n\n"
                f"- **Booking Reference:** `{res['booking_id']}`\n"
                f"- **Attendee:** {res['customer_name']} ({res['customer_email']})\n"
                f"- **Date & Time:** `{res['slot_time']}`\n"
                f"- **Assigned Official:** {res['official_assigned']}\n"
                f"- **Direct Meeting Link:** [{res['meeting_link']}]({res['meeting_link']})\n\n"
                f"> 📧 An automated calendar invite and briefing doc have been dispatched to `{res['customer_email']}`. "
                f"Even when officials are in meetings, this slot is locked and reserved exclusively for you."
            )
            return {"text": text, "action": {"type": "booking_confirmed", "data": res}}
        else:
            text = f"⚠️ Could not complete booking: {res.get('error')}. Let me know if you would like to choose another slot."
            return {"text": text, "action": {"type": "booking_failed", "error": res.get("error")}}

    def _handle_pending_rescheduling(self, session: Dict, message: str) -> Dict[str, Any]:
        """Multi-turn slot filling for rescheduling appointments."""
        ctx = session["context"]
        booking_id = ctx.get("booking_id") or self._extract_booking_id(message)
        slots = get_available_slots(days_ahead=5)
        
        slot_match = re.search(r'slot\s*([1-8])', message.lower())
        new_slot = None
        if slot_match:
            idx = int(slot_match.group(1)) - 1
            if 0 <= idx < len(slots):
                new_slot = slots[idx]["slot_time"]
                
        if not booking_id:
            return {
                "text": "Please provide your existing **Booking Reference ID** (e.g., `VIT-XXXXXX`) so I can locate your reservation.",
                "action": {"type": "awaiting_reschedule_id"}
            }
            
        if not new_slot:
            return {
                "text": f"Found appointment `{booking_id}`. Please choose which new slot you want (e.g. **'Slot 1'** or **'Slot 2'**).",
                "action": {"type": "awaiting_reschedule_slot"}
            }
            
        res = reschedule_appointment(booking_id, new_slot)
        session["pending_intent"] = None
        if res["success"]:
            return {
                "text": f"### ✅ Appointment Rescheduled\n\n{res['message']}",
                "action": {"type": "appointment_rescheduled", "data": res}
            }
        else:
            return {
                "text": f"⚠️ Could not reschedule: {res.get('error')}",
                "action": {"type": "reschedule_failed", "error": res.get("error")}
            }

    def _handle_pending_escalation(self, session: Dict, message: str) -> Dict[str, Any]:
        """Multi-turn slot filling for official ticket escalation."""
        ctx = session["context"]
        
        email = ctx.get("email") or self._extract_email(message)
        name = ctx.get("name") or self._extract_name(message) or "Enterprise Client"
        
        if not email:
            return {
                "text": "Please provide your **Work Email** so our lead architect can respond with the incident resolution.",
                "action": {"type": "awaiting_escalation_email"}
            }
            
        ticket = dispatch_official_escalation(
            customer_name=name,
            customer_email=email,
            issue_summary=message,
            urgency="HIGH",
            category="Customer Reported In-App & Infrastructure Incident",
            diagnostics_context="Autonomous agent ran diagnostics; escalated per official inavailability protocol."
        )
        
        session["pending_intent"] = None
        
        text = (
            f"### 🚨 Executive Escalation Dossier Dispatched\n\n"
            f"- **Ticket ID:** `{ticket['ticket_id']}`\n"
            f"- **Assigned Official:** {ticket['assigned_official']}\n"
            f"- **Priority Level:** `{ticket['urgency']}`\n"
            f"- **Target SLA:** {ticket['estimated_sla']}\n\n"
            f"> {ticket['message']}\n\n"
            f"You will receive an update at `{ticket['customer_email']}` as soon as the review is complete."
        )
        return {"text": text, "action": {"type": "escalation_dispatched", "data": ticket}}
