"""Autonomous Calendar & Appointment Booking Tool with SQLite persistence and Official Dossiers."""
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import config

def init_db():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT,
        service_type TEXT NOT NULL,
        slot_time TEXT NOT NULL,
        official_assigned TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'CONFIRMED',
        notes TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    # Official Status table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS officials_state (
        id INTEGER PRIMARY KEY,
        current_status TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        notice TEXT
    )
    """)
    
    # Customer Dossiers / Notification queue for officials when they clear their schedule
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_dossiers (
        id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT,
        related_query TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        official_assigned TEXT NOT NULL,
        official_status TEXT NOT NULL,
        review_status TEXT NOT NULL DEFAULT 'PENDING_OFFICIAL_CLEARANCE',
        created_at TEXT NOT NULL
    )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM officials_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO officials_state (id, current_status, updated_at, notice) VALUES (1, ?, ?, ?)",
            (
                config.DEFAULT_OFFICIALS_STATUS,
                datetime.now().isoformat(),
                "Officials currently in closed client enterprise delivery & meetings. Autonomous Agent taking customer dossiers & scheduling."
            )
        )
        
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()


def get_officials_availability() -> Dict:
    """Returns the current live operational status of Vittoris officials."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT current_status, notice, updated_at FROM officials_state WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    
    status = row[0] if row else config.DEFAULT_OFFICIALS_STATUS
    notice = row[1] if row else "Autonomous system active."
    
    return {
        "status": status,
        "is_available_right_now": (status == "AVAILABLE"),
        "notice": notice,
        "officials_directory": config.OFFICIALS_DIRECTORY,
        "business_hours": "09:00 AM - 06:00 PM EST (Mon - Fri)"
    }


def set_officials_status(status: str, notice: str = "") -> Dict:
    """Toggle official status (e.g. AVAILABLE, OUT_OF_OFFICE, IN_MEETINGS)."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("UPDATE officials_state SET current_status = ?, notice = ?, updated_at = ? WHERE id = 1", (status, notice, now_str))
    conn.commit()
    conn.close()
    return {"status": status, "notice": notice, "updated_at": now_str}


def get_available_slots(days_ahead: int = 5) -> List[Dict]:
    """Generates and returns open appointment slots over the next upcoming business days."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT slot_time FROM appointments WHERE status = 'CONFIRMED'")
    booked_slots = {row[0] for row in cursor.fetchall()}
    conn.close()

    now = datetime.now()
    available_slots = []
    
    day_offset = 0
    while len(available_slots) < 8 and day_offset < 14:
        target_date = now + timedelta(days=day_offset)
        if target_date.weekday() in [5, 6]:
            day_offset += 1
            continue
            
        for hour, minute in [(10, 0), (11, 30), (14, 0), (15, 30), (17, 0)]:
            slot_dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if slot_dt > now + timedelta(hours=2):
                slot_str = slot_dt.strftime("%Y-%m-%d %H:%M EST")
                if slot_str not in booked_slots:
                    available_slots.append({
                        "slot_time": slot_str,
                        "formatted": slot_dt.strftime("%A, %b %d at %I:%M %p EST"),
                        "official": "Uday Zayn & Solutions Team",
                        "duration_minutes": 30
                    })
                    if len(available_slots) >= 8:
                        break
        day_offset += 1
        
    return available_slots


def create_customer_dossier(
    customer_name: str,
    customer_phone: str,
    related_query: str,
    appointment_date: str,
    customer_email: str = "",
    official_assigned: str = "Uday Zayn (Lead AI Architect)"
) -> Dict:
    """
    Records customer details (Name, Phone, Query) and assigns an appointment date 
    in the absence of officials. When the official clears their schedule, they are notified with this dossier.
    """
    dossier_id = f"VIT-DOS-{uuid.uuid4().hex[:6].upper()}"
    created_at = datetime.now().isoformat()
    avail = get_officials_availability()
    official_status = avail["status"]
    
    # Default email if not provided
    email = customer_email.strip() if customer_email else f"{customer_name.lower().replace(' ', '.')}@client-notify.com"
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO customer_dossiers (
        id, customer_name, customer_phone, customer_email, 
        related_query, appointment_date, official_assigned, 
        official_status, review_status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_OFFICIAL_CLEARANCE', ?)
    """, (
        dossier_id, customer_name, customer_phone, email,
        related_query, appointment_date, official_assigned,
        official_status, created_at
    ))
    
    # Also record in standard appointments table
    cursor.execute("""
    INSERT OR REPLACE INTO appointments (
        id, customer_name, customer_email, customer_phone, 
        service_type, slot_time, official_assigned, status, notes, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, ?)
    """, (
        dossier_id, customer_name, email, customer_phone,
        f"Inquiry: {related_query[:40]}", appointment_date, 
        official_assigned, f"Recorded in absence of officials. Query: {related_query}", created_at
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "dossier_id": dossier_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_email": email,
        "related_query": related_query,
        "appointment_date": appointment_date,
        "official_assigned": official_assigned,
        "official_status": official_status,
        "review_status": "PENDING_OFFICIAL_CLEARANCE",
        "message": (
            f"Details successfully recorded for {customer_name}. Phone: {customer_phone}. "
            f"Appointment locked for {appointment_date}. "
            f"Company official ({official_assigned}) will be notified with your inquiry when their schedule clears."
        )
    }


def list_customer_dossiers() -> List[Dict]:
    """Returns all customer dossiers waiting for official schedule clearance or reviewed."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, customer_name, customer_phone, customer_email, related_query, 
           appointment_date, official_assigned, official_status, review_status, created_at 
    FROM customer_dossiers ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    dossiers = []
    for r in rows:
        dossiers.append({
            "id": r[0],
            "customer_name": r[1],
            "customer_phone": r[2],
            "customer_email": r[3],
            "related_query": r[4],
            "appointment_date": r[5],
            "official_assigned": r[6],
            "official_status": r[7],
            "review_status": r[8],
            "created_at": r[9]
        })
    return dossiers


def reschedule_customer_appointment(identifier: str, new_slot_time: str) -> Dict:
    """
    Reschedules an appointment by booking reference ID, customer phone, or customer name.
    Updates both appointments and customer dossiers.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Try finding by dossier/appointment ID, phone, or name
    cursor.execute("""
    SELECT id, customer_name, customer_phone, appointment_date, official_assigned 
    FROM customer_dossiers 
    WHERE id = ? OR customer_phone = ? OR customer_name LIKE ?
    ORDER BY created_at DESC LIMIT 1
    """, (identifier.upper(), identifier, f"%{identifier}%"))
    row = cursor.fetchone()
    
    if not row:
        # Check standard appointments
        cursor.execute("SELECT id, customer_name, customer_phone, slot_time, official_assigned FROM appointments WHERE id = ? OR customer_phone = ? OR customer_name LIKE ? LIMIT 1", (identifier.upper(), identifier, f"%{identifier}%"))
        row = cursor.fetchone()
        
    if not row:
        conn.close()
        return {"success": False, "error": f"No booking or customer dossier found for '{identifier}'."}
        
    found_id, name, phone, old_date, official = row
    
    cursor.execute("UPDATE customer_dossiers SET appointment_date = ?, review_status = 'RESCHEDULED_PENDING_REVIEW' WHERE id = ?", (new_slot_time, found_id))
    cursor.execute("UPDATE appointments SET slot_time = ?, notes = notes || ' [Rescheduled]' WHERE id = ?", (new_slot_time, found_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "dossier_id": found_id,
        "customer_name": name,
        "customer_phone": phone,
        "old_date": old_date,
        "new_slot_time": new_slot_time,
        "official_assigned": official,
        "message": f"Appointment for {name} has been successfully rescheduled to {new_slot_time}. The assigned official ({official}) has been updated."
    }


def clear_officials_schedule_and_notify() -> Dict:
    """
    Simulates the official clearing their calendar/schedule.
    Delivers and confirms all pending customer dossiers.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM customer_dossiers WHERE review_status LIKE 'PENDING%'")
    pending_count = cursor.fetchone()[0]
    
    cursor.execute("UPDATE customer_dossiers SET review_status = 'OFFICIAL_NOTIFIED_AND_ACCEPTED'")
    set_officials_status("AVAILABLE", "Officials have cleared their schedule and received all customer dossiers.")
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "pending_dossiers_cleared": pending_count,
        "officials_status": "AVAILABLE",
        "message": f"Officials schedule cleared! {pending_count} customer dossier(s) have been delivered to Uday Zayn and the engineering leadership team."
    }


def book_appointment(customer_name: str, customer_email: str, slot_time: str, service_type: str = "AI Strategy & Diagnostic", customer_phone: str = "", notes: str = "") -> Dict:
    """Standard appointment booking helper."""
    return create_customer_dossier(
        customer_name=customer_name,
        customer_phone=customer_phone if customer_phone else "Not Provided",
        related_query=notes if notes else service_type,
        appointment_date=slot_time,
        customer_email=customer_email
    )


def reschedule_appointment(booking_id: str, new_slot_time: str) -> Dict:
    """Alias for rescheduling."""
    return reschedule_customer_appointment(booking_id, new_slot_time)


def cancel_appointment(booking_id: str) -> Dict:
    """Cancels a scheduled appointment."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ?", (booking_id.upper(),))
    cursor.execute("UPDATE customer_dossiers SET review_status = 'CANCELLED_BY_CUSTOMER' WHERE id = ?", (booking_id.upper(),))
    conn.commit()
    conn.close()
    return {"success": True, "booking_id": booking_id.upper(), "message": f"Appointment {booking_id.upper()} has been cancelled."}


def list_all_appointments() -> List[Dict]:
    """Returns all appointments."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, customer_email, customer_phone, service_type, slot_time, official_assigned, status, notes, created_at FROM appointments ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0], "customer_name": r[1], "customer_email": r[2],
            "customer_phone": r[3], "service_type": r[4], "slot_time": r[5],
            "official_assigned": r[6], "status": r[7], "notes": r[8], "created_at": r[9]
        })
    return results
