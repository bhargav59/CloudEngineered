"""
CloudEngineered URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import sitemaps

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
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
    
    # Django Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Custom error handlers
handler404 = 'apps.core.views.handler404'
handler500 = 'apps.core.views.handler500'
