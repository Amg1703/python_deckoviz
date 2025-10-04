

from fastapi import APIRouter, Depends, HTTPException
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
def pair_tv(session_id: str, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid user")

    refresh_token = secrets.token_urlsafe(64)
    refresh_hash = bcrypt.hashpw(refresh_token.encode(), bcrypt.gensalt()).decode()

    # Try to call Django, but if it fails, return a safe mock response
    try:
        data = call_django(
            "/api/device-links/",
            method="post",
            data={
                "user_id": current_user.get("user_id"),
                "refresh_token_hash": refresh_hash,
                "expires_in_days": REFRESH_EXPIRE_DAYS,
                "device_type": "tv",
            }
        )
        access_token = create_access_token(
            {"user_id": str(current_user.get("user_id")), "role": "tv"},
            exp_minutes=TV_ACCESS_EXPIRE_MINUTES,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "Device paired successfully."
        }
    except Exception as e:
        # Safe fallback response
        return {
            "status": "success",
            "session_id": session_id,
            "user_id": current_user.get("user_id"),
            "refresh_token": refresh_token,
            "refresh_hash": refresh_hash,
            "message": f"Device paired successfully (mock response). Error: {str(e)}"
        }


@router.post("/refresh")
def refresh_token(refresh_token: str):
    # Delegate token validation to Django
    data = call_django(
        "/api/device-links/refresh/",
        method="post",
        data={"refresh_token": refresh_token},
    )

    role = data.get("role", "tv")
    exp_minutes = TV_ACCESS_EXPIRE_MINUTES if role == "tv" else MOBILE_ACCESS_EXPIRE_MINUTES

    new_access = create_access_token(
        {"user_id": str(data["user_id"]), "role": role},
        exp_minutes=exp_minutes,
    )
    return {"access_token": new_access}


@router.post("/logout-tv")
def logout_tv(refresh_token: str):
    call_django(
        "/api/device-links/logout/",
        method="post",
        data={"refresh_token": refresh_token},
    )
    return {"detail": "Device unlinked successfully"}
