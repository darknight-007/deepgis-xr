import logging
import traceback
from django.http import JsonResponse
from rest_framework import status
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """Global error handling middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        return self.get_response(request)
        
    def process_exception(self, request, exception):
        """Handle uncaught exceptions"""
        
        # Log the error
        logger.error(
            f"Uncaught exception: {str(exception)}\n"
            f"Request path: {request.path}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Return JSON response for API endpoints
        if request.path.startswith('/api/'):
            return JsonResponse({
                'status': 'error',
                'message': str(exception) if settings.DEBUG else 'Internal server error',
                'detail': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        # Let Django handle other errors
        return None


class APIVersionMiddleware:
    """API version handling middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Add API version to request
        if request.path.startswith('/api/'):
            version = request.path.split('/')[2]
            request.version = version
            
        return self.get_response(request)


class RequestLoggingMiddleware:
    """Request logging middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Log request
        logger.info(
            f"Request: {request.method} {request.path}\n"
            f"User: {request.user}\n"
            f"Data: {request.POST or request.body}"
        )
        
        response = self.get_response(request)
        
        # Log response
        logger.info(
            f"Response: {response.status_code}\n"
            f"Content-Type: {response.get('Content-Type', '')}"
        )
        
        return response 