from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Tuple
import os

try:
    from db import NFTS, USERS_RISK
except Exception:
    # Fallback to avoid import errors during partial edits; these will be provided by db.py
    NFTS = {}
    USERS_RISK = {}

router = APIRouter()

# -------------------- FDC integration (mockable) --------------------
# Turn on to require FDC proofs for certain user events. In demo, set USE_FDC=1 to enforce.
USE_FDC = os.getenv("USE_FDC", "0") == "1"

# Map user event types -> the kind of attestation we expect from FDC
FDC_REQUIRED_FOR_EVENT: Dict[str, str] = {
    # delivery related
    "false_non_delivery": "delivery_confirmed",   # user claims not delivered; FDC says delivered
    "on_time_delivery_ack": "delivery_confirmed",
    # return / cleaning related
    "good_return": "return_scanned",
    "dirty_return": "cleaning_scanned",
}

def _fdc_verify(event_type: str, meta: Dict[str, Any] | None) -> bool:
    """Verify evidence with FDC (demo-friendly).
    Real integration: call Flare Data Connector off-chain API / smart contract to verify proof.
    For demo, when USE_FDC=1 we require `meta` contains {"fdc_proof": "ok"} OR {"fdc": {"verified": true}}.
    When USE_FDC=0 we accept as verified to keep flows simple.
    """
    if not USE_FDC:
        return True
    if not meta:
        return False
    # two simple ways to pass in the demo
    if meta.get("fdc_proof") == "ok":
        return True
    fdc = meta.get("fdc")
    if isinstance(fdc, dict) and fdc.get("verified") is True:
        return True
    return False

class RiskGrade(str, Enum):
    AAA = "AAA"; AA = "AA"; A = "A"; BBB = "BBB"; BB = "BB"; B = "B"; CCC = "CCC"; CC = "CC"; C = "C"; D = "D"

# -------------------- Utility: score -> grade --------------------
def _grade_from_score(score: float) -> 'RiskGrade':
    if score >= 90: return RiskGrade.AAA
    if score >= 80: return RiskGrade.AA
    if score >= 70: return RiskGrade.A
    if score >= 60: return RiskGrade.BBB
    if score >= 55: return RiskGrade.BB
    if score >= 50: return RiskGrade.B
    if score >= 45: return RiskGrade.CCC
    if score >= 40: return RiskGrade.CC
    if score >= 35: return RiskGrade.C
    return RiskGrade.D

# -------------------- NFT-level risk --------------------
def compute_risk_score(nft: dict) -> Tuple[float, RiskGrade]:
    wear = nft.get("wear_level", 0)
    cleans_30d = nft.get("cleans_30d", 0)
    late = nft.get("late_deliveries", 0)
    returns = nft.get("returns", 0)
    # Base heuristic (item condition + logistics issues affecting item risk)
    score = 100 - 10 * wear - 5 * cleans_30d - 3 * late - 4 * returns
    score = max(0, min(100, score))
    return float(score), _grade_from_score(score)

class NftRegisterReq(BaseModel):
    token_id: str
    title: str
    wear_level: int = 0

@router.post("/nft/register")
def nft_register(req: NftRegisterReq):
    NFTS[req.token_id] = {
        "token_id": req.token_id,
        "title": req.title,
        "wear_level": req.wear_level,
        "cleans_30d": 0,
        "late_deliveries": 0,
        "returns": 0,
        "events": []
    }
    s, g = compute_risk_score(NFTS[req.token_id])
    return {"token_id": req.token_id, "risk_score": s, "risk_grade": g}

class NftEventReq(BaseModel):
    token_id: str
    event_type: str   # rented/returned/cleaned/delivered/delivery_late/wear_plus/altered/reviewed/dirty_return
    meta: Dict[str, Any] | None = None

# Internal helper (reusable from other modules, e.g., rental.py)
def register_nft_event(token_id: str, event_type: str, meta: Dict[str, Any] | None = None) -> Tuple[float, RiskGrade, int]:
    nft = NFTS.get(token_id)
    if not nft:
        raise HTTPException(404, "NFT not found")
    nft.setdefault("events", []).append({"ts": datetime.utcnow().isoformat(), "type": event_type, "meta": meta})

    if event_type == "cleaned":
        nft["cleans_30d"] = int(nft.get("cleans_30d", 0)) + 1
    if event_type == "delivery_late":
        nft["late_deliveries"] = int(nft.get("late_deliveries", 0)) + 1
    if event_type == "returned":
        nft["returns"] = int(nft.get("returns", 0)) + 1
    if event_type == "wear_plus":
        nft["wear_level"] = min(5, int(nft.get("wear_level", 0)) + 1)
    if event_type == "dirty_return":
        # Dirty return negatively impacts the item's risk too
        nft["returns"] = int(nft.get("returns", 0)) + 1
        nft["wear_level"] = min(5, int(nft.get("wear_level", 0)) + 1)

    s, g = compute_risk_score(nft)
    return s, g, len(nft["events"])

@router.post("/nft/event")
def nft_event(req: NftEventReq):
    s, g, cnt = register_nft_event(req.token_id, req.event_type, req.meta)
    return {"token_id": req.token_id, "risk_score": s, "risk_grade": g, "events": cnt}

@router.get("/score/{token_id}")
def risk_score(token_id: str):
    nft = NFTS.get(token_id)
    if not nft:
        raise HTTPException(404, "NFT not found")
    s, g = compute_risk_score(nft)
    return {"token_id": token_id, "risk_score": s, "risk_grade": g}

# -------------------- USER-level risk (focus on honesty & reliability) --------------------
# Event weights (negative values improve score, positive values penalize)
USER_EVENT_WEIGHTS: Dict[str, int] = {
    # bad behavior
    "not_returned": 20,
    "late_return": 8,
    "dirty_return": 6,
    "false_non_delivery": 12,  # claimed not delivered but FDC says delivered
    # good behavior
    "on_time_delivery_ack": -1,
    "good_return": -2,
}

def _ensure_user(user_id: str) -> dict:
    if user_id not in USERS_RISK:
        USERS_RISK[user_id] = {"user_id": user_id, "score": 85.0, "events": []}  # start slightly below AAA
    return USERS_RISK[user_id]

def compute_user_risk(user: dict) -> Tuple[float, RiskGrade]:
    # Base score is whatever currently stored
    score = float(user.get("score", 85.0))
    # Clamp & grade
    score = max(0.0, min(100.0, score))
    return score, _grade_from_score(score)

class UserEventReq(BaseModel):
    user_id: str       # e.g., email
    event_type: str    # not_returned/late_return/dirty_return/false_non_delivery/on_time_delivery_ack/good_return (some require FDC)
    meta: Dict[str, Any] | None = None

# Internal helper (callable from rental.py)
def register_user_event(user_id: str, event_type: str, meta: Dict[str, Any] | None = None) -> Tuple[float, RiskGrade, int]:
    user = _ensure_user(user_id)
    user.setdefault("events", []).append({"ts": datetime.utcnow().isoformat(), "type": event_type, "meta": meta})
    # If this user event requires an FDC attestation, verify it first
    if event_type in FDC_REQUIRED_FOR_EVENT:
        if not _fdc_verify(event_type, meta):
            raise HTTPException(400, f"FDC verification failed for event '{event_type}'. Provide meta.fdc_proof='ok' or meta.fdc.verified=true in demo, or integrate real FDC proof.")
    delta = USER_EVENT_WEIGHTS.get(event_type, 0)
    # Higher score = better; penalties decrease score
    user["score"] = float(user.get("score", 85.0)) - float(max(0, delta)) + float(min(0, delta) * -1)
    # The above line treats positive weights as penalties (score down), negative weights as rewards (score up)
    # Alternatively, simpler: user["score"] -= delta; but we keep explicit for clarity
    if event_type in ("dirty_return",):
        # Optional: stronger clamp after dirty return
        user["score"] = max(0.0, user["score"] - 0.0)
    score, grade = compute_user_risk(user)
    return score, grade, len(user["events"])

@router.post("/user/event")
def user_event(req: UserEventReq):
    score, grade, cnt = register_user_event(req.user_id, req.event_type, req.meta)
    return {"user_id": req.user_id, "user_score": score, "user_grade": grade, "events": cnt}

@router.get("/user/score/{user_id}")
def user_score(user_id: str):
    user = _ensure_user(user_id)
    score, grade = compute_user_risk(user)
    return {"user_id": user_id, "user_score": score, "user_grade": grade, "events": len(user.get("events", []))}

@router.get("/fdc/status")
def fdc_status():
    return {
        "use_fdc": USE_FDC,
        "required_events": FDC_REQUIRED_FOR_EVENT,
        "hint": "When USE_FDC=1, pass meta: {\"fdc_proof\": \"ok\"} in demo to mark attested."
    }