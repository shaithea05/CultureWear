from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import REWARDS

router = APIRouter()

class IssueReq(BaseModel):
    user: str
    amount: int

class SpendReq(BaseModel):
    user: str
    amount: int

@router.get("/balance/{user}")
def balance(user: str):
    return {"user": user, "balance": REWARDS.get(user, 0)}

@router.post("/issue")
def issue(req: IssueReq):
    if req.amount <= 0:
        raise HTTPException(400, "amount must be > 0")
    REWARDS[req.user] = REWARDS.get(req.user, 0) + req.amount
    return {"user": req.user, "balance": REWARDS[req.user]}

@router.post("/spend")
def spend(req: SpendReq):
    bal = REWARDS.get(req.user, 0)
    if req.amount <= 0:
        raise HTTPException(400, "amount must be > 0")
    if bal < req.amount:
        raise HTTPException(400, "insufficient points")
    REWARDS[req.user] = bal - req.amount
    return {"user": req.user, "balance": REWARDS[req.user]}