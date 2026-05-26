"""
Telegram authentication utilities
"""
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from telegram import Update

from config import settings

logger = logging.getLogger(__name__)


def verify_telegram_auth_data(init_data: str) -> dict:
    """
    Verify Telegram WebApp auth data signature
    
    Args:
        init_data: The initData string from Telegram WebApp
        
    Returns:
        Parsed data as dict if valid
        
    Raises:
        HTTPException: If signature is invalid or data is expired
    """
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing init_data"
        )

    try:
        params = dict(pair.split("=") for pair in init_data.split("&"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid init_data format"
        )

    # Extract and remove hash
    hash_value = params.pop("hash", None)
    if not hash_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in init_data"
        )

    # Check auth_date
    auth_date_str = params.get("auth_date")
    if not auth_date_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth_date"
        )

    try:
        auth_date = datetime.fromtimestamp(int(auth_date_str))
        if datetime.utcnow() - auth_date > timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auth data expired (older than 24 hours)"
            )
    except (ValueError, OverflowError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth_date"
        )

    # Verify signature
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(hash_value, expected_hash):
        logger.warning(f"Invalid signature for init_data")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    return params


def extract_user_id(init_data: str) -> int:
    """Extract and verify user ID from Telegram init_data"""
    params = verify_telegram_auth_data(init_data)
    
    user_str = params.get("user")
    if not user_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user data"
        )

    try:
        import json
        user_data = json.loads(user_str)
        user_id = user_data.get("id")
        if not user_id:
            raise ValueError("Missing user id")
        return int(user_id)
    except (ValueError, KeyError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data format"
        )
