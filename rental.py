from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from db import BONDS, RENTAL_HISTORY, REWARDS
try:
    from db import QUOTES  # optional in-memory store for quotes
except Exception:
    QUOTES = {}

router = APIRouter()

class BondQuoteReq(BaseModel):
    base_price: float
    bundle_rentals: int = 3
    holiday_multiplier: float = 1.0
    risk_spread_bps: int = 0     # 250 => 2.5%

class BondPurchaseReq(BondQuoteReq):
    user: str
    token_id: str | None = None
    quote_id: str | None = None  # optional: purchase by a previously returned quote_id
def _save_quote(req: BondQuoteReq, qdata: dict) -> dict:
    """
    Persist a short-lived quote so frontend can reference it by `quote_id` in /bonds/purchase.
    """
    quote_id = f"QUOTE-{len(QUOTES)+1:06d}"
    rec = {
        "quote_id": quote_id,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat(),
        "params": req.model_dump(),
        "pricing": qdata
    }
    QUOTES[quote_id] = rec
    return rec

def _quote(q: BondQuoteReq) -> dict:
    rentals_value = q.base_price * q.bundle_rentals * q.holiday_multiplier
    y = q.risk_spread_bps / 10000.0
    T = 0.25  # quarter (in years)
    price = rentals_value / ((1 + y) ** T)
    return {
        "fair_value": round(price, 2),
        "rentals_value": round(rentals_value, 2),
        "discount": round(rentals_value - price, 2),
        "implied_yield": y,
        "tenor_years": T
    }

@router.post("/bonds/quote")
def bonds_quote(req: BondQuoteReq):
    q = _quote(req)
    saved = _save_quote(req, q)
    # Merge the pricing fields with quote metadata for the response
    return {"quote_id": saved["quote_id"], **q, "expires_at": saved["expires_at"]}

@router.post("/bonds/purchase")
def bonds_purchase(req: BondPurchaseReq):
    # If client provided a valid quote_id, use that pricing and parameters
    q_used = None
    if req.quote_id:
        saved = QUOTES.get(req.quote_id)
        if not saved:
            raise HTTPException(404, "quote not found")
        # Check expiry
        if datetime.utcnow() > datetime.fromisoformat(saved["expires_at"]):
            raise HTTPException(400, "quote expired")
        # Use the exact quote and original parameters
        q_used = saved["pricing"]
        saved_params = saved["params"]
        bundle_rentals = int(saved_params.get("bundle_rentals", req.bundle_rentals))
    else:
        # Fall back to calculating from current request
        q_used = _quote(req)
        bundle_rentals = req.bundle_rentals

    bond_id = f"BOND-{len(BONDS)+1:06d}"
    BONDS[bond_id] = {
        "bond_id": bond_id,
        "user": req.user,
        "bundle_left": bundle_rentals,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat(),
        "price_paid": q_used["fair_value"],
        "params": req.model_dump(),
        "redemptions": []
    }
    return {"bond_id": bond_id, **q_used}

class RedeemReq(BaseModel):
    bond_id: str
    token_id: str
    location: str | None = None

@router.post("/bonds/redeem")
def bonds_redeem(req: RedeemReq):
    b = BONDS.get(req.bond_id)
    if not b: raise HTTPException(404, "bond not found")
    if b["bundle_left"] <= 0: raise HTTPException(400, "no rentals left")
    if datetime.utcnow() > datetime.fromisoformat(b["expires_at"]): raise HTTPException(400, "bond expired")

    b["bundle_left"] -= 1
    rec = {"ts": datetime.utcnow().isoformat(), "token_id": req.token_id, "location": req.location}
    b["redemptions"].append(rec)
    # issue +10 points on each redemption
    REWARDS[b["user"]] = REWARDS.get(b["user"], 0) + 10
    RENTAL_HISTORY.append({"type": "redeem", "user": b["user"], **rec, "bond_id": req.bond_id})
    return {"ok": True, "bundle_left": b["bundle_left"], "reward_points": REWARDS[b["user"]]}

@router.get("/bonds/{bond_id}")
def bond_detail(bond_id: str):
    b = BONDS.get(bond_id)
    if not b:
        raise HTTPException(404, "bond not found")
    return b

@router.get("/history")
def rental_history():
    return {"events": RENTAL_HISTORY}