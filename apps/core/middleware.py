"""
Search tracking middleware for analytics and suggestions.
"""

import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import SearchQuery, PopularSearch


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
            logger.error(f"Search tracking error: {e}")
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
