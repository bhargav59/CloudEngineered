"""
URLs for AI Content Generation
"""

from django.urls import path
from . import api_views, views

app_name = 'ai'

urlpatterns = [
    # Dashboard
    path('', views.ai_dashboard, name='dashboard'),
    
    # Content Templates
    path('templates/', api_views.ContentTemplateListView.as_view(), name='templates_list'),
    
    # Content Generation
    path('generate/', api_views.ContentGenerationView.as_view(), name='content_generate'),
    path('generations/', api_views.ContentGenerationView.as_view(), name='generations_list'),
    path('generations/<int:generation_id>/', api_views.ContentGenerationDetailView.as_view(), name='generation_detail'),
    path('generations/<int:generation_id>/status/', api_views.generation_status, name='generation_status'),
    
    # Quick Actions
    path('quick-review/', api_views.quick_tool_review, name='quick_tool_review'),
    
    # AI Models and Stats
    path('models/', api_views.ai_models_list, name='ai_models_list'),
    path('stats/', api_views.ai_stats, name='ai_stats'),
]
