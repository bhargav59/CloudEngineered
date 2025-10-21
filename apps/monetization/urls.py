"""
Monetization URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'monetization'

# API Router
router = DefaultRouter()
router.register(r'affiliates', api_views.AffiliateViewSet, basename='affiliate')
router.register(r'premium-reports', api_views.PremiumReportViewSet, basename='premium-report')
router.register(r'consulting', api_views.ConsultingViewSet, basename='consulting')
router.register(r'tech-stack-profile', api_views.TechStackProfileViewSet, basename='tech-stack-profile')
router.register(r'teams', api_views.TeamViewSet, basename='team')
router.register(r'cost-calculator', api_views.CostCalculatorViewSet, basename='cost-calculator')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Web views - Premium Reports
    path('reports/', views.ReportListView.as_view(), name='report-list'),
    path('reports/<slug:slug>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('reports/<uuid:pk>/purchase/', views.ReportPurchaseView.as_view(), name='report-purchase'),
    path('my-reports/', views.MyReportsView.as_view(), name='my-reports'),
    
    # Consulting
    path('consulting/', views.ConsultingListView.as_view(), name='consulting-list'),
    path('consulting/<slug:slug>/', views.ConsultingDetailView.as_view(), name='consulting-detail'),
    path('consulting/<int:pk>/book/', views.ConsultingBookView.as_view(), name='consulting-book'),
    path('my-consultations/', views.MyConsultationsView.as_view(), name='my-consultations'),
    
    # Affiliate Dashboard
    path('affiliates/dashboard/', views.AffiliateDashboardView.as_view(), name='affiliate-dashboard'),
    path('affiliates/link/<int:pk>/click/', views.AffiliateClickView.as_view(), name='affiliate-click'),
    
    # Sponsored Content
    path('sponsored/', views.SponsoredContentView.as_view(), name='sponsored-content'),
    
    # Freemium Features
    path('tech-stack/', views.TechStackProfileView.as_view(), name='tech-stack-profile'),
    path('recommendations/', views.RecommendationsView.as_view(), name='recommendations'),
    path('teams/', views.TeamListView.as_view(), name='team-list'),
    path('teams/<slug:slug>/', views.TeamDetailView.as_view(), name='team-detail'),
    path('cost-calculator/', views.CostCalculatorView.as_view(), name='cost-calculator'),
    path('integration-roadmap/', views.IntegrationRoadmapView.as_view(), name='integration-roadmap'),
]
