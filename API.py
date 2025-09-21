# import os
# from fastapi import FastAPI
# from xrpl.clients import JsonRpcClient
# from xrpl.models.transactions import Payment, NFTokenMint
# from xrpl.wallet import Wallet
# from xrpl.transaction import submit_and_wait
# from xrpl.utils import xrp_to_drops

# app = FastAPI()
# client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
# wallet = Wallet.from_seed(os.environ["XRPL_SEED"])

# @app.post("/xrpl/pay")
# def pay(to: str, amountXRP: float):
#     tx = Payment(account=wallet.classic_address, destination=to,
#                  amount=xrp_to_drops(str(amountXRP)))
#     r = submit_and_wait(tx, client, wallet)
#     return {"hash": r.result["hash"]}
import os
import json
from typing import Optional, Dict, Any

# 环境变量（.env 可选）
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ---------- XRPL ----------
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import Payment
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.utils import xrp_to_drops

# ---------- Flare / web3 ----------
from web3 import Web3

app = FastAPI(title="XRPL + Flare API", version="0.1.0")

# ==============================
# XRPL: 支付（Testnet）
# ==============================
XRPL_RPC = os.getenv("XRPL_RPC", "https://s.altnet.rippletest.net:51234")
xrpl_client = JsonRpcClient(XRPL_RPC)

XRPL_SEED = os.getenv("XRPL_SEED")
if not XRPL_SEED:
    raise RuntimeError("XRPL_SEED not set. Export it or put it in .env")

xrpl_wallet = Wallet.from_seed(XRPL_SEED)

@app.post("/xrpl/pay")
def xrpl_pay(to: str, amountXRP: float) -> Dict[str, Any]:
    if amountXRP <= 0:
        raise HTTPException(400, "amountXRP must be > 0")
    try:
        tx = Payment(
            account=xrpl_wallet.classic_address,
            destination=to,
            amount=xrp_to_drops(str(amountXRP)),
        )
        r = submit_and_wait(tx, xrpl_client, xrpl_wallet)
        return {"hash": r.result["hash"], "validated": r.is_successful()}
    except Exception as e:
        raise HTTPException(500, f"XRPL payment failed: {e}")

# ==============================
# Flare: FTSO v2 价格读取
# ==============================
FLARE_RPC = os.getenv("FLARE_RPC", "https://coston2-api.flare.network/ext/C/rpc")  # 默认 Coston2 testnet
w3 = Web3(Web3.HTTPProvider(FLARE_RPC))

# 官方示例里提供的 ContractRegistry 常量地址（适用于获取 FtsoV2 合约地址）
CONTRACT_REGISTRY_ADDR = os.getenv(
    "FLARE_CONTRACT_REGISTRY",
    "0xaD67FE66660Fb8dFE9d6b1b4240d8650e30F6019"
)

# 最小 ABI：只包含我们要用的函数
CONTRACT_REGISTRY_ABI = [
    { "inputs": [], "name": "getFtsoV2", "outputs": [{"internalType":"address","name":"","type":"address"}], "stateMutability": "view", "type": "function" },
    { "inputs": [], "name": "getTestFtsoV2", "outputs": [{"internalType":"address","name":"","type":"address"}], "stateMutability": "view", "type": "function" },
]

FTSOV2_MIN_ABI = [
    { "inputs": [{"internalType":"bytes21","name":"_feedId","type":"bytes21"}],
      "name":"getFeedById",
      "outputs":[{"internalType":"uint256","name":"_value","type":"uint256"},
                 {"internalType":"int8","name":"_decimals","type":"int8"},
                 {"internalType":"uint64","name":"_timestamp","type":"uint64"}],
      "stateMutability":"view","type":"function"
    },
    { "inputs": [{"internalType":"bytes21[]","name":"_feedIds","type":"bytes21[]"}],
      "name":"getFeedsById",
      "outputs":[{"internalType":"uint256[]","name":"_values","type":"uint256[]"},
                 {"internalType":"int8[]","name":"_decimals","type":"int8[]"},
                 {"internalType":"uint64","name":"_timestamp","type":"uint64"}],
      "stateMutability":"view","type":"function"
    }
]

def _get_contract_registry():
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_REGISTRY_ADDR),
        abi=CONTRACT_REGISTRY_ABI
    )

def _get_ftsoV2_address_for_env() -> str:
    """
    Coston2 测试网优先 getTestFtsoV2()，失败则回退 getFtsoV2()
    """
    reg = _get_contract_registry()
    try:
        addr = reg.functions.getTestFtsoV2().call()
        if int(addr, 16) != 0:
            return addr
    except Exception:
        pass
    return reg.functions.getFtsoV2().call()

def _get_ftsoV2_contract():
    addr = _get_ftsoV2_address_for_env()
    if int(addr, 16) == 0:
        raise RuntimeError("FtsoV2 address not found from ContractRegistry")
    return w3.eth.contract(address=Web3.to_checksum_address(addr), abi=FTSOV2_MIN_ABI)

@app.get("/flare/ftso/price/{feed_id}")
def ftso_price_by_feed_id(feed_id: str) -> Dict[str, Any]:
    """
    feed_id: 例如 FLR/USD 的 feedId = 0x01464c522f55534400000000000000000000000000
    返回: 原始整数 price、decimals、timestamp，以及 float_price
    """
    try:
        if not feed_id.startswith("0x") or len(feed_id) != 44:  # bytes21 => 21*2+2
            raise HTTPException(400, "feed_id must be 0x + 42 hex chars (bytes21)")
        c = _get_ftsoV2_contract()
        value, decimals, ts = c.functions.getFeedById(feed_id).call()
        return {
            "feed_id": feed_id,
            "price": str(value),
            "decimals": int(decimals),
            "timestamp": int(ts),
            "float_price": float(value) / (10 ** int(decimals))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"FTSO read failed: {e}")

# ==============================
# Flare: FDC 验证（占位 Demo）
# ==============================
class FdcPayload(BaseModel):
    attestation_type: str          # e.g., "delivery_confirmed", "cleaning_done", "holiday_eid"
    evidence_id: Optional[str] = None  # 外部系统单号/追踪号
    meta: Optional[Dict[str, Any]] = None

@app.post("/flare/fdc/verify")
def flare_fdc_verify(payload: FdcPayload):
    """
    占位：返回 verified=True。
    真接 FDC 时：
      1) 发起 attestation 请求
      2) 轮询获取证明（merkle / 签名）
      3) 后端或合约侧校验 proof
    """
    return {
        "attestation_type": payload.attestation_type,
        "verified": True,
        "evidence_id": payload.evidence_id,
        "meta": payload.meta
    }

# ==============================
# Flare: FAssets 占位（可选）
# ==============================
class FassetsWrapReq(BaseModel):
    asset: str               # e.g., "USDToken", "XRP", "StylePoints"
    amount: float
    target_chain: str = "flare"

@app.post("/flare/fassets/wrap")
def flare_fassets_wrap(req: FassetsWrapReq):
    # TODO: 真正集成 FAssets 流程（锁定/映射/铸造/桥接）
    return {
        "ok": True,
        "note": "Recorded request to wrap into FAsset (stub for demo)",
        "asset": req.asset,
        "amount": req.amount,
        "target_chain": req.target_chain
    }