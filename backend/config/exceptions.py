"""
Custom DRF exception handler for consistent JSON responses.

All API responses follow the format:
{
    "status": "success" | "error",
    "data": {},
    "message": ""
}
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent JSON envelope.
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response = {
            'status': 'error',
            'data': None,
            'message': _get_error_message(exc, response),
        }
        response.data = custom_response

    return response


def _get_error_message(exc, response):
    """Extract user-friendly error message from exception."""
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, str):
            return exc.detail
        if isinstance(exc.detail, dict):
            # Flatten validation errors
            messages = []
            for field, errors in exc.detail.items():
                if isinstance(errors, list):
                    messages.append(f"{field}: {', '.join(str(e) for e in errors)}")
                else:
                    messages.append(f"{field}: {errors}")
            return '; '.join(messages)
        if isinstance(exc.detail, list):
            return ', '.join(str(e) for e in exc.detail)
    return str(exc)


def success_response(data=None, message='', status_code=status.HTTP_200_OK):
    """
    Helper function for successful responses.
    """
    return Response({
        'status': 'success',
        'data': data,
        'message': message,
    }, status=status_code)


def error_response(message='An error occurred', data=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Helper function for error responses.
    """
    return Response({
        'status': 'error',
        'data': data,
        'message': message,
    }, status=status_code)
