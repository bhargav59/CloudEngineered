"""
API Rate Limiting and Throttling System
Implements comprehensive API throttling with different rates for different user types.
"""

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.throttling import BaseThrottle
from rest_framework.exceptions import Throttled
import hashlib
import time
from typing import Dict, Optional, Tuple

User = get_user_model()


class RateLimitConfig:
    """Rate limiting configuration for different user types and endpoints."""
    
    # Rate limits per hour for different user types
    RATE_LIMITS = {
        'anonymous': {
            'default': 100,      # 100 requests per hour
            'api': 50,           # 50 API calls per hour
            'search': 200,       # 200 searches per hour
            'view': 500,         # 500 page views per hour
        },
        'authenticated': {
            'default': 500,      # 500 requests per hour
            'api': 200,          # 200 API calls per hour
            'search': 1000,      # 1000 searches per hour
            'view': 2000,        # 2000 page views per hour
        },
        'premium': {
            'default': 2000,     # 2000 requests per hour
            'api': 1000,         # 1000 API calls per hour
            'search': 5000,      # 5000 searches per hour
            'view': 10000,       # 10000 page views per hour
        },
        'staff': {
            'default': 10000,    # 10000 requests per hour
            'api': 5000,         # 5000 API calls per hour
            'search': 20000,     # 20000 searches per hour
            'view': 50000,       # 50000 page views per hour
        }
    }
    
    # Burst limits (per minute)
    BURST_LIMITS = {
        'anonymous': 20,     # 20 requests per minute
        'authenticated': 60, # 60 requests per minute
        'premium': 120,      # 120 requests per minute
        'staff': 300,        # 300 requests per minute
    }
    
    # Rate limit periods in seconds
    RATE_WINDOW = 3600    # 1 hour
    BURST_WINDOW = 60     # 1 minute


class RateLimiter:
    """Advanced rate limiter with sliding window and burst protection."""
    
    def __init__(self):
        self.config = RateLimitConfig()
    
    def get_user_type(self, user) -> str:
        """Determine user type for rate limiting."""
        if not user or user.is_anonymous:
            return 'anonymous'
        elif user.is_staff or user.is_superuser:
            return 'staff'
        elif hasattr(user, 'userprofile') and user.userprofile.is_premium:
            return 'premium'
        else:
            return 'authenticated'
    
    def get_rate_limit(self, user, endpoint_type: str = 'default') -> int:
        """Get rate limit for user and endpoint type."""
        user_type = self.get_user_type(user)
        return self.config.RATE_LIMITS.get(user_type, {}).get(endpoint_type, 100)
    
    def get_burst_limit(self, user) -> int:
        """Get burst limit for user."""
        user_type = self.get_user_type(user)
        return self.config.BURST_LIMITS.get(user_type, 20)
    
    def get_cache_key(self, identifier: str, endpoint_type: str, window: str) -> str:
        """Generate cache key for rate limiting."""
        key_data = f"rate_limit:{identifier}:{endpoint_type}:{window}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_identifier(self, request) -> str:
        """Get unique identifier for the request (user ID or IP)."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        else:
            # Get IP address from request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR', 'unknown')
            return f"ip:{ip}"
    
    def is_rate_limited(self, request, endpoint_type: str = 'default') -> Tuple[bool, Dict]:
        """
        Check if request should be rate limited.
        Returns (is_limited, rate_info)
        """
        identifier = self.get_identifier(request)
        user = getattr(request, 'user', None)
        
        # Get limits
        rate_limit = self.get_rate_limit(user, endpoint_type)
        burst_limit = self.get_burst_limit(user)
        
        current_time = int(time.time())
        rate_window_start = current_time - self.config.RATE_WINDOW
        burst_window_start = current_time - self.config.BURST_WINDOW
        
        # Check rate limit (sliding window)
        rate_key = self.get_cache_key(identifier, endpoint_type, 'rate')
        rate_requests = cache.get(rate_key, [])
        
        # Remove old requests outside window
        rate_requests = [req_time for req_time in rate_requests if req_time > rate_window_start]
        
        # Check burst limit
        burst_key = self.get_cache_key(identifier, endpoint_type, 'burst')
        burst_requests = cache.get(burst_key, [])
        burst_requests = [req_time for req_time in burst_requests if req_time > burst_window_start]
        
        rate_info = {
            'rate_limit': rate_limit,
            'rate_remaining': max(0, rate_limit - len(rate_requests)),
            'rate_reset': current_time + self.config.RATE_WINDOW,
            'burst_limit': burst_limit,
            'burst_remaining': max(0, burst_limit - len(burst_requests)),
            'burst_reset': current_time + self.config.BURST_WINDOW,
        }
        
        # Check limits
        if len(rate_requests) >= rate_limit:
            return True, rate_info
        
        if len(burst_requests) >= burst_limit:
            return True, rate_info
        
        # Update counters
        rate_requests.append(current_time)
        burst_requests.append(current_time)
        
        cache.set(rate_key, rate_requests, self.config.RATE_WINDOW + 60)
        cache.set(burst_key, burst_requests, self.config.BURST_WINDOW + 60)
        
        return False, rate_info


class CloudEngineeredThrottle(BaseThrottle):
    """Custom DRF throttle class for CloudEngineered API."""
    
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter()
    
    def allow_request(self, request, view):
        """Determine if request should be allowed."""
        # Determine endpoint type based on view
        endpoint_type = self.get_endpoint_type(view)
        
        is_limited, rate_info = self.rate_limiter.is_rate_limited(request, endpoint_type)
        
        # Store rate info for response headers
        self.rate_info = rate_info
        
        return not is_limited
    
    def get_endpoint_type(self, view) -> str:
        """Determine endpoint type from view."""
        view_name = getattr(view, '__class__', {})
        if hasattr(view_name, '__name__'):
            view_name = view_name.__name__.lower()
        else:
            view_name = str(view_name).lower()
        
        if 'search' in view_name:
            return 'search'
        elif 'api' in view_name or hasattr(view, 'serializer_class'):
            return 'api'
        else:
            return 'view'
    
    def wait(self):
        """Return time to wait before next request."""
        if hasattr(self, 'rate_info'):
            return min(self.rate_info['rate_reset'], self.rate_info['burst_reset']) - int(time.time())
        return 60


class RateLimitMiddleware:
    """Middleware to apply rate limiting to all requests."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = RateLimiter()
    
    def __call__(self, request):
        # Skip rate limiting for certain paths
        skip_paths = ['/admin/', '/static/', '/media/', '/health/', '/metrics/']
        if any(request.path.startswith(path) for path in skip_paths):
            return self.get_response(request)
        
        # Determine endpoint type
        endpoint_type = self.get_endpoint_type(request)
        
        # Check rate limit
        is_limited, rate_info = self.rate_limiter.is_rate_limited(request, endpoint_type)
        
        if is_limited:
            return self.rate_limit_response(rate_info)
        
        # Process request
        response = self.get_response(request)
        
        # Add rate limit headers
        self.add_rate_limit_headers(response, rate_info)
        
        return response
    
    def get_endpoint_type(self, request) -> str:
        """Determine endpoint type from request path."""
        path = request.path.lower()
        
        if '/api/' in path:
            return 'api'
        elif '/search/' in path or 'search' in request.GET:
            return 'search'
        else:
            return 'view'
    
    def rate_limit_response(self, rate_info: Dict) -> JsonResponse:
        """Return rate limit exceeded response."""
        retry_after = min(
            rate_info['rate_reset'] - int(time.time()),
            rate_info['burst_reset'] - int(time.time())
        )
        
        response_data = {
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'rate_limit': rate_info['rate_limit'],
            'rate_remaining': rate_info['rate_remaining'],
            'retry_after': retry_after,
        }
        
        response = JsonResponse(response_data, status=429)
        self.add_rate_limit_headers(response, rate_info)
        response['Retry-After'] = str(retry_after)
        
        return response
    
    def add_rate_limit_headers(self, response, rate_info: Dict):
        """Add rate limiting headers to response."""
        response['X-RateLimit-Limit'] = str(rate_info['rate_limit'])
        response['X-RateLimit-Remaining'] = str(rate_info['rate_remaining'])
        response['X-RateLimit-Reset'] = str(rate_info['rate_reset'])
        response['X-RateLimit-Burst-Limit'] = str(rate_info['burst_limit'])
        response['X-RateLimit-Burst-Remaining'] = str(rate_info['burst_remaining'])


# Rate limiting decorators
def rate_limit(endpoint_type: str = 'default'):
    """Decorator to apply rate limiting to views."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            rate_limiter = RateLimiter()
            is_limited, rate_info = rate_limiter.is_rate_limited(request, endpoint_type)
            
            if is_limited:
                retry_after = min(
                    rate_info['rate_reset'] - int(time.time()),
                    rate_info['burst_reset'] - int(time.time())
                )
                
                response_data = {
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after,
                }
                
                response = JsonResponse(response_data, status=429)
                response['X-RateLimit-Limit'] = str(rate_info['rate_limit'])
                response['X-RateLimit-Remaining'] = str(rate_info['rate_remaining'])
                response['Retry-After'] = str(retry_after)
                
                return response
            
            # Execute view
            response = view_func(request, *args, **kwargs)
            
            # Add rate limit headers
            response['X-RateLimit-Limit'] = str(rate_info['rate_limit'])
            response['X-RateLimit-Remaining'] = str(rate_info['rate_remaining'])
            
            return response
        
        return wrapper
    return decorator


class RateLimitStatus:
    """Utility class for checking rate limit status."""
    
    @staticmethod
    def get_status(request, endpoint_type: str = 'default') -> Dict:
        """Get current rate limit status for request."""
        rate_limiter = RateLimiter()
        identifier = rate_limiter.get_identifier(request)
        user = getattr(request, 'user', None)
        
        rate_limit = rate_limiter.get_rate_limit(user, endpoint_type)
        burst_limit = rate_limiter.get_burst_limit(user)
        
        current_time = int(time.time())
        rate_window_start = current_time - rate_limiter.config.RATE_WINDOW
        burst_window_start = current_time - rate_limiter.config.BURST_WINDOW
        
        # Get current usage
        rate_key = rate_limiter.get_cache_key(identifier, endpoint_type, 'rate')
        burst_key = rate_limiter.get_cache_key(identifier, endpoint_type, 'burst')
        
        rate_requests = cache.get(rate_key, [])
        burst_requests = cache.get(burst_key, [])
        
        rate_requests = [req_time for req_time in rate_requests if req_time > rate_window_start]
        burst_requests = [req_time for req_time in burst_requests if req_time > burst_window_start]
        
        return {
            'user_type': rate_limiter.get_user_type(user),
            'endpoint_type': endpoint_type,
            'rate_limit': rate_limit,
            'rate_used': len(rate_requests),
            'rate_remaining': max(0, rate_limit - len(rate_requests)),
            'rate_reset': current_time + rate_limiter.config.RATE_WINDOW,
            'burst_limit': burst_limit,
            'burst_used': len(burst_requests),
            'burst_remaining': max(0, burst_limit - len(burst_requests)),
            'burst_reset': current_time + rate_limiter.config.BURST_WINDOW,
        }