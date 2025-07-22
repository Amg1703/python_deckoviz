from rest_framework.views import exception_handler
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Handle ValidationError
    if isinstance(exc, ValidationError):
        error_details = {}
        
        # Get detailed error information from the ValidationError
        if hasattr(exc, 'detail') and exc.detail:
            if isinstance(exc.detail, dict):
                # Handle field-specific errors - return full details
                error_details = exc.detail
            elif isinstance(exc.detail, list):
                error_details = {"errors": exc.detail}
            else:
                error_details = {"error": str(exc.detail)}
        
        return Response(
            error_details,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle IntegrityError
    if isinstance(exc, IntegrityError):
        error_msg = str(exc).lower()
        if 'duplicate key value' in error_msg:
            return Response(
                {"error": "This item already exists.", "detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"error": "A database error occurred.", "detail": str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle any other exceptions with full detail
    if response is None:
        return Response(
            {"error": "An unexpected error occurred.", "detail": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # For other exceptions, use DRF's default response format
    return response