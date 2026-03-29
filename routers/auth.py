import json
import uuid
from datetime import datetime
from fastapi import APIRouter
from models.schemas import LoginRequest, LoginResponse

router = APIRouter()

# In-memory session store (replace with DB in production)
sessions = {}
otps = {}

@router.post("/login/request-otp")
async def request_otp(mobile: str):
    """Simulate OTP sending"""
    otp = "1234"  # Fixed OTP for demo
    otps[mobile] = otp
    return {
        "success": True,
        "message": f"OTP sent to {mobile}. (Demo OTP: 1234)",
        "mobile": mobile
    }

@router.post("/login/verify-otp", response_model=LoginResponse)
async def verify_otp(request: LoginRequest):
    """Verify OTP and create session"""
    mobile = request.mobile
    entered_otp = request.otp

    if entered_otp == "1234" or otps.get(mobile) == entered_otp:
        farmer_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, mobile))
        token = str(uuid.uuid4())
        sessions[token] = {"farmer_id": farmer_id, "mobile": mobile}
        return LoginResponse(
            success=True,
            message="Login successful! Welcome to KrishiAI.",
            token=token,
            farmer_id=farmer_id
        )
    return LoginResponse(success=False, message="Invalid OTP. Please try again.")

@router.post("/logout")
async def logout(token: str):
    sessions.pop(token, None)
    return {"success": True, "message": "Logged out successfully"}
