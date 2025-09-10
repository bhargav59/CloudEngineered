"""
Analytics middleware for tracking user interactions and page views.
"""

from django.utils.deprecation import MiddlewareMixin
import uuid

from .models import PageView, AnalyticsEvent


class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware to automatically track page views and basic analytics.
    """
    
    def process_request(self, request):
        """
        Initialize analytics session data.
        """
        # Ensure session has analytics data
        if 'analytics_session_id' not in request.session:
            request.session['analytics_session_id'] = str(uuid.uuid4())
        
        # Store analytics session ID for use in views
        request.analytics_session_id = request.session['analytics_session_id']
        
        return None
    
    def process_response(self, request, response):
        """
        Track page view after response is generated.
        """
        # Only track successful GET requests to HTML pages
        if (response.status_code == 200 and 
            request.method == 'GET' and
            'text/html' in response.get('Content-Type', '') and
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/') and
            not request.path.startswith('/admin/') and
            not request.path.startswith('/api/')):
            
            try:
                self._track_page_view(request, response)
            except Exception as e:
                # Don't let analytics tracking break the response
                # In production, you might want to log this error
                pass
        
        return response
    
    def _track_page_view(self, request, response):
        """
        Create a PageView record for the request.
        """
        # Get user agent info
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        
        # Simple device type detection
        device_type = 'desktop'
        if 'Mobile' in user_agent_string:
            device_type = 'mobile'
        elif 'Tablet' in user_agent_string:
            device_type = 'tablet'
        
        # Simple browser detection
        browser = 'Unknown'
        if 'Chrome' in user_agent_string:
            browser = 'Chrome'
        elif 'Firefox' in user_agent_string:
            browser = 'Firefox'
        elif 'Safari' in user_agent_string:
            browser = 'Safari'
        elif 'Edge' in user_agent_string:
            browser = 'Edge'
        
        # Simple OS detection
        os = 'Unknown'
        if 'Windows' in user_agent_string:
            os = 'Windows'
        elif 'Mac' in user_agent_string:
            os = 'macOS'
        elif 'Linux' in user_agent_string:
            os = 'Linux'
        elif 'Android' in user_agent_string:
            os = 'Android'
        elif 'iOS' in user_agent_string:
            os = 'iOS'
        
        # Determine page type
        page_type = self._get_page_type(request.path)
        
        # Extract UTM parameters
        utm_params = {
            'utm_source': request.GET.get('utm_source', ''),
            'utm_medium': request.GET.get('utm_medium', ''),
            'utm_campaign': request.GET.get('utm_campaign', ''),
            'utm_term': request.GET.get('utm_term', ''),
            'utm_content': request.GET.get('utm_content', ''),
        }
        
        # Create PageView record
        PageView.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.analytics_session_id,
            page_url=request.build_absolute_uri(),
            page_title=self._extract_page_title(response),
            page_type=page_type,
            ip_address=self._get_client_ip(request),
            user_agent=user_agent_string,
            referrer=request.META.get('HTTP_REFERER', ''),
            device_type=device_type,
            browser=browser,
            os=os,
            country='',  # Will be empty for now
            city='',     # Will be empty for now
            **utm_params
        )
        
        # Also create a general analytics event
        AnalyticsEvent.objects.create(
            event_type='page_view',
            event_name=f"Page view: {page_type}",
            user=request.user if request.user.is_authenticated else None,
            session_id=request.analytics_session_id,
            ip_address=self._get_client_ip(request),
            user_agent=user_agent_string,
            referrer=request.META.get('HTTP_REFERER', ''),
            page_url=request.build_absolute_uri(),
            properties={
                'page_type': page_type,
                'device_type': device_type,
                'browser': browser,
                'os': os,
            }
        )
    
    def _get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _get_page_type(self, path):
        """
        Determine the page type based on the URL path.
        """
        if path == '/':
            return 'home'
        elif path.startswith('/tools/'):
            if '/compare/' in path:
                return 'comparison'
            elif path.count('/') > 2:  # Individual tool page
                return 'tool_detail'
            else:
                return 'tool_list'
        elif path.startswith('/content/') or path.startswith('/articles/'):
            if path.count('/') > 2:  # Individual article
                return 'article_detail'
            else:
                return 'article_list'
        elif path.startswith('/users/'):
            return 'user_profile'
        elif path.startswith('/analytics/'):
            return 'analytics'
        elif path.startswith('/search/'):
            return 'search'
        else:
            return 'other'
    
    def _extract_page_title(self, response):
        """
        Extract the page title from the response HTML.
        """
        try:
            content = response.content.decode('utf-8')
            start = content.find('<title>')
            if start != -1:
                start += 7  # Length of '<title>'
                end = content.find('</title>', start)
                if end != -1:
                    return content[start:end].strip()
        except:
            pass
        return ''


def track_event(request, event_type, event_name=None, content_object=None, properties=None, value=None):
    """
    Helper function to manually track custom events.
    
    Usage:
        from apps.analytics.middleware import track_event
        track_event(request, 'bookmark_add', 'Tool bookmarked', tool_instance)
    """
    from django.contrib.contenttypes.models import ContentType
    
    # Get content type and object ID if content_object is provided
    content_type = None
    object_id = None
    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        object_id = content_object.pk
    
    # Create the analytics event
    AnalyticsEvent.objects.create(
        event_type=event_type,
        event_name=event_name or event_type,
        user=request.user if request.user.is_authenticated else None,
        session_id=getattr(request, 'analytics_session_id', ''),
        content_type=content_type,
        object_id=object_id,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', ''),
        page_url=request.build_absolute_uri(),
        properties=properties or {},
        value=value,
    )
