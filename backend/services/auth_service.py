import asyncio
import logging
import jwt
import bcrypt
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import json

logger = logging.getLogger(__name__)

class UserRole(Enum):
    USER = "user"
    TRADER = "trader"
    ADMIN = "admin"
    PREMIUM = "premium"

class AuthStatus(Enum):
    PENDING_OTP = "pending_otp"
    VERIFIED = "verified"
    BLOCKED = "blocked"
    SUSPENDED = "suspended"

@dataclass
class User:
    user_id: str
    username: str
    email: str
    phone: str
    role: UserRole
    status: AuthStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    failed_attempts: int = 0
    is_2fa_enabled: bool = False
    preferences: Dict[str, Any] = None

@dataclass
class OTPRequest:
    user_id: str
    otp_code: str
    otp_type: str  # "login", "reset_password", "2fa"
    expires_at: datetime
    attempts: int = 0
    max_attempts: int = 3

@dataclass
class LoginAttempt:
    user_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: Optional[str] = None

class AuthenticationService:
    """Enhanced authentication service with OTP and security features"""
    
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        except:
            pass
        self.secret_key = "your-secret-key-here-change-in-production"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Email configuration (configure in production)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_username = "your-email@gmail.com"
        self.smtp_password = "your-app-password"
        
        # In-memory user storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.login_attempts: List[LoginAttempt] = []
        
        # Initialize with some demo users (only if Redis is available)
        if self.redis_client:
            self._initialize_demo_users()
    
    def _initialize_demo_users(self):
        """Initialize demo users for testing"""
        demo_users = [
            {
                "user_id": "user001",
                "username": "demo_user",
                "email": "demo@vittcott.com",
                "phone": "+1234567890",
                "role": UserRole.USER,
                "status": AuthStatus.VERIFIED,
                "created_at": datetime.now(),
                "password_hash": self._hash_password("demo123")
            },
            {
                "user_id": "admin001",
                "username": "admin",
                "email": "admin@vittcott.com",
                "phone": "+1234567891",
                "role": UserRole.ADMIN,
                "status": AuthStatus.VERIFIED,
                "created_at": datetime.now(),
                "password_hash": self._hash_password("admin123")
            },
            {
                "user_id": "trader001",
                "username": "trader",
                "email": "trader@vittcott.com",
                "phone": "+1234567892",
                "role": UserRole.TRADER,
                "status": AuthStatus.VERIFIED,
                "created_at": datetime.now(),
                "password_hash": self._hash_password("trader123")
            }
        ]
        
        for user_data in demo_users:
            user = User(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                status=user_data["status"],
                created_at=user_data["created_at"],
                preferences={}
            )
            self.users[user_data["user_id"]] = user
            # Store password hash separately
            if self.redis_client:
                self.redis_client.set(f"password_hash:{user_data['user_id']}", user_data["password_hash"])
    
    async def register_user(self, username: str, email: str, phone: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists
            if any(u.username == username for u in self.users.values()):
                return {"success": False, "error": "Username already exists"}
            
            if any(u.email == email for u in self.users.values()):
                return {"success": False, "error": "Email already registered"}
            
            # Create new user
            user_id = f"user_{len(self.users) + 1:03d}"
            password_hash = self._hash_password(password)
            
            user = User(
                user_id=user_id,
                username=username,
                email=email,
                phone=phone,
                role=UserRole.USER,
                status=AuthStatus.PENDING_OTP,
                created_at=datetime.now(),
                preferences={}
            )
            
            self.users[user_id] = user
            if self.redis_client:
                self.redis_client.set(f"password_hash:{user_id}", password_hash)
            
            # Send OTP for verification
            otp_result = await self.send_otp(user_id, "verification")
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "User registered successfully. Please verify your email with OTP.",
                "otp_sent": otp_result["success"]
            }
            
        except Exception as e:
            logger.error(f"User registration error: {e}")
            return {"success": False, "error": "Registration failed"}
    
    async def login_user(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Dict[str, Any]:
        """Login user with credentials"""
        try:
            # Find user by username
            user = next((u for u in self.users.values() if u.username == username), None)
            if not user:
                return {"success": False, "error": "Invalid credentials"}
            
            # Check if user is blocked
            if user.status == AuthStatus.BLOCKED:
                return {"success": False, "error": "Account is blocked. Contact support."}
            
            # Verify password
            stored_hash = self.redis_client.get(f"password_hash:{user.user_id}")
            if not stored_hash or not self._verify_password(password, stored_hash):
                # Record failed attempt
                self._record_login_attempt(user.user_id, ip_address, user_agent, False, "Invalid password")
                user.failed_attempts += 1
                
                # Block user after 5 failed attempts
                if user.failed_attempts >= 5:
                    user.status = AuthStatus.BLOCKED
                    return {"success": False, "error": "Account blocked due to multiple failed attempts"}
                
                return {"success": False, "error": "Invalid credentials"}
            
            # Check if 2FA is enabled
            if user.is_2fa_enabled:
                # Send 2FA OTP
                otp_result = await self.send_otp(user.user_id, "2fa")
                if otp_result["success"]:
                    return {
                        "success": True,
                        "requires_2fa": True,
                        "user_id": user.user_id,
                        "message": "2FA OTP sent to your phone"
                    }
                else:
                    return {"success": False, "error": "Failed to send 2FA OTP"}
            
            # Successful login
            self._record_login_attempt(user.user_id, ip_address, user_agent, True)
            user.failed_attempts = 0
            user.last_login = datetime.now()
            
            # Generate tokens
            access_token = self._create_access_token(user.user_id, user.role)
            refresh_token = self._create_refresh_token(user.user_id)
            
            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": self._user_to_dict(user),
                "message": "Login successful"
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "error": "Login failed"}
    
    async def verify_otp(self, user_id: str, otp_code: str, otp_type: str) -> Dict[str, Any]:
        """Verify OTP code"""
        try:
            # Get OTP from Redis
            otp_key = f"otp:{user_id}:{otp_type}"
            otp_data = self.redis_client.get(otp_key)
            
            if not otp_data:
                return {"success": False, "error": "OTP expired or not found"}
            
            otp_info = json.loads(otp_data)
            
            # Check if OTP is expired
            if datetime.fromisoformat(otp_info["expires_at"]) < datetime.now():
                self.redis_client.delete(otp_key)
                return {"success": False, "error": "OTP expired"}
            
            # Check if max attempts exceeded
            if otp_info["attempts"] >= otp_info["max_attempts"]:
                self.redis_client.delete(otp_key)
                return {"success": False, "error": "Max OTP attempts exceeded"}
            
            # Verify OTP code
            if otp_info["otp_code"] != otp_code:
                # Increment attempts
                otp_info["attempts"] += 1
                self.redis_client.setex(otp_key, 300, json.dumps(otp_info))  # 5 minutes
                return {"success": False, "error": "Invalid OTP code"}
            
            # OTP verified successfully
            self.redis_client.delete(otp_key)
            
            # Update user status based on OTP type
            user = self.users.get(user_id)
            if user and otp_type == "verification":
                user.status = AuthStatus.VERIFIED
            
            return {"success": True, "message": "OTP verified successfully"}
            
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return {"success": False, "error": "OTP verification failed"}
    
    async def send_otp(self, user_id: str, otp_type: str) -> Dict[str, Any]:
        """Send OTP to user's phone/email"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Generate OTP
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Store OTP in Redis (5 minutes expiry)
            otp_data = {
                "otp_code": otp_code,
                "otp_type": otp_type,
                "expires_at": (datetime.now() + timedelta(minutes=5)).isoformat(),
                "attempts": 0,
                "max_attempts": 3
            }
            
            otp_key = f"otp:{user_id}:{otp_type}"
            self.redis_client.setex(otp_key, 300, json.dumps(otp_data))
            
            # Send OTP via SMS/Email (simulated)
            if otp_type == "verification":
                message = f"Your VittCott verification code is: {otp_code}. Valid for 5 minutes."
            elif otp_type == "2fa":
                message = f"Your VittCott 2FA code is: {otp_code}. Valid for 5 minutes."
            else:
                message = f"Your VittCott OTP code is: {otp_code}. Valid for 5 minutes."
            
            # Simulate sending OTP (replace with actual SMS/Email service)
            await self._send_otp_message(user.phone, user.email, message)
            
            return {
                "success": True,
                "message": f"OTP sent to {user.phone}",
                "otp_type": otp_type
            }
            
        except Exception as e:
            logger.error(f"Send OTP error: {e}")
            return {"success": False, "error": "Failed to send OTP"}
    
    async def _send_otp_message(self, phone: str, email: str, message: str):
        """Send OTP message via SMS/Email (simulated)"""
        try:
            # In production, integrate with actual SMS/Email services
            # For now, just log the message
            logger.info(f"OTP Message to {phone}/{email}: {message}")
            
            # Simulate sending delay
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Send message error: {e}")
    
    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Initiate password reset"""
        try:
            user = next((u for u in self.users.values() if u.email == email), None)
            if not user:
                return {"success": False, "error": "Email not found"}
            
            # Send reset OTP
            otp_result = await self.send_otp(user.user_id, "reset_password")
            
            return {
                "success": True,
                "message": "Password reset OTP sent to your phone",
                "otp_sent": otp_result["success"]
            }
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return {"success": False, "error": "Password reset failed"}
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        try:
            # Verify current password
            stored_hash = self.redis_client.get(f"password_hash:{user_id}")
            if not stored_hash or not self._verify_password(current_password, stored_hash):
                return {"success": False, "error": "Current password is incorrect"}
            
            # Hash new password
            new_password_hash = self._hash_password(new_password)
            self.redis_client.set(f"password_hash:{user_id}", new_password_hash)
            
            return {"success": True, "message": "Password changed successfully"}
            
        except Exception as e:
            logger.error(f"Change password error: {e}")
            return {"success": False, "error": "Password change failed"}
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _create_access_token(self, user_id: str, role: UserRole) -> str:
        """Create JWT access token"""
        payload = {
            "user_id": user_id,
            "role": role.value,
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _record_login_attempt(self, user_id: str, ip_address: str, user_agent: str, success: bool, failure_reason: str = None):
        """Record login attempt for security monitoring"""
        attempt = LoginAttempt(
            user_id=user_id,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        self.login_attempts.append(attempt)
        
        # Keep only last 1000 attempts
        if len(self.login_attempts) > 1000:
            self.login_attempts = self.login_attempts[-1000:]
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user object to dictionary"""
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "status": user.status.value,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "is_2fa_enabled": user.is_2fa_enabled,
            "preferences": user.preferences or {}
        }
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = self.users.get(user_id)
        return self._user_to_dict(user) if user else None
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.preferences.update(preferences)
            return {"success": True, "message": "Preferences updated successfully"}
            
        except Exception as e:
            logger.error(f"Update preferences error: {e}")
            return {"success": False, "error": "Failed to update preferences"}
    
    async def enable_2fa(self, user_id: str) -> Dict[str, Any]:
        """Enable 2FA for user"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.is_2fa_enabled = True
            return {"success": True, "message": "2FA enabled successfully"}
            
        except Exception as e:
            logger.error(f"Enable 2FA error: {e}")
            return {"success": False, "error": "Failed to enable 2FA"}
    
    async def disable_2fa(self, user_id: str) -> Dict[str, Any]:
        """Disable 2FA for user"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            user.is_2fa_enabled = False
            return {"success": True, "message": "2FA disabled successfully"}
            
        except Exception as e:
            logger.error(f"Disable 2FA error: {e}")
            return {"success": False, "error": "Failed to disable 2FA"}

# Global instance
auth_service = AuthenticationService()
