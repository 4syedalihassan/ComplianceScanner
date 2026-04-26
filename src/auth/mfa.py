"""
Authentication and MFA module
"""
import bcrypt
import pyotp
import secrets
import json
from datetime import datetime, timedelta
from typing import Optional
import jwt
from jwt.exceptions import PyJWTError

import os

SECRET_KEY = os.getenv("JWT_SECRET", "CHANGE-ME-IN-PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 3600  # 1 hour
REFRESH_TOKEN_EXPIRE = 604800  # 7 days


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify bcrypt password"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def generate_totp_secret() -> str:
    """Generate TOTP secret for MFA"""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer: str = "CloudAisle") -> str:
    """Get provisioning URI for TOTP"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp(code: str, secret: str) -> bool:
    """Verify TOTP code"""
    totp = pyotp.TOTP(secret)
    # Allow 30s window (prev/current/next)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(count: int = 8) -> list[str]:
    """Generate one-time backup codes"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


def hash_backup_codes(codes: list[str]) -> list[str]:
    """Hash backup codes for storage"""
    return [bcrypt.hashpw(c.encode(), bcrypt.gensalt(rounds=10)).decode() for c in codes]


def verify_backup_code(code: str, hashed_codes: list[str]) -> tuple[bool, list[str]]:
    """Verify and consume backup code"""
    code = code.upper()
    for i, hashed in enumerate(hashed_codes):
        if bcrypt.checkpw(code.encode(), hashed.encode()):
            # Remove used code
            new_hashed = hashed_codes[:i] + hashed_codes[i+1:]
            return True, new_hashed
    return False, hashed_codes


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + expires_delta,
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(days=7),
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except PyJWTError as e:
        raise ValueError(f"Invalid token: {e}")


def create_temp_token(data: dict) -> str:
    """Create temporary MFA verification token"""
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "type": "mfa_temp"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class AuthService:
    """Authentication service"""
    
    def __init__(self, db_pool):
        self.db = db_pool
    
    async def authenticate(self, email: str, password: str) -> dict:
        """Authenticate user"""
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1", email
            )
            
            if not row:
                await self._log_audit(None, "login_fail", "User not found")
                return {"error": "Invalid credentials"}
            
            # Check account lock
            if row["locked_until"] and row["locked_until"] > datetime.utcnow():
                await self._log_audit(row["id"], "login_locked", "Account locked")
                return {"error": "Account locked"}
            
            # Verify password
            if not verify_password(password, row["password_hash"]):
                await self._increment_failed(row["id"])
                await self._log_audit(row["id"], "login_fail", "Wrong password")
                return {"error": "Invalid credentials"}
            
            # Check MFA
            if row["mfa_enabled"]:
                temp_token = create_temp_token({"user_id": row["id"], "email": row["email"]})
                await self._log_audit(row["id"], "mfa_required", "MFA required")
                return {"mfa_required": True, "temp_token": temp_token}
            
            # Success - create tokens
            await self._update_last_login(row["id"])
            await self._log_audit(row["id"], "login_success", "Login successful")
            
            return {
                "access_token": create_access_token({"user_id": row["id"], "email": row["email"], "role": row["role"]}),
                "refresh_token": create_refresh_token({"user_id": row["id"]}),
                "user": {"id": row["id"], "email": row["email"], "role": row["role"]}
            }
    
    async def verify_mfa(self, temp_token: str, code: str) -> dict:
        """Verify MFA code"""
        try:
            payload = decode_token(temp_token)
            if payload.get("type") != "mfa_temp":
                raise ValueError("Invalid token type")
        except ValueError as e:
            return {"error": str(e)}
        
        async with self.db.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1", payload["user_id"]
            )
            
            if not row:
                return {"error": "User not found"}
            
            # Try TOTP first
            if row["mfa_secret_encrypted"]:
                if verify_totp(code, row["mfa_secret_encrypted"]):
                    await self._update_last_login(row["id"])
                    await self._log_audit(row["id"], "mfa_success", "MFA verified")
                    return {
                        "access_token": create_access_token({"user_id": row["id"], "email": row["email"], "role": row["role"]}),
                        "refresh_token": create_refresh_token({"user_id": row["id"]}),
                        "user": {"id": row["id"], "email": row["email"], "role": row["role"]}
                    }
            
            # Try backup codes
            if row["mfa_backup_codes"]:
                valid, new_codes = verify_backup_code(code, row["mfa_backup_codes"])
                if valid:
                    await conn.execute(
                        "UPDATE users SET mfa_backup_codes = $1, last_login = NOW() WHERE id = $2",
                        new_codes, row["id"]
                    )
                    await self._log_audit(row["id"], "mfa_backup_used", "Backup code used")
                    return {
                        "access_token": create_access_token({"user_id": row["id"], "email": row["email"], "role": row["role"]}),
                        "refresh_token": create_refresh_token({"user_id": row["id"]}),
                        "user": {"id": row["id"], "email": row["email"], "role": row["role"]}
                    }
            
            await self._log_audit(row["id"], "mfa_fail", "Invalid MFA code")
            return {"error": "Invalid MFA code"}
    
    async def setup_mfa(self, user_id: int) -> dict:
        """Setup MFA for user"""
        secret = generate_totp_secret()
        uri = get_totp_uri(secret, "user@cloudaisle.com", "CloudAisle")
        backup_codes = generate_backup_codes()
        
        async with self.db.acquire() as conn:
            # Store encrypted secret (in production, encrypt this!)
            await conn.execute("""
                UPDATE users SET 
                    mfa_secret_encrypted = $1,
                    mfa_backup_codes = $2,
                    mfa_enabled = TRUE
                WHERE id = $3
            """, secret, backup_codes, user_id)
        
        await self._log_audit(user_id, "mfa_setup", "MFA enabled")
        
        return {
            "secret": secret,
            "uri": uri,
            "backup_codes": backup_codes
        }
    
    async def _increment_failed(self, user_id: int):
        """Increment failed login attempts"""
        async with self.db.acquire() as conn:
            await conn.execute("""
                UPDATE users SET 
                    failed_attempts = failed_attempts + 1,
                    locked_until = CASE 
                        WHEN failed_attempts >= 4 THEN NOW() + INTERVAL '15 minutes'
                        ELSE NULL
                    END
                WHERE id = $1
            """, user_id)
    
    async def _update_last_login(self, user_id: int):
        """Update last login time"""
        async with self.db.acquire() as conn:
            await conn.execute(
                "UPDATE users SET last_login = NOW(), failed_attempts = 0, locked_until = NULL WHERE id = $1",
                user_id
            )
    
    async def _log_audit(self, user_id: Optional[int], event: str, details: str = ""):
        """Log authentication audit"""
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO audit_login (user_id, event, details)
                VALUES ($1, $2, $3)
            """, user_id, event, details)
