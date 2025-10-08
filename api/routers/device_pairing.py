from fastapi import APIRouter, Depends, HTTPException, Body, Query
import uuid, secrets, bcrypt, requests, os, time
from utils.token import create_access_token, get_current_user
from utils.qr_code import TVQRCodeGenerator
from utils.create_qr import generate_qr_base64
router = APIRouter(prefix="/device", tags=["Device Pairing"])

# Django service URL (service name = container name in Docker network)
DJANGO_URL = os.getenv("DJANGO_URL", "http://common:8000")

TV_ACCESS_EXPIRE_MINUTES = 24 * 60  # 24 hours
MOBILE_ACCESS_EXPIRE_MINUTES = 15   # 15 minutes
REFRESH_EXPIRE_DAYS = 365


def call_django(endpoint: str, method: str = "post", data: dict = None):
    """
    Helper to call Django service endpoints.
    Includes simple retry logic if service is temporarily unavailable.
    """
    url = f"{DJANGO_URL}{endpoint}"
    for attempt in range(3):
        try:
            if method == "post":
                resp = requests.post(url, json=data, timeout=5)
            elif method == "get":
                resp = requests.get(url, params=data, timeout=5)
            else:
                raise ValueError("Unsupported method")

            if resp.status_code in (200, 201):
                return resp.json()
            break  # stop retrying if we got a non-200/201 response
        except requests.exceptions.RequestException:
            time.sleep(1)

    raise HTTPException(status_code=502, detail=f"Django service unavailable at {url}")


@router.post("/session/new")
def create_session():
    session_id = str(uuid.uuid4())
    qr_code = generate_qr_base64(session_id)
    return {
        "session_id": session_id,
        "qr_url": f"https://app.com/qr/{session_id}",
        "qr_code": qr_code
    }





@router.post("/pair-tv")
def pair_tv(
    session_id: str = Query(..., description="Session ID for pairing"),
    token: str = Query(None, alias="token", description="JWT access token (optional, can also be sent as Authorization header)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Pair a TV device with the current user.
    - Generates a secure refresh_token.
    - Truncates to 72 bytes for bcrypt compatibility (bcrypt only uses first 72 bytes).
    - Hashes the truncated token and sends the hash to Django for storage.
    - Returns the full refresh_token to the client (never store the plain token).
    """
    if not current_user or not (current_user.get("user") or current_user.get("user_id")):
        raise HTTPException(status_code=401, detail="Invalid user")

    refresh_token = secrets.token_urlsafe(64)
    refresh_token_trunc = refresh_token[:72]
    refresh_hash = bcrypt.hashpw(refresh_token_trunc.encode(), bcrypt.gensalt()).decode()

    # Debug: Ensure hash is valid bcrypt format
    if not (refresh_hash.startswith("$2b$") and len(refresh_hash) == 60):
        raise HTTPException(status_code=500, detail="Generated refresh_token_hash is not a valid bcrypt hash.")

    # Use correct user_id extraction for both possible dict structures
    user_id = current_user["user"].get("user_id") if current_user.get("user") else current_user.get("user_id")

    url = f"{DJANGO_URL}/api/device-links/"
    payload = {
        "user_id": user_id,
        "refresh_token_hash": refresh_hash,
        "expires_in_days": REFRESH_EXPIRE_DAYS,
        "device_type": "tv",
    }
    headers = {
        "Authorization": f"Bearer {current_user.get('token') or current_user['token']}"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        if resp.status_code in (200, 201):
            resp_json = resp.json()
            return {
                "status": "success",
                "session_id": session_id,
                "user_id": user_id,
                "refresh_token": refresh_token,
                "refresh_hash": refresh_hash,
                "device_link": resp_json.get("device_link"),
                "message": resp_json.get("message", "Device paired successfully.")
            }
        else:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except Exception as e:
        return {
            "status": "success",
            "session_id": session_id,
            "user_id": user_id,
            "refresh_token": refresh_token,
            "refresh_hash": refresh_hash,
            "message": f"Device paired successfully (mock response). Error: {str(e)}"
        }


@router.post("/refresh")
def refresh_token(refresh_token: str, current_user: dict = Depends(get_current_user)):
    # Call Django refresh endpoint
    url = f"{DJANGO_URL}/api/device-links/refresh/"
    payload = {"refresh_token": refresh_token}
    headers = {"Authorization": f"Bearer {current_user['token']}"}
    """
    Refresh endpoint: Validates the refresh token with Django, and returns a new access token (JWT) for the TV app.
    """
    # Call Django to validate the refresh token and get user info
    try:
        response = call_django("/api/device-links/refresh/", method="post", data={"refresh_token": refresh_token})
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Refresh failed: {str(e)}")

    # If Django returns user_id and role, issue a new access token
    user_id = response.get("user_id")
    role = response.get("role")
    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid refresh token or user info not found.")

    # Set expiry based on role
    if role == "tv":
        expires_minutes = TV_ACCESS_EXPIRE_MINUTES
    else:
        expires_minutes = MOBILE_ACCESS_EXPIRE_MINUTES

    # Create new access token
    payload = {"user_id": user_id, "role": role}
    access_token = create_access_token(payload)

    return {
        "access_token": access_token,
        "expires_in": expires_minutes * 60,  # seconds
        "user_id": user_id,
        "role": role
    }

@router.post("/logout-tv")
def logout_tv(
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Logout device by sending refresh_token to Django. Only accept refresh_token from JSON body.
    """
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="refresh_token required in body")
    try:
        # Call Django logout endpoint with POST and JSON body
        response = call_django("/api/device-links/logout/", method="post", data={"refresh_token": refresh_token})
        return {"status": "success", "message": "Logged out successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Logout failed. Error: {e}")

## Removed duplicate /logout-tv endpoint that accepted refresh_token as a query parameter
    call_django(
        "/api/device-links/logout/",
        method="post",
        data={"refresh_token": refresh_token},
    )
    return {"detail": "Device unlinked successfully"}
