import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.models.requests.account_info import AccountInfo
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops, drops_to_xrp
from decimal import Decimal

router = APIRouter()

XRPL_RPC = os.getenv("XRPL_RPC", "https://s.altnet.rippletest.net:51234")
XRPL_SEED = os.getenv("XRPL_SEED")
if not XRPL_SEED:
    raise RuntimeError("XRPL_SEED not set in .env")

client = JsonRpcClient(XRPL_RPC)
wallet = Wallet.from_seed(XRPL_SEED)

class PayReq(BaseModel):
    to: str
    amountXRP: float

@router.post("/pay")
def pay(req: PayReq):
    if req.amountXRP <= 0:
        raise HTTPException(400, "amountXRP must be > 0")
    try:
        tx = Payment(
            account=wallet.classic_address,
            destination=req.to,
            amount=xrp_to_drops(Decimal(str(req.amountXRP))),
        )
        r = submit_and_wait(tx, client, wallet)
        return {"hash": r.result["hash"], "validated": r.is_successful()}
    except Exception as e:
        return {"hash": "DEMO123456", "validated": False, "note": f"Mock fallback, error: {e}"}

@router.get("/balance/{account}")
def balance(account: str):
    try:
        resp = client.request(AccountInfo(account=account, ledger_index="validated", strict=True))
        bal_drops = resp.result["account_data"]["Balance"]
        return {"account": account, "balance": float(drops_to_xrp(bal_drops))}
    except Exception as e:
        msg = str(e)
        if "actNotFound" in msg or "account_data" in msg:
            # XRPL returns actNotFound for non-existent accounts on this network
            raise HTTPException(404, "Account not found on XRPL (check the faucet/network).")
        raise HTTPException(500, f"XRPL balance error: {e}")