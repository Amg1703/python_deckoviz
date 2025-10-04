from jose import jwt
from fastapi import HTTPException, status, Request
from utils.settings import SECRET_KEY, JWT_HASH_ALGORITHM

def verify_access_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=JWT_HASH_ALGORITHM)
		return payload
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")
	except Exception:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

def create_access_token(payload: dict) -> str:
	try:
		token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_HASH_ALGORITHM)
		return token
	except Exception:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")

async def get_current_user(request: Request):
	"""
	Accept JWT from either Authorization header (Bearer <token>) or query param (token/access_token).
	This allows both legacy and new mobile app requests to work seamlessly.
	"""
	token = None
	# Check Authorization header
	auth_header = request.headers.get("Authorization")
	if auth_header and auth_header.startswith("Bearer "):
		token = auth_header.split("Bearer ", 1)[1]
	# Fallback: check query param
	if not token:
		token = request.query_params.get("token") or request.query_params.get("access_token")
	if not token:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing JWT token")
	return verify_access_token(token)

