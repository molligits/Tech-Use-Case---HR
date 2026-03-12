"""
Orange Customer Account Lookup API
──────────────────────────────────
Single-file FastAPI endpoint for HappyRobot voice agent demo.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


# ── Request model ─────────────────────────────────────────────────────────────

class LookupRequest(BaseModel):
    customer_full_name: str
    account_or_phone: str
    postcode: str


# ── Endpoint ──────────────────────────────────────────────────────────────────

@app.post("/lookup")
async def lookup_customer(req: LookupRequest):
    return {
        "verified": True,
        "account_id": "ACC-48291",
        "current_plan": "Orange Fibre Standard",
        "monthly_cost": 29.99,
        "upgrade_eligible": True,
        "upgrade_offer": "Orange Fibre Premium Upgrade",
        "upgrade_price_delta": 8.00,
        "open_tickets": 0,
        "message": "Customer verified. Account found.",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
