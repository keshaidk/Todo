"""
Authentication tests
"""
import pytest
import hmac
import hashlib
import json
from datetime import datetime, timedelta, timezone

from auth import verify_telegram_auth_data, extract_user_id
from config import settings
from fastapi import HTTPException


def create_valid_init_data(user_id: int = 123456):
    """Helper to create valid init data"""
    user_data = json.dumps({"id": user_id, "first_name": "Test"})
    auth_date = int(datetime.now(timezone.utc).timestamp())
    
    params = {
        "user": user_data,
        "auth_date": str(auth_date),
    }
    
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    params["hash"] = hash_value
    return "&".join(f"{k}={v}" for k, v in params.items())


def test_verify_valid_auth_data():
    """Test verifying valid authentication data"""
    init_data = create_valid_init_data()
    result = verify_telegram_auth_data(init_data)
    assert "user" in result
    assert "auth_date" in result


def test_extract_user_id():
    """Test extracting user ID"""
    user_id = 999888777
    init_data = create_valid_init_data(user_id)
    extracted_id = extract_user_id(init_data)
    assert extracted_id == user_id


def test_invalid_hash():
    """Test with invalid hash"""
    init_data = "user=test&auth_date=1700000000&hash=invalid"
    with pytest.raises(HTTPException) as exc_info:
        verify_telegram_auth_data(init_data)
    assert exc_info.value.status_code == 401


def test_missing_hash():
    """Test with missing hash"""
    init_data = "user=test&auth_date=1700000000"
    with pytest.raises(HTTPException) as exc_info:
        verify_telegram_auth_data(init_data)
    assert exc_info.value.status_code == 401


def test_expired_auth_data():
    """Test with expired auth data"""
    # Create data from 25 hours ago
    old_timestamp = int((datetime.now(timezone.utc) - timedelta(hours=25)).timestamp())
    
    user_data = json.dumps({"id": 123456, "first_name": "Test"})
    params = {
        "user": user_data,
        "auth_date": str(old_timestamp),
    }
    
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    
    secret_key = hmac.new(
        b"WebAppData",
        settings.BOT_TOKEN.encode(),
        hashlib.sha256
    ).digest()
    
    hash_value = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    params["hash"] = hash_value
    init_data = "&".join(f"{k}={v}" for k, v in params.items())
    
    with pytest.raises(HTTPException) as exc_info:
        verify_telegram_auth_data(init_data)
    assert exc_info.value.status_code == 401
