from fastapi import Header, HTTPException, Depends
import os

def require_api_key(x_api_key: str = Header(...)):
    expected = os.getenv("API_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    # return the provided api key so handlers can use it (rate limiting, logging)
    return x_api_key

def require_admin_key(x_api_key: str = Header(...)):
    expected = os.getenv("ADMIN_API_KEY")
    if not expected:
        raise HTTPException(status_code=500, detail="Admin API key not configured")
    if x_api_key != expected:
        raise HTTPException(status_code=403, detail="Admin API Key required")
    return x_api_key
