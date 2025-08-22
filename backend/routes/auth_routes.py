from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic models for request/response
class UserRegistration(BaseModel):
    username: str
    email: str
    phone: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class OTPVerification(BaseModel):
    user_id: str
    otp_code: str
    otp_type: str

class PasswordReset(BaseModel):
    email: str

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class TwoFactorEnable(BaseModel):
    enable: bool

@router.post("/register")
async def register_user(user_data: UserRegistration, request: Request):
    """Register a new user"""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        
        result = await auth_service.register_user(
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            password=user_data.password
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "user_id": result["user_id"],
                "requires_otp": True
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login")
async def login_user(login_data: UserLogin, request: Request):
    """Login user with credentials"""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")
        
        result = await auth_service.login_user(
            username=login_data.username,
            password=login_data.password,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if result["success"]:
            if result.get("requires_2fa"):
                return {
                    "success": True,
                    "requires_2fa": True,
                    "user_id": result["user_id"],
                    "message": result["message"]
                }
            else:
                return {
                    "success": True,
                    "access_token": result["access_token"],
                    "refresh_token": result["refresh_token"],
                    "user": result["user"],
                    "message": result["message"]
                }
        else:
            raise HTTPException(status_code=401, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/verify-otp")
async def verify_otp(otp_data: OTPVerification):
    """Verify OTP code for various purposes"""
    try:
        result = await auth_service.verify_otp(
            user_id=otp_data.user_id,
            otp_code=otp_data.otp_code,
            otp_type=otp_data.otp_type
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        raise HTTPException(status_code=500, detail="OTP verification failed")

@router.post("/resend-otp")
async def resend_otp(user_id: str, otp_type: str):
    """Resend OTP to user"""
    try:
        result = await auth_service.send_otp(user_id, otp_type)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Resend OTP error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend OTP")

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Initiate password reset process"""
    try:
        result = await auth_service.reset_password(email=reset_data.email)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change user password (requires authentication)"""
    try:
        # Verify token
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload["user_id"]
        
        result = await auth_service.change_password(
            user_id=user_id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail="Password change failed")

@router.post("/2fa/enable")
async def toggle_2fa(
    twofa_data: TwoFactorEnable,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Enable or disable 2FA for user"""
    try:
        # Verify token
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload["user_id"]
        
        if twofa_data.enable:
            result = await auth_service.enable_2fa(user_id)
        else:
            result = await auth_service.disable_2fa(user_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"2FA toggle error: {e}")
        raise HTTPException(status_code=500, detail="2FA operation failed")

@router.get("/profile")
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user profile"""
    try:
        # Verify token
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload["user_id"]
        user = await auth_service.get_user_by_id(user_id)
        
        if user:
            return {
                "success": True,
                "user": user
            }
        else:
            raise HTTPException(status_code=404, detail="User not found")
            
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

@router.put("/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Update user preferences"""
    try:
        # Verify token
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        user_id = payload["user_id"]
        
        result = await auth_service.update_user_preferences(user_id, preferences)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        logger.error(f"Update preferences error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (invalidate token)"""
    try:
        # In production, you would add the token to a blacklist
        # For now, just return success
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/health")
async def auth_health():
    """Health check for authentication service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": "2024-01-01T00:00:00Z"
    }
