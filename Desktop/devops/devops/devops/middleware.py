"""
Custom middleware for handling database connection issues in Railway deployment
"""

import logging
from django.db import connection
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

class DatabaseHealthCheckMiddleware:
    """
    Middleware to handle database connection health checks and recovery
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Health check endpoint
        if request.path == '/health/':
            return self.health_check(request)
        
        response = self.get_response(request)
        return response

    def health_check(self, request):
        """
        Simple health check that verifies database connectivity
        """
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return HttpResponse(
                "OK - Database connected", 
                status=200,
                content_type="text/plain"
            )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return HttpResponse(
                f"ERROR - Database connection failed: {e}", 
                status=503,
                content_type="text/plain"
            )

    def process_exception(self, request, exception):
        """
        Handle database-related exceptions
        """
        if "connection" in str(exception).lower():
            logger.error(f"Database connection error: {exception}")
            # Force close the connection to trigger reconnection
            connection.close()
        return None