"""
URL configuration for the tools app.
"""

from django.urls import path
from . import views, ai_integration
from .comparison_bot_views import (
    ComparisonBotView,
    ComparisonBotAPIView,
    QuickComparisonAPIView,
    ComparisonSuggestionsAPIView,
    ComparisonFeedbackAPIView,
    ComparisonHistoryView,
    ToolSearchAPIView
)

app_name = 'tools'

urlpatterns = [
    # Tool categories and listings
    path('', views.category_list, name='category_list'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    path('comparisons/<slug:slug>/', views.comparison_detail, name='comparison_detail'),
    
    # AI Comparison Bot
    path('compare/', ComparisonBotView.as_view(), name='comparison_bot'),
    path('compare/generate/', ComparisonBotAPIView.as_view(), name='comparison_bot_generate'),
    path('compare/quick/', QuickComparisonAPIView.as_view(), name='comparison_bot_quick'),
    path('compare/suggestions/', ComparisonSuggestionsAPIView.as_view(), name='comparison_suggestions'),
    path('compare/feedback/', ComparisonFeedbackAPIView.as_view(), name='comparison_feedback'),
    path('compare/history/', ComparisonHistoryView.as_view(), name='comparison_history'),
    path('api/search/', ToolSearchAPIView.as_view(), name='tool_search'),
    
    # AI Integration endpoints
    path('api/<int:tool_id>/generate-content/', ai_integration.generate_tool_content, name='generate_tool_content'),
    path('api/bulk-generate-reviews/', ai_integration.bulk_generate_reviews, name='bulk_generate_reviews'),
    path('api/<int:tool_id>/ai-content-history/', ai_integration.tool_ai_content_history, name='tool_ai_content_history'),
    
    # Tool detail pages
    path('<slug:category>/', views.tool_list, name='tool_list'),
    path('<slug:category>/<slug:slug>/', views.tool_detail, name='tool_detail'),
    path('<slug:category>/<slug:slug>/review/', views.create_review, name='create_review'),
]
