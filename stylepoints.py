"""
StylePoints service

This module supports TWO modes controlled by env POINTS_MODE:

1) offline  (default)  -> use in-memory REWARDS ledger (no blockchain)
2) onchain             -> interact with deployed ERC20 on Flare via web3

Endpoints are kept stable so your frontend doesn't need to change:
- POST  /stylepoints/mint   { to|user, amount }
- GET   /stylepoints/balance/{addr}   # 'addr' can be an email/user-id in offline mode
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os, json

router = APIRouter()

# --------- Mode switch ----------
POINTS_MODE = os.getenv("POINTS_MODE", "offline").lower()

# ----- OFFLINE MODE (default) -----
from db import REWARDS  # in-memory ledger

class MintReq(BaseModel):
    # Keep both names for compatibility with previous on-chain shape
    to: str | None = None      # user id or EVM address (unused in offline)
    user: str | None = None    # preferred for offline
    amount: float              # human readable amount; will be rounded in offline

@router.post("/mint")
def mint(req: MintReq):
    """
    If POINTS_MODE=offline:
        - interpret 'user' (or fallback to 'to') as the unique user id (e.g., email)
        - add integer(points) to REWARDS ledger
    If POINTS_MODE=onchain:
        - call ERC20.issue(to, amount * 10**decimals) using OWNER_PRIVATE_KEY
    """
    if POINTS_MODE == "offline":
        recipient = req.user or req.to
        if not recipient:
            raise HTTPException(400, "Provide 'user' (email/uid).")
        if req.amount <= 0:
            raise HTTPException(400, "amount must be > 0")
        add = int(round(req.amount))
        REWARDS[recipient] = REWARDS.get(recipient, 0) + add
        return {"mode": "offline", "user": recipient, "amount_added": add, "balance": REWARDS[recipient]}

    # --------- ONCHAIN MODE ----------
    try:
        from web3 import Web3  # lazy import so offline mode has no web3 dependency
    except Exception as e:
        raise HTTPException(500, f"web3 not available: {e}")

    FLARE_RPC = os.getenv("FLARE_RPC", "https://coston2-api.flare.network/ext/C/rpc")
    STYLEPOINTS_ADDRESS = os.getenv("STYLEPOINTS_ADDRESS")
    OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")

    if not (STYLEPOINTS_ADDRESS and OWNER_PRIVATE_KEY):
        raise HTTPException(500, "STYLEPOINTS_ADDRESS / OWNER_PRIVATE_KEY not set for onchain mode")

    w3 = Web3(Web3.HTTPProvider(FLARE_RPC))
    owner = w3.eth.account.from_key(OWNER_PRIVATE_KEY)

    STYLEPOINTS_ABI = json.loads("""
    [
      {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
      {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
      {"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"amount","type":"uint256"}],"name":"issue","outputs":[],"stateMutability":"nonpayable","type":"function"}
    ]
    """)

    recipient = (req.to or "").strip()
    if not recipient:
        raise HTTPException(400, "Provide 'to' (EVM address) for onchain mode")
    try:
        c = w3.eth.contract(address=Web3.to_checksum_address(STYLEPOINTS_ADDRESS), abi=STYLEPOINTS_ABI)
        decimals = c.functions.decimals().call()
        amt = int(req.amount * (10 ** decimals))
        nonce = w3.eth.get_transaction_count(owner.address)
        tx = c.functions.issue(Web3.to_checksum_address(recipient), amt).build_transaction({
            "from": owner.address,
            "nonce": nonce,
            "gas": 200000,
            "maxFeePerGas": w3.to_wei("25", "gwei"),
            "maxPriorityFeePerGas": w3.to_wei("2", "gwei"),
            "chainId": w3.eth.chain_id
        })
        signed = w3.eth.account.sign_transaction(tx, private_key=OWNER_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        return {"mode": "onchain", "tx_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(500, f"onchain mint failed: {e}")

@router.get("/balance/{addr}")
def balance(addr: str):
    """
    If POINTS_MODE=offline:
        - 'addr' is treated as user id (email), returns integer balance from REWARDS.
    If POINTS_MODE=onchain:
        - 'addr' must be an EVM address, returns ERC20 balance / 10**decimals.
    """
    if POINTS_MODE == "offline":
        return {"mode": "offline", "user": addr, "balance": REWARDS.get(addr, 0)}

    # --------- ONCHAIN MODE ----------
    try:
        from web3 import Web3
    except Exception as e:
        raise HTTPException(500, f"web3 not available: {e}")

    FLARE_RPC = os.getenv("FLARE_RPC", "https://coston2-api.flare.network/ext/C/rpc")
    STYLEPOINTS_ADDRESS = os.getenv("STYLEPOINTS_ADDRESS")

    if not STYLEPOINTS_ADDRESS:
        raise HTTPException(500, "STYLEPOINTS_ADDRESS not set for onchain mode")

    try:
        w3 = Web3(Web3.HTTPProvider(FLARE_RPC))
        STYLEPOINTS_ABI = json.loads("""
        [
          {"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
          {"constant":true,"inputs":[{"name":"account","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"}
        ]
        """)
        c = w3.eth.contract(address=Web3.to_checksum_address(STYLEPOINTS_ADDRESS), abi=STYLEPOINTS_ABI)
        decimals = c.functions.decimals().call()
        raw = c.functions.balanceOf(Web3.to_checksum_address(addr)).call()
        return {"mode": "onchain", "address": addr, "balance": raw / (10 ** decimals), "raw": str(raw), "decimals": decimals}
    except Exception as e:
        raise HTTPException(500, f"onchain balance failed: {e}")