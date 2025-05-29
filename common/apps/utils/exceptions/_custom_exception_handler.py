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
        error_message = None
        
        # Get the first error message from the ValidationError
        if hasattr(exc, 'detail') and exc.detail:
            if isinstance(exc.detail, dict):
                # Handle field-specific errors
                if 'non_field_errors' in exc.detail:
                    error_message = exc.detail['non_field_errors'][0]
                else:
                    # Get the first error from the first field
                    first_field = next(iter(exc.detail))
                    error_message = exc.detail[first_field][0]
            elif isinstance(exc.detail, list):
                error_message = exc.detail[0]
        
        return Response(
            {"error": str(error_message or "Validation error")},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle IntegrityError
    if isinstance(exc, IntegrityError):
        error_msg = str(exc).lower()
        if 'duplicate key value' in error_msg:
            return Response(
                {"error": "This item already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"error": "A database error occurred."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # For other exceptions, use DRF's default response format
    return response