"""
Middleware collection for CloudEngineered platform.
Includes search tracking, performance monitoring, and other utilities.
"""

import time
import json
import logging
import threading
from django.db import connection
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from django.conf import settings
from django.utils import timezone
from .models import SearchQuery, PopularSearch

# Thread-local storage for request metrics
_thread_locals = threading.local()
logger = logging.getLogger(__name__)


class SearchTrackingMiddleware(MiddlewareMixin):
    """Track search queries for analytics and suggestions"""
    
    def process_request(self, request):
        # Mark start time for response time calculation
        request._search_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Only track search requests
        try:
            resolver_match = resolve(request.path)
            if resolver_match.view_name == 'core:search':
                self._track_search(request, response)
        except Exception:
            # Don't break the response if tracking fails
            pass
        
        return response
    
    def _track_search(self, request, response):
        """Track search query and metrics"""
        query = request.GET.get('q', '').strip()
        if not query:
            return
        
        try:
            # Calculate response time
            response_time = None
            if hasattr(request, '_search_start_time'):
                response_time = time.time() - request._search_start_time
            
            # Get search parameters
            content_type = request.GET.get('type', '')
            category = request.GET.get('category', '')
            sort_by = request.GET.get('sort', '')
            
            # Get user info
            user = request.user if request.user.is_authenticated else None
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Count results (try to extract from response context)
            results_count = 0
            try:
                # This would need to be set in the view context
                results_count = getattr(request, '_search_results_count', 0)
            except:
                pass
            
            # Create search query record
            search_query = SearchQuery.objects.create(
                query=query,
                user=user,
                ip_address=ip_address,
                user_agent=user_agent[:1000],  # Limit length
                content_type=content_type,
                category=category,
                sort_by=sort_by,
                results_count=results_count,
                response_time=response_time,
            )
            
            # Update popular searches
            PopularSearch.increment_search(query, user)
            
        except Exception as e:
            # Log error but don't break the response
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error tracking search: {e}")


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor request performance and database usage."""
    
    def process_request(self, request):
        """Start performance monitoring for the request."""
        _thread_locals.start_time = time.time()
        _thread_locals.start_queries = len(connection.queries)
        _thread_locals.request_path = request.path
        _thread_locals.request_method = request.method
        _thread_locals.user = getattr(request, 'user', None)
        
    def process_response(self, request, response):
        """Complete performance monitoring and log metrics."""
        if not hasattr(_thread_locals, 'start_time'):
            return response
            
        # Calculate performance metrics
        total_time = time.time() - _thread_locals.start_time
        total_queries = len(connection.queries) - _thread_locals.start_queries
        
        # Get database query time
        db_time = sum(float(q['time']) for q in connection.queries[_thread_locals.start_queries:])
        
        # Calculate cache hit rate (simplified)
        cache_operations = getattr(_thread_locals, 'cache_operations', 0)
        cache_hits = getattr(_thread_locals, 'cache_hits', 0)
        cache_hit_rate = (cache_hits / cache_operations * 100) if cache_operations > 0 else 0
        
        # Determine if this is a slow request
        slow_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD', 1.0)  # 1 second
        is_slow = total_time > slow_threshold
        
        # Log performance metrics
        self.log_performance_metrics(
            request=request,
            response=response,
            total_time=total_time,
            db_time=db_time,
            query_count=total_queries,
            cache_hit_rate=cache_hit_rate,
            is_slow=is_slow
        )
        
        # Add performance headers (in development)
        if settings.DEBUG:
            response['X-Response-Time'] = f"{total_time:.3f}s"
            response['X-DB-Queries'] = str(total_queries)
            response['X-DB-Time'] = f"{db_time:.3f}s"
            response['X-Cache-Hit-Rate'] = f"{cache_hit_rate:.1f}%"
        
        return response
    
    def log_performance_metrics(self, request, response, total_time, db_time, query_count, cache_hit_rate, is_slow):
        """Log performance metrics."""
        log_data = {
            'path': request.path,
            'method': request.method,
            'status_code': response.status_code,
            'response_time': f"{total_time:.3f}s",
            'db_time': f"{db_time:.3f}s",
            'query_count': query_count,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'user': str(request.user) if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
        }
        
        if is_slow:
            logger.warning(f"Slow request detected: {log_data}")
        elif settings.DEBUG:
            logger.info(f"Request performance: {log_data}")


# Context manager for tracking specific operations
class PerformanceTracker:
    """Context manager for tracking performance of specific operations."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.start_queries = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.start_queries = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        end_queries = len(connection.queries)
        
        duration = end_time - self.start_time
        query_count = end_queries - self.start_queries
        
        logger.info(f"Operation '{self.operation_name}' completed in {duration:.3f}s with {query_count} queries")
        
        # Log slow operations
        if duration > 0.5:  # 500ms threshold
            logger.warning(f"Slow operation detected: '{self.operation_name}' took {duration:.3f}s")


# Decorator for tracking function performance
def track_performance(operation_name: str = None):
    """Decorator to track function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            name = operation_name or f"{func.__module__}.{func.__name__}"
            with PerformanceTracker(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator
