"""
URL configuration for the tools app.
"""

from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    # Tool categories and listings
    path('', views.category_list, name='category_list'),
    path('comparisons/', views.comparison_list, name='comparison_list'),
    path('<slug:category>/', views.tool_list, name='tool_list'),
    path('<slug:category>/<slug:slug>/', views.tool_detail, name='tool_detail'),
]
