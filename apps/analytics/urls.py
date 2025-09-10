from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main dashboards
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('user/', views.UserAnalyticsView.as_view(), name='user_dashboard'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    
    # API endpoints
    path('api/events/', views.analytics_api_events, name='api_events'),
    path('api/content/', views.analytics_api_content, name='api_content'),
    path('api/realtime/', views.analytics_api_realtime, name='api_realtime'),
    path('api/track/', views.track_event, name='track_event'),
]
