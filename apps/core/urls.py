"""
Core URL patterns for CloudEngineered platform.
"""

from django.urls import path
from . import views
from . import api_views
# Temporarily commenting out AI views until circular imports are resolved
# from .views_ai import (
#     AIDashboardView, generate_tool_review_ajax, generate_comparison_ajax,
#     generate_trend_analysis_ajax, scan_github_ajax, ai_content_preview,
#     bulk_ai_operations, ai_content_analytics
# )

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Search API endpoints
    path('api/search/suggestions/', api_views.SearchSuggestionsAPI.as_view(), name='search_suggestions_api'),
    path('api/search/filters/', api_views.SearchFiltersAPI.as_view(), name='search_filters_api'),
    path('api/search/analytics/', api_views.SearchAnalyticsAPI.as_view(), name='search_analytics_api'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
    
    # AI Dashboard (Admin only) - Temporarily disabled
    # path('admin/ai-dashboard/', AIDashboardView.as_view(), name='ai_dashboard'),
    # path('admin/ai/generate-review/', generate_tool_review_ajax, name='generate_tool_review_ajax'),
    # path('admin/ai/generate-comparison/', generate_comparison_ajax, name='generate_comparison_ajax'),
    # path('admin/ai/generate-trend-analysis/', generate_trend_analysis_ajax, name='generate_trend_analysis_ajax'),
    # path('admin/ai/scan-github/', scan_github_ajax, name='scan_github_ajax'),
    # path('admin/ai/preview/', ai_content_preview, name='ai_content_preview'),
    # path('admin/ai/bulk-operations/', bulk_ai_operations, name='ai_content_preview'),
    # path('admin/ai/analytics/', ai_content_analytics, name='ai_content_analytics'),
]
