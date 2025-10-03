"""
URL configuration for Public API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .public_api import (
    CategoryViewSet,
    ToolViewSet,
    ComparisonViewSet,
    PricingViewSet,
    AIModelsViewSet,
    api_root,
    health_check,
    user_stats,
)

app_name = 'public_api'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tools', ToolViewSet, basename='tool')
router.register(r'comparisons', ComparisonViewSet, basename='comparison')
router.register(r'pricing', PricingViewSet, basename='pricing')
router.register(r'ai-models', AIModelsViewSet, basename='aimodel')

urlpatterns = [
    # API root
    path('', api_root, name='api-root'),
    
    # Health check
    path('health/', health_check, name='health-check'),
    
    # User stats (authenticated)
    path('user/stats/', user_stats, name='user-stats'),
    
    # Router URLs
    path('', include(router.urls)),
]
