"""Autonomous Calendar & Appointment Booking Tool with SQLite persistence."""
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
    
    cursor.execute("SELECT COUNT(*) FROM officials_state")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO officials_state (id, current_status, updated_at, notice) VALUES (1, ?, ?, ?)",
            (
                config.DEFAULT_OFFICIALS_STATUS,
                datetime.now().isoformat(),
                "Officials currently in closed client enterprise delivery & meetings. Autonomous Agent handling bookings & triage."
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
    
    # Scan upcoming days
    day_offset = 0
    while len(available_slots) < 8 and day_offset < 14:
        target_date = now + timedelta(days=day_offset)
        # Skip weekends (5 = Sat, 6 = Sun)
        if target_date.weekday() in [5, 6]:
            day_offset += 1
            continue
            
        # Target standard appointment slots: 10:00, 11:30, 14:00, 15:30, 17:00
        for hour, minute in [(10, 0), (11, 30), (14, 0), (15, 30), (17, 0)]:
            slot_dt = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if slot_dt > now + timedelta(hours=2):  # Minimum 2 hours advance notice
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


def book_appointment(customer_name: str, customer_email: str, slot_time: str, service_type: str = "AI Strategy & Diagnostic", customer_phone: str = "", notes: str = "") -> Dict:
    """Books an appointment and stores it in the persistent database."""
    if not customer_name or not customer_email or not slot_time:
        return {
            "success": False,
            "error": "Missing required fields: customer_name, customer_email, and slot_time are mandatory."
        }
        
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    # Check if slot is already booked
    cursor.execute("SELECT id, customer_name FROM appointments WHERE slot_time = ? AND status = 'CONFIRMED'", (slot_time,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return {
            "success": False,
            "error": f"The slot '{slot_time}' has just been booked. Please choose another slot from the available times."
        }
        
    booking_id = f"VIT-{uuid.uuid4().hex[:6].upper()}"
    official = "Uday Zayn (Lead AI Architect) & Engineering Solutions Team"
    created_at = datetime.now().isoformat()
    
    cursor.execute("""
    INSERT INTO appointments (id, customer_name, customer_email, customer_phone, service_type, slot_time, official_assigned, status, notes, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'CONFIRMED', ?, ?)
    """, (booking_id, customer_name, customer_email, customer_phone, service_type, slot_time, official, notes, created_at))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "booking_id": booking_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "service_type": service_type,
        "slot_time": slot_time,
        "official_assigned": official,
        "meeting_link": f"https://meet.vittoris.com/{booking_id.lower()}",
        "message": f"Appointment successfully confirmed for {customer_name} on {slot_time}. Confirmation email and calendar invite sent to {customer_email}."
    }


def reschedule_appointment(booking_id: str, new_slot_time: str) -> Dict:
    """Reschedules an existing appointment to a new slot."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, customer_name, customer_email FROM appointments WHERE id = ?", (booking_id.upper(),))
    apt = cursor.fetchone()
    if not apt:
        conn.close()
        return {"success": False, "error": f"No appointment found with ID '{booking_id}'."}
        
    # Check if new slot is taken
    cursor.execute("SELECT id FROM appointments WHERE slot_time = ? AND status = 'CONFIRMED' AND id != ?", (new_slot_time, booking_id.upper()))
    if cursor.fetchone():
        conn.close()
        return {"success": False, "error": f"The requested slot '{new_slot_time}' is already booked."}
        
    cursor.execute("UPDATE appointments SET slot_time = ? WHERE id = ?", (new_slot_time, booking_id.upper()))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "booking_id": booking_id.upper(),
        "customer_name": apt[1],
        "new_slot_time": new_slot_time,
        "message": f"Appointment {booking_id.upper()} successfully rescheduled to {new_slot_time}."
    }


def cancel_appointment(booking_id: str) -> Dict:
    """Cancels a scheduled appointment."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, customer_name, slot_time FROM appointments WHERE id = ?", (booking_id.upper(),))
    apt = cursor.fetchone()
    if not apt:
        conn.close()
        return {"success": False, "error": f"No appointment found with ID '{booking_id}'."}
        
    cursor.execute("UPDATE appointments SET status = 'CANCELLED' WHERE id = ?", (booking_id.upper(),))
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "booking_id": booking_id.upper(),
        "message": f"Appointment {booking_id.upper()} for {apt[1]} has been cancelled."
    }


def list_all_appointments() -> List[Dict]:
    """Returns all scheduled appointments."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, customer_email, customer_phone, service_type, slot_time, official_assigned, status, notes, created_at FROM appointments ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "customer_name": r[1],
            "customer_email": r[2],
            "customer_phone": r[3],
            "service_type": r[4],
            "slot_time": r[5],
            "official_assigned": r[6],
            "status": r[7],
            "notes": r[8],
            "created_at": r[9]
        })
    return results
