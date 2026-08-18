import logging
from fastapi import APIRouter, HTTPException, Response, Request
from pydantic import BaseModel, EmailStr
from app.database import UserRepository
from app.auth import get_password_hash, verify_password, create_access_token
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])
_repository = UserRepository()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def _set_auth_cookie(response: Response, token: str, request: Request):
    # In production (HTTPS), use __Host- prefix and Secure=True
    # In local development (HTTP), use a fallback name and Secure=False
    is_secure = request.url.scheme == "https"
    cookie_name = "__Host-fitmind_access" if is_secure else "fitmind_access"
    
    response.set_cookie(
        key=cookie_name,
        value=token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        path="/",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/register")
def register(req: RegisterRequest, request: Request, response: Response):
    existing = _repository.get_user_by_email(req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    hashed = get_password_hash(req.password)
    user_id = _repository.create_user(req.email, hashed)
    
    # Auto-login
    token = create_access_token({"sub": str(user_id)})
    _set_auth_cookie(response, token, request)
    return {"message": "Registered successfully"}

@router.post("/login")
def login(req: LoginRequest, request: Request, response: Response):
    user = _repository.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token = create_access_token({"sub": str(user["id"])})
    _set_auth_cookie(response, token, request)
    return {"message": "Logged in successfully"}

@router.post("/logout")
def logout(request: Request, response: Response):
    is_secure = request.url.scheme == "https"
    cookie_name = "__Host-fitmind_access" if is_secure else "fitmind_access"
    response.delete_cookie(
        key=cookie_name,
        path="/",
        httponly=True,
        secure=is_secure,
        samesite="lax",
    )
    # Also delete the other just in case
    other_cookie = "fitmind_access" if is_secure else "__Host-fitmind_access"
    response.delete_cookie(key=other_cookie, path="/")
    
    return {"message": "Logged out successfully"}
