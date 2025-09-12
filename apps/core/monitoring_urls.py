"""
URL patterns for monitoring and performance endpoints.
"""

from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    # Health and monitoring endpoints
    path('health/', views.health_check, name='health_check'),
    path('cache/status/', views.cache_status, name='cache_status'),
    path('performance/metrics/', views.performance_metrics, name='performance_metrics'),
    path('cache/warm/', views.warm_caches, name='warm_caches'),
    path('system/status/', views.system_status, name='system_status'),
    
    # Dashboard
    path('dashboard/', views.PerformanceDashboardView.as_view(), name='dashboard'),
]