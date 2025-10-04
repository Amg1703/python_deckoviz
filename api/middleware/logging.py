import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Get the request logger
request_logger = logging.getLogger('fastapi.requests')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware to log request and response details
    """
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request start
        request_logger.info(
            f"START {request.method} {request.url.path} | "
            f"IP: {client_ip} | "
            f"User-Agent: {user_agent[:100]}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log successful response
            request_logger.info(
                f"END {request.method} {request.url.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {client_ip}"
            )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            request_logger.error(
                f"ERROR {request.method} {request.url.path} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {client_ip} | "
                f"Exception: {str(e)}"
            )
            
            # Re-raise the exception
            raise
