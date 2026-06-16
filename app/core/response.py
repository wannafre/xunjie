from typing import Any, Optional
from fastapi.responses import JSONResponse

# ==========================================
# Unified Response Codes (Business status codes)
# ==========================================
class ResponseCode:
    SUCCESS = "SUCCESS"
    CAPTCHA_REQUIRED = "CAPTCHA_REQUIRED"
    INVALID_CAPTCHA = "INVALID_CAPTCHA"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    ERROR = "ERROR"

def make_response(
    status_code: int,
    code: str,
    message: str,
    data: Optional[Any] = None
) -> JSONResponse:
    """
    Returns a unified JSON response structure directly to avoid FastAPI's 
    default wrapping (e.g. nested inside a 'detail' object).
    
    Structure:
    {
        "code": "BUSINESS_CODE",
        "message": "User-friendly description",
        "data": null or payload
    }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )
