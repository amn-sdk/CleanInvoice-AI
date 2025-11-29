from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib

# JWT Configuration
SECRET_KEY = "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR"  # Should be in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def _hash_password_pre(password: str) -> bytes:
    """SHA256 hash the password to ensure it fits in bcrypt's 72 byte limit"""
    return hashlib.sha256(password.encode()).hexdigest().encode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash"""
    return bcrypt.checkpw(_hash_password_pre(plain_password), hashed_password.encode())

def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_hash_password_pre(password), salt)
    return hashed.decode()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
