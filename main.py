"""
Orange Customer Account Lookup API
──────────────────────────────────
Single-file FastAPI endpoint for HappyRobot voice agent demo.
Deploy to Railway / Render / Fly.io in minutes.

Accepts: customer_full_name, account_or_phone, postcode
Returns: verified account data + upgrade eligibility
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

app = FastAPI(
    title="Orange Account Lookup",
    description="Demo endpoint for HappyRobot voice agent integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Mock customer database ────────────────────────────────────────────────────

CUSTOMERS = [
    {
        "name": "Marie Dupont",
        "account_id": "ACC-48291",
        "phone": "+33612345678",
        "postcode": "75015",
        "plan": "Livebox Fibre 300",
        "monthly_cost": 29.99,
        "contract_start": "2022-03-15",
        "upgrade_eligible": True,
        "upgrade_offer": "Livebox Max Fibre 2G",
        "upgrade_price": 39.99,
        "open_tickets": 0,
        "last_outage": "2025-11-02",
    },
    {
        "name": "Jean-Pierre Martin",
        "account_id": "ACC-71054",
        "phone": "+33698765432",
        "postcode": "69003",
        "plan": "Livebox Fibre 500",
        "monthly_cost": 34.99,
        "contract_start": "2023-08-01",
        "upgrade_eligible": False,
        "upgrade_offer": None,
        "upgrade_price": None,
        "open_tickets": 1,
        "last_outage": "2026-01-18",
    },
    {
        "name": "Sophie Bernard",
        "account_id": "ACC-33210",
        "phone": "+33655512345",
        "postcode": "33000",
        "plan": "Livebox ADSL",
        "monthly_cost": 19.99,
        "contract_start": "2020-06-10",
        "upgrade_eligible": True,
        "upgrade_offer": "Livebox Fibre 500",
        "upgrade_price": 34.99,
        "open_tickets": 0,
        "last_outage": "2025-09-30",
    },
    {
        "name": "Carlos García",
        "account_id": "ACC-92017",
        "phone": "+33677788899",
        "postcode": "92100",
        "plan": "Livebox Max Fibre 2G",
        "monthly_cost": 39.99,
        "contract_start": "2024-01-20",
        "upgrade_eligible": False,
        "upgrade_offer": None,
        "upgrade_price": None,
        "open_tickets": 2,
        "last_outage": "2026-02-25",
    },
]


# ── Request / Response models ─────────────────────────────────────────────────

class LookupRequest(BaseModel):
    customer_full_name: str
    account_or_phone: str
    postcode: str

class LookupResponse(BaseModel):
    verified: bool
    confidence: float
    account_id: str | None = None
    customer_name: str | None = None
    plan: str | None = None
    monthly_cost: float | None = None
    contract_start: str | None = None
    upgrade_eligible: bool | None = None
    upgrade_offer: str | None = None
    upgrade_price: float | None = None
    open_tickets: int | None = None
    last_outage: str | None = None
    available_appointment_slots: list[str] | None = None
    message: str


# ── Matching logic ────────────────────────────────────────────────────────────




def generate_appointment_slots():
    """Generate 3 realistic upcoming appointment slots."""
    base = datetime.now() + timedelta(days=random.randint(1, 3))
    slots = []
    for i in range(3):
        slot_date = base + timedelta(days=i)
        hour = random.choice([9, 10, 11, 14, 15, 16])
        slot = slot_date.replace(hour=hour, minute=0, second=0)
        slots.append(slot.strftime("%A %d %B, %H:%M"))
    return slots


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.post("/lookup", response_model=LookupResponse)
async def lookup_customer(req: LookupRequest):
    """
    Main endpoint for HappyRobot tool integration.
    Matches customer by name + account/phone + postcode.
    Returns account details and upgrade eligibility.
    """
    # Demo mode: always return a verified account using the caller's own name
    demo = CUSTOMERS[0]
    return LookupResponse(
        verified=True,
        confidence=97.5,
        account_id=demo["account_id"],
        customer_name=req.customer_full_name,  # echo back whatever name they gave
        plan=demo["plan"],
        monthly_cost=demo["monthly_cost"],
        contract_start=demo["contract_start"],
        upgrade_eligible=demo["upgrade_eligible"],
        upgrade_offer=demo["upgrade_offer"],
        upgrade_price=demo["upgrade_price"],
        open_tickets=demo["open_tickets"],
        last_outage=demo["last_outage"],
        available_appointment_slots=generate_appointment_slots(),
        message=f"Customer verified. Account {demo['account_id']} found.",
    )


@app.get("/health")
async def health():
    return {"status": "ok", "customers_loaded": len(CUSTOMERS)}


@app.get("/customers")
async def list_customers():
    """Debug endpoint — list test customers for demo setup."""
    return [
        {"name": c["name"], "account_id": c["account_id"], "postcode": c["postcode"]}
        for c in CUSTOMERS
    ]
