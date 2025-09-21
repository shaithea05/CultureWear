from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict  # pydantic v2
import hashlib, uuid
from db import USERS, SESSIONS, REWARDS, WELCOME_BONUS

router = APIRouter()

def _hash(pwd: str) -> str:
    salt = "demo_salt"
    return hashlib.sha256((pwd + salt).encode()).hexdigest()



class SignUpReq(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # allow using field name or alias in requests
    firstName: str = Field(alias="first_name")
    lastName: str  = Field(alias="last_name")
    email: EmailStr
    password: str

class SignInReq(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
def signup(req: SignUpReq):
    if req.email in USERS:
        raise HTTPException(400, "Email already exists")
    USERS[req.email] = {
        "id": str(uuid.uuid4()),
        "firstName": req.firstName,
        "lastName": req.lastName,
        "email": req.email,
        "password_hash": _hash(req.password),
    }
    # welcome bonus (offline accounting)
    REWARDS[req.email] = REWARDS.get(req.email, 0) + WELCOME_BONUS
    return {"msg": "Signup success", "bonus": WELCOME_BONUS}

@router.post("/signin")
def signin(req: SignInReq):
    u = USERS.get(req.email)
    if not u or u["password_hash"] != _hash(req.password):
        raise HTTPException(401, "Invalid credentials")
    token = str(uuid.uuid4())
    SESSIONS[token] = req.email
    return {"token": token, "user": {"firstName": u["firstName"], "lastName": u["lastName"], "email": u["email"]}}