from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from wallet import router as wallet_router
from rewards import router as rewards_router
from rental import router as rental_router
from pricing import router as pricing_router
from risk import router as risk_router
# choice: stylepoints is optional
# because it requires a running Flare node with FDC enabled
try:
    from stylepoints import router as sp_router
    HAS_STYLEPOINTS = True
except Exception:
    HAS_STYLEPOINTS = False

app = FastAPI(title="XRPL + Flare Rental Demo", version="1.0.0")

# open CORS for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(auth_router,   prefix="/auth",   tags=["Auth"])
app.include_router(wallet_router, prefix="/xrpl",   tags=["Wallet"])
app.include_router(rewards_router,prefix="/rewards",tags=["Rewards"])
app.include_router(rental_router, prefix="/rental", tags=["Rental"])
app.include_router(pricing_router,prefix="/pricing",tags=["Pricing"])
app.include_router(risk_router,   prefix="/risk",   tags=["Risk"])
if HAS_STYLEPOINTS:
    app.include_router(sp_router, prefix="/stylepoints", tags=["StylePoints (On-chain)"])

@app.get("/")
def root():
    return {"ok": True, "service": "XRPL+Flare Rental API"}