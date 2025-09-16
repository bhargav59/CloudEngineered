"""
SEO and Performance Middleware for CloudEngineered
"""

from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import gzip
import io


class SEOMiddleware(MiddlewareMixin):
    """
    Middleware to add SEO-friendly headers and optimizations
    """
    
    def process_response(self, request, response):
        """Add SEO and security headers to all responses"""
        
        # Security headers for SEO
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Cache headers for static content
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            patch_cache_control(response, max_age=31536000)  # 1 year
            response['Vary'] = 'Accept-Encoding'
        
        # Add canonical URL header for pages
        if hasattr(request, 'build_absolute_uri'):
            response['Link'] = f'<{request.build_absolute_uri()}>; rel="canonical"'
        
        return response


class GzipMiddleware(MiddlewareMixin):
    """
    Middleware to compress responses for better page speed
    """
    
    def process_response(self, request, response):
        """Compress response if client accepts gzip and content is compressible"""
        
        # Check if client accepts gzip
        if 'gzip' not in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            return response
        
        # Don't compress if already compressed or if it's a small response
        if (response.get('Content-Encoding') or 
            len(response.content) < 200 or
            not self._should_compress(response)):
            return response
        
        # Compress the content
        try:
            compressed_content = self._compress_content(response.content)
            if len(compressed_content) < len(response.content):
                response.content = compressed_content
                response['Content-Encoding'] = 'gzip'
                response['Content-Length'] = str(len(compressed_content))
                response['Vary'] = 'Accept-Encoding'
        except Exception:
            # If compression fails, return original response
            pass
        
        return response
    
    def _should_compress(self, response):
        """Determine if response should be compressed"""
        content_type = response.get('Content-Type', '').lower()
        
        compressible_types = [
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript',
            'application/json',
            'text/xml',
            'application/xml',
            'text/plain'
        ]
        
        return any(ctype in content_type for ctype in compressible_types)
    
    def _compress_content(self, content):
        """Compress content using gzip"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as gz_file:
            gz_file.write(content)
        
        return buf.getvalue()


class PreloadMiddleware(MiddlewareMixin):
    """
    Middleware to add resource preload hints for better performance
    """
    
    def process_response(self, request, response):
        """Add preload headers for critical resources"""
        
        # Only add preload headers to HTML responses
        if not response.get('Content-Type', '').startswith('text/html'):
            return response
        
        preload_links = []
        
        # Preload critical CSS
        preload_links.append('</static/css/main.css>; rel=preload; as=style')
        
        # Preload critical JS
        preload_links.append('</static/js/main.js>; rel=preload; as=script')
        
        # Preload web fonts (if using)
        # preload_links.append('</static/fonts/main.woff2>; rel=preload; as=font; type=font/woff2; crossorigin')
        
        if preload_links:
            existing_link = response.get('Link', '')
            all_links = [existing_link] + preload_links if existing_link else preload_links
            response['Link'] = ', '.join(all_links)
        
        return response