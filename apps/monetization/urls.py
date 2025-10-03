"""
URL Configuration for Monetization App
"""
from django.urls import path
from . import views

app_name = 'monetization'

urlpatterns = [
    # Affiliate Links
    path('affiliate/<int:link_id>/click/', views.track_affiliate_click, name='affiliate_click'),
    
    # Premium Subscriptions
    path('pricing/', views.pricing_page, name='pricing'),
    path('subscribe/<str:tier_slug>/', views.subscribe, name='subscribe'),
    path('billing/', views.billing_portal, name='billing_portal'),
    
    # Stripe Webhooks
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Sponsored Content
    path('advertise/', views.advertise_page, name='advertise'),
]
