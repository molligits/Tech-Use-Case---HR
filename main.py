"""
Orange Customer Support API
────────────────────────────
HappyRobot voice agent demo — all endpoints in one file.

Endpoints:
  POST /lookup          → verify customer, return account + upgrade eligibility
  POST /support-action  → run troubleshooting fix, return resolved true/false
  POST /slots           → return available technician appointment slots
  POST /book            → confirm appointment booking
  POST /close-call      → post-call CRM update and ticket creation

Deploy: push to GitHub, Railway auto-deploys.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="Orange Customer Support API",
    description="Demo endpoints for HappyRobot voice agent integration",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. LOOKUP — verify customer identity and return account details
# ═══════════════════════════════════════════════════════════════════════════════

class LookupRequest(BaseModel):
    customer_full_name: str
    account_or_phone: str
    postcode: str


@app.post("/lookup")
async def lookup_customer(req: LookupRequest):
    return {
        "verified": True,
        "account_id": "ACC-48291",
        "current_plan": "Orange Fibre Standard",
        "current_speed": "300 Mbps",
        "monthly_cost": 29.99,
        "upgrade_eligible": True,
        "upgrade_offer": "Orange Fibre Premium",
        "upgrade_speed": "2 Gbps",
        "upgrade_price_delta": 8.00,
        "upgrade_includes": "Latest Wi-Fi 6 router, up to 2 Gbps download, priority support",
        "open_tickets": 0,
        "message": "Customer verified. Account found.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SUPPORT ACTION — run troubleshooting fix with random outcome
# ═══════════════════════════════════════════════════════════════════════════════

# Resolution probabilities — happy path most likely on first fix
RESOLUTION_ODDS = {
    "remote_refresh": 0.70,
    "wan_refresh": 0.50,
    "router_reprovision": 0.30,
}

ACTION_MESSAGES = {
    "remote_refresh": {
        True: "Remote refresh completed successfully. Connection restored.",
        False: "Remote refresh completed. Connection issue persists.",
    },
    "wan_refresh": {
        True: "WAN refresh completed successfully. Service restored.",
        False: "WAN refresh completed. The issue may still persist.",
    },
    "router_reprovision": {
        True: "Router reprovision completed successfully. Connection restored.",
        False: "Router reprovision completed. Additional technical support is required.",
    },
}

VALID_ACTIONS = list(RESOLUTION_ODDS.keys())


class SupportActionRequest(BaseModel):
    account_id: str
    action: str


@app.post("/support-action")
async def support_action(req: SupportActionRequest):
    if req.action not in VALID_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {VALID_ACTIONS}",
        )

    resolved = random.random() < RESOLUTION_ODDS[req.action]

    return {
        "success": True,
        "action": req.action,
        "resolved": resolved,
        "message": ACTION_MESSAGES[req.action][resolved],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SLOTS — return available technician appointment slots
# ═══════════════════════════════════════════════════════════════════════════════

class SlotsRequest(BaseModel):
    account_id: str


@app.post("/slots")
async def check_slots(req: SlotsRequest):
    # Generate 3 realistic slots starting tomorrow
    base = datetime.now() + timedelta(days=1)
    slots = []

    for i in range(3):
        slot_date = base + timedelta(days=i)
        # Skip weekends
        while slot_date.weekday() >= 5:
            slot_date += timedelta(days=1)
        hour = [9, 14, 10][i]  # morning, afternoon, morning
        slot_time = slot_date.replace(hour=hour, minute=0, second=0)
        end_hour = hour + 2
        am_pm = "AM" if hour < 12 else "PM"
        end_am_pm = "AM" if end_hour < 12 else "PM"
        slots.append({
            "slot_id": f"SLOT-{i+1}",
            "datetime": slot_time.strftime(f"%A %d %B, {hour}:{0:02d} {am_pm}"),
            "window": f"{hour} {am_pm} to {end_hour} {end_am_pm}",
        })

    return {
        "available": True,
        "slots": slots,
        "message": f"Found {len(slots)} available appointment slots.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. BOOK — confirm appointment booking
# ═══════════════════════════════════════════════════════════════════════════════

class BookRequest(BaseModel):
    account_id: str
    selected_slot: str


@app.post("/book")
async def book_appointment(req: BookRequest):
    # Generate a confirmation number
    conf_number = f"ORG-{random.randint(100000, 999999)}"

    return {
        "booked": True,
        "confirmation_number": conf_number,
        "slot": req.selected_slot,
        "service": "Orange Fibre Premium Upgrade",
        "includes": "New router, fibre line upgrade, technician installation",
        "message": f"Appointment confirmed. Reference number: {conf_number}.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CLOSE CALL — post-call CRM update and ticket creation
# ═══════════════════════════════════════════════════════════════════════════════

class CloseCallRequest(BaseModel):
    account_id: str = ""
    issue_reported: str = ""
    issue_resolved: str = ""
    resolution_method: str = ""
    upgrade_offered: str = ""
    upgrade_accepted: str = ""
    appointment_confirmation: str = ""
    call_summary: str = ""


@app.post("/close-call")
async def close_call(req: CloseCallRequest):
    today = datetime.now().strftime("%Y%m%d")
    ticket_id = f"TKT-{today}-{req.account_id.replace('ACC-', '')}" if req.account_id else f"TKT-{today}-00000"

    fields_updated = ["support_history"]
    next_action = "No follow-up required."

    is_resolved = req.issue_resolved.lower() == "true"
    is_upgrade = req.upgrade_accepted.lower() == "true"

    if is_resolved:
        fields_updated.append("issue_status:resolved")
    else:
        fields_updated.append("issue_status:escalated")
        next_action = "Escalation ticket created. Tier 2 team notified."

    if is_upgrade:
        fields_updated.append("plan_status:upgrade_pending")
        fields_updated.append("appointment_scheduled")
        next_action = f"Technician dispatch confirmed. Ref: {req.appointment_confirmation}."
    elif not is_upgrade and is_resolved:
        fields_updated.append("upgrade_pipeline:open")

    return {
        "logged": True,
        "ticket_id": ticket_id,
        "crm_updated": True,
        "fields_updated": fields_updated,
        "next_action": next_action,
        "message": f"Call record saved. Account {req.account_id} updated.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "endpoints": ["/lookup", "/support-action", "/slots", "/book", "/close-call"],
    }
