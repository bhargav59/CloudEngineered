"""
URL configuration for the tools app.
"""

from django.urls import path
from . import views, ai_integration

app_name = 'tools'

urlpatterns = [
    # Tool categories and listings
    path('', views.category_list, name='category_list'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    
    # AI Integration endpoints
    path('api/<int:tool_id>/generate-content/', ai_integration.generate_tool_content, name='generate_tool_content'),
    path('api/bulk-generate-reviews/', ai_integration.bulk_generate_reviews, name='bulk_generate_reviews'),
    path('api/<int:tool_id>/ai-content-history/', ai_integration.tool_ai_content_history, name='tool_ai_content_history'),
    
    # Tool detail pages
    path('<slug:category>/', views.tool_list, name='tool_list'),
    path('<slug:category>/<slug:slug>/', views.tool_detail, name='tool_detail'),
]
