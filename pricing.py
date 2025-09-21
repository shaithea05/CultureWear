import os, time
from fastapi import APIRouter
from pydantic import BaseModel
from db import NFTS
from risk import compute_risk_score, RiskGrade

router = APIRouter()

USE_MOCK_FTSO = os.getenv("USE_MOCK_FTSO", "1") == "1"
MOCK_FEEDS = {
    # feed_id: (value, decimals)
    "0x01464c522f55534400000000000000000000000000": (25000, 6)  # 0.025000
}

def _get_fx(feed_id: str | None) -> tuple[float, str]:
    if not feed_id:
        return 1.0, "none"
    if USE_MOCK_FTSO:
        v, d = MOCK_FEEDS.get(feed_id, (1_000_000, 6))
        return float(v) / (10**d), "mock"
    # TODO: real FTSO query
    return 1.0, "fallback=1.0"

class PriceReq(BaseModel):
    token_id: str
    base_price: float
    region: str = "US"
    fx_feed_id: str | None = None

@router.post("/quote")
def quote(req: PriceReq):
    price = req.base_price
    detail = {"base": price}

    fx, src = _get_fx(req.fx_feed_id)
    price *= fx
    detail["fx"] = fx
    detail["fx_source"] = src

    nft = NFTS.get(req.token_id)
    if nft:
        score, grade = compute_risk_score(nft)
        adj = 1.00
        if grade in [RiskGrade.BB, RiskGrade.B, RiskGrade.CCC, RiskGrade.CC, RiskGrade.C, RiskGrade.D]:
            adj = 1.10
        elif grade in [RiskGrade.AAA, RiskGrade.AA]:
            adj = 0.95
        price *= adj
        detail["risk_grade"] = grade
        detail["risk_mul"] = adj

    return {"token_id": req.token_id, "final_price": round(price, 2), "detail": detail, "ts": int(time.time())}