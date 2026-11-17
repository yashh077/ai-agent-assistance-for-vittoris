"""Autonomous Voice Assistant Engine for Vittoris AI: Intake, Rescheduling & Official Notification Queue."""
import re
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

import config
from knowledge_base import search_knowledge_base, VITTORIS_KNOWLEDGE
from tools.calendar_tool import (
    get_officials_availability,
    get_available_slots,
    create_customer_dossier,
    list_customer_dossiers,
    reschedule_customer_appointment,
    clear_officials_schedule_and_notify,
    cancel_appointment
)
from tools.routing_tool import (
    match_best_official,
    execute_warm_transfer,
    get_all_officials_live_status
)


class VittorisAutonomousAgent:
    """
    Speech-to-Speech Oriented Voice Assistant for Vittoris AI.
    Focuses on:
      1. Taking customer details (Name, Phone, Related Query, Appointment Date) in officials' absence.
      2. Rescheduling existing appointments conversationally.
      3. Queueing dossiers so company officials are notified as soon as their schedule clears.
    """
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "pending_intent": "intake",
                "context": {
                    "name": None,
                    "phone": None,
                    "email": None,
                    "query": None,
                    "appointment_date": None,
                    "booking_id": None
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
        match = re.search(r'VIT-(?:DOS|APT)-[A-Z0-9]{6}', text, re.IGNORECASE)
        return match.group(0).upper() if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        # Matches patterns like +1-555-019-2834, (555) 019-2834, 9876543210, 555.019.2834
        patterns = [
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\b\d{10}\b',
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b'
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                phone_str = match.group(0).strip()
                # Clean punctuation for consistency
                clean_digits = re.sub(r'[^\d+]', '', phone_str)
                if len(clean_digits) >= 10:
                    return phone_str
        return None

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r'(?:my name is|i am|i\'m|this is|caller is|name[:\s]+)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
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
        # Check title patterns (e.g., Dr. Marcus Brody)
        title_match = re.search(r'(?:Dr\.|Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', text)
        if title_match:
            return title_match.group(0).strip()
        return None

    def _extract_date_or_slot(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        slots = get_available_slots(days_ahead=5)
        
        # Check slot 1..8
        slot_match = re.search(r'slot\s*([1-8])', text_lower)
        if slot_match:
            idx = int(slot_match.group(1)) - 1
            if 0 <= idx < len(slots):
                return slots[idx]["slot_time"]
                
        # Check natural language days
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "tomorrow"]:
            if day in text_lower:
                for s in slots:
                    if day in s["formatted"].lower() or (day == "tomorrow" and "nov" in s["formatted"].lower()):
                        return s["slot_time"]
                return f"{day.capitalize()} at 02:00 PM EST"

        # Check explicit time mentions
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', text_lower)
        if time_match:
            return f"Upcoming Business Day at {time_match.group(1).upper()} EST"
            
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
        cleaned = re.sub(r'[⚡📅🛠️🚨💡🎉✅⚠️ℹ️👨‍💼👩‍💻👨‍🔧📞👋📧🕒📋⏳]', '', cleaned)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        spoken = ". ".join(lines)
        spoken = re.sub(r'\.{2,}', '.', spoken)
        return spoken.strip()

    def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Processes voice/chat input and returns both visual markdown and spoken voice text."""
        session = self.get_or_create_session(session_id)
        ctx = session["context"]
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()
        
        session["history"].append({"sender": "customer", "text": msg_clean})
        
        # 1. Update session context from current message
        phone = self._extract_phone(msg_clean)
        if phone:
            ctx["phone"] = phone
            
        name = self._extract_name(msg_clean)
        if name:
            ctx["name"] = name
            
        email = self._extract_email(msg_clean)
        if email:
            ctx["email"] = email
            
        bid = self._extract_booking_id(msg_clean)
        if bid:
            ctx["booking_id"] = bid
            
        date_slot = self._extract_date_or_slot(msg_clean)
        if date_slot:
            ctx["appointment_date"] = date_slot

        # 2. Extract potential query details if message is descriptive
        words = msg_clean.split()
        if len(words) >= 4 and not ctx.get("query"):
            # Avoid using purely meta commands as the query
            if not any(k in msg_lower for k in ["my name is", "my phone is", "slot 1", "reschedule"]):
                ctx["query"] = msg_clean
            elif any(k in msg_lower for k in ["server", "voice bot", "integration", "pipeline", "booking", "pricing", "problem", "issue", "contract", "help"]):
                ctx["query"] = msg_clean

        official_state = get_officials_availability()

        # -----------------------------------------------------------------
        # INTENT A: Clear Officials Schedule Simulator (Admin action)
        # -----------------------------------------------------------------
        if any(w in msg_lower for w in ["clear schedule", "officials clear", "clear officials schedule"]):
            cleared_res = clear_officials_schedule_and_notify()
            text = (
                f"### 📋 Official Schedule Cleared & Notified\n\n"
                f"{cleared_res['message']}\n\n"
                f"- **Pending Dossiers Processed:** `{cleared_res['pending_dossiers_cleared']}`\n"
                f"- **Officials State:** `AVAILABLE & ONLINE`\n"
                f"- **Leadership Roster Notified:** Uday Zayn, Sarah Chen, Marcus Vance"
            )
            voice = f"Officials have cleared their schedule. All pending customer dossiers have been delivered to leadership."
            return {"text": text, "voice_script": voice, "action": {"type": "schedule_cleared", "data": cleared_res}}

        # -----------------------------------------------------------------
        # INTENT B: Reschedule Existing Appointment
        # -----------------------------------------------------------------
        if any(w in msg_lower for w in ["reschedule", "move appointment", "change appointment", "change date", "postpone"]):
            session["pending_intent"] = "rescheduling"
            
            identifier = ctx.get("booking_id") or ctx.get("phone") or ctx.get("name")
            new_date = ctx.get("appointment_date")
            
            # If both identifier and new slot provided in same turn
            if identifier and new_date:
                res = reschedule_customer_appointment(identifier, new_date)
                if res["success"]:
                    text = (
                        f"### ✅ Appointment Rescheduled & Official Notified\n\n"
                        f"- **Customer:** {res['customer_name']} ({res['customer_phone']})\n"
                        f"- **Reference:** `{res['dossier_id']}`\n"
                        f"- **Previous Date:** ~{res['old_date']}~\n"
                        f"- **New Appointment Date:** `{res['new_slot_time']}`\n"
                        f"- **Assigned Official:** {res['official_assigned']}\n\n"
                        f"> ℹ️ *The company official has been automatically updated with your new appointment time.*"
                    )
                    voice = f"Your appointment for {res['customer_name']} has been successfully rescheduled to {res['new_slot_time']}. Our official has been updated with your new time."
                    session["pending_intent"] = "intake"
                    return {"text": text, "voice_script": voice, "action": {"type": "appointment_rescheduled", "data": res}}
                else:
                    text = f"⚠️ Could not reschedule: {res.get('error')}. Please verify your phone number or reference code."
                    voice = f"I could not locate an existing booking. Could you please state your name or phone number?"
                    return {"text": text, "voice_script": voice, "action": {"type": "reschedule_lookup_failed"}}
            
            # Ask for missing reschedule info
            slots = get_available_slots(days_ahead=4)
            slots_txt = "\n".join([f"- **Slot {i+1}:** `{s['slot_time']}` ({s['formatted']})" for i, s in enumerate(slots[:4])])
            text = (
                f"### Reschedule Your Appointment\n\n"
                f"I can help you reschedule right now. Please tell me:\n"
                f"1. Your **Name** or **Phone Number**\n"
                f"2. Your **New Preferred Date** from the available slots:\n\n{slots_txt}"
            )
            voice = "I can help you reschedule your appointment. Could you please share your name or phone number, and what new date or time you prefer?"
            return {"text": text, "voice_script": voice, "action": {"type": "awaiting_reschedule_info", "slots": slots}}

        # -----------------------------------------------------------------
        # INTENT C: Customer Intake & Official Dossier Generation (Primary Focus)
        # -----------------------------------------------------------------
        # Check what information we still need from the customer
        missing_fields = []
        if not ctx.get("name"):
            missing_fields.append("name")
        if not ctx.get("phone"):
            missing_fields.append("phone number")
        if not ctx.get("query"):
            missing_fields.append("details of your query or project")
        if not ctx.get("appointment_date"):
            missing_fields.append("preferred appointment date")

        # CASE 1: All 4 key details are collected -> Generate Official Dossier
        if len(missing_fields) == 0:
            assigned_official = "Uday Zayn (Lead AI Architect) & Engineering Team"
            if any(w in ctx["query"].lower() for w in ["server", "database", "pdf", "pipeline", "crash"]):
                assigned_official = "Sarah Chen (Head of Enterprise Integrations)"
            elif any(w in ctx["query"].lower() for w in ["voice", "call", "audio", "sip", "phone"]):
                assigned_official = "Marcus Vance (Senior Solutions Engineer)"

            dossier = create_customer_dossier(
                customer_name=ctx["name"],
                customer_phone=ctx["phone"],
                related_query=ctx["query"],
                appointment_date=ctx["appointment_date"],
                customer_email=ctx.get("email") or "",
                official_assigned=assigned_official
            )
            
            text = (
                f"### 📋 Customer Dossier Recorded & Queued for Official Review\n\n"
                f"Thank you, **{ctx['name']}**. Even though our company officials are currently in closed sessions and unavailable right now, "
                f"I have taken down your full file and locked your appointment.\n\n"
                f"- **Dossier Reference:** `{dossier['dossier_id']}`\n"
                f"- **Customer Name:** {ctx['name']}\n"
                f"- **Phone Number:** `{ctx['phone']}`\n"
                f"- **Related Query:** *\"{ctx['query']}\"*\n"
                f"- **Locked Appointment Date:** `{ctx['appointment_date']}`\n"
                f"- **Assigned Official:** {assigned_official}\n"
                f"- **Official Status:** `SCHEDULE BUSY (Notification Sent)`\n\n"
                f"> 🔔 **Official Notification Protocol:**\n"
                f"> As soon as {assigned_official} clears their schedule, this complete dossier will be delivered to their dashboard "
                f"> so they are fully briefed on your inquiry before your appointment."
            )
            voice = (
                f"Thank you, {ctx['name']}. I have recorded your phone number {ctx['phone']} and your inquiry regarding {ctx['query']}. "
                f"I have locked in your appointment for {ctx['appointment_date']}. "
                f"Our company officials are currently in client sessions, but as soon as they clear their schedule, they will be directly notified "
                f"with your full file. We look forward to speaking with you!"
            )
            
            # Reset context for next inquiry
            session["context"] = {"name": None, "phone": None, "email": None, "query": None, "appointment_date": None, "booking_id": None}
            session["pending_intent"] = "intake"
            
            return {"text": text, "voice_script": voice, "action": {"type": "dossier_created", "dossier": dossier}}

        # CASE 2: Name is missing
        if "name" in missing_fields:
            text = (
                f"### Vittoris AI Voice Assistant\n\n"
                f"> ℹ️ **Notice:** Company officials and lead architects are currently in closed meetings and unavailable right now.\n\n"
                f"I am here to take all your details, record your specific inquiry, and lock in an appointment date for you. "
                f"When the officials clear their schedule, they will be immediately notified with your file.\n\n"
                f"**To get started, could you please tell me your Full Name and Phone Number?**"
            )
            voice = (
                "Hello! You have reached Vittoris AI. Our company officials are currently in closed meetings and unavailable right now. "
                "However, I can take down your details, record your inquiry, and lock in an appointment date for you. "
                "Could you please start by telling me your full name and phone number?"
            )
            return {"text": text, "voice_script": voice, "action": {"type": "prompting_name_phone"}}

        # CASE 3: Phone number is missing
        if "phone number" in missing_fields:
            text = f"Thank you, **{ctx['name']}**. What is the best **Phone Number** where our officials can reach you once their schedule clears?"
            voice = f"Thank you, {ctx['name']}. What is the best phone number where our company officials can reach you once their schedule clears?"
            return {"text": text, "voice_script": voice, "action": {"type": "prompting_phone"}}

        # CASE 4: Query / problem description is missing
        if "details of your query or project" in missing_fields:
            text = (
                f"Got it! Phone number saved as `{ctx['phone']}`.\n\n"
                f"Could you briefly describe your **query or the problem** you need help with? "
                f"(e.g., *voice agent automation, server/pipeline crash, custom infrastructure, or pricing consultation*)"
            )
            voice = f"Got it. Could you briefly describe your inquiry or the problem you are experiencing, so I can brief the company official?"
            return {"text": text, "voice_script": voice, "action": {"type": "prompting_query"}}

        # CASE 5: Appointment date is missing
        if "preferred appointment date" in missing_fields:
            slots = get_available_slots(days_ahead=4)
            slots_fmt = "\n".join([f"- **Slot {i+1}:** `{s['slot_time']}` ({s['formatted']})" for i, s in enumerate(slots[:4])])
            text = (
                f"Understood. Inquiry logged: *\"{ctx['query']}\"*.\n\n"
                f"What **appointment date and time** works best for you? Here are our earliest open slots:\n\n"
                f"{slots_fmt}\n\n"
                f"*(You can simply say 'Slot 1', 'Tomorrow at 2 PM', or any preferred day)*"
            )
            voice = "What appointment date or time works best for you? We have open slots starting tomorrow at 10 AM, 2 PM, or Friday at 11:30 AM."
            return {"text": text, "voice_script": voice, "action": {"type": "prompting_date", "slots": slots}}

        # Fallback General Response
        kb_ans = search_knowledge_base(msg_clean)
        return {"text": kb_ans, "voice_script": self._clean_for_voice(kb_ans), "action": {"type": "general_info"}}
