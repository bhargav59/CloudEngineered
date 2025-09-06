"""
Core URL patterns for CloudEngineered platform.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
    
    # Newsletter
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms'),
]
