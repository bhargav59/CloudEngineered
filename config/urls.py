"""
CloudEngineered URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from apps.core.sitemaps import sitemaps
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for Railway deployment monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'cloudengineered',
        'version': '1.0.0'
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),  # Add this line
    
    # SEO Files
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # Core application URLs
    path('', include('apps.core.urls')),
    
    # User management and authentication
    path('accounts/', include('django.contrib.auth.urls')),  # Basic Django auth URLs
    # path('accounts/', include('allauth.urls')),  # Commented out until allauth is installed
    path('users/', include('apps.users.urls')),
    
    # Main application URLs
    path('tools/', include('apps.tools.urls')),
    path('content/', include('apps.content.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('api/', include('apps.api.urls')),
    
    # AI Content Generation
    path('api/ai/', include('apps.ai.urls')),
    
    # SEO and utilities
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # path('health/', include('health_check.urls')),  # Commented out until health_check is installed
]

# API Documentation (commented out until drf_spectacular is installed)
# if settings.DEBUG:
#     from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
#     urlpatterns += [
#         path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
#         path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
#     ]

# Static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Django Debug Toolbar (optional)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass  # Debug toolbar not available

# Custom error handlers
handler404 = 'apps.core.views.handler404'
handler500 = 'apps.core.views.handler500'
