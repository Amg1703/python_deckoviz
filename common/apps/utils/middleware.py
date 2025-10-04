import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger('django.request')

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log detailed request information including user, timing, and response status
    """
    
    def process_request(self, request):
        """Record start time and request details"""
        request._start_time = time.time()
        
        # Get user info
        user_info = "anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f"user:{request.user.id}({request.user.username})"
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # Log request start
        logger.info(
            f"START {request.method} {request.get_full_path()} | "
            f"User: {user_info} | IP: {ip} | "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')[:100]}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Log response details and timing"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Get user info
            user_info = "anonymous"
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"user:{request.user.id}({request.user.username})"
            
            # Log response
            logger.info(
                f"END {request.method} {request.get_full_path()} | "
                f"Status: {response.status_code} | "
                f"User: {user_info} | "
                f"Duration: {duration:.3f}s"
            )
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions with request context"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Get user info
            user_info = "anonymous"
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_info = f"user:{request.user.id}({request.user.username})"
            
            # Log exception
            logger.error(
                f"ERROR {request.method} {request.get_full_path()} | "
                f"User: {user_info} | "
                f"Duration: {duration:.3f}s | "
                f"Exception: {str(exception)}"
            )
        
        return None
