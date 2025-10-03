"""
Admin Configuration for Monetization App
"""
from django.contrib import admin
from .models import (
    AffiliateNetwork, 
    AffiliateProgram, 
    AffiliateLink, 
    Commission,
    PremiumTier,
    PremiumSubscription,
    SponsoredContent
)


@admin.register(AffiliateNetwork)
class AffiliateNetworkAdmin(admin.ModelAdmin):
    """Admin interface for affiliate networks."""
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(AffiliateProgram)
class AffiliateProgramAdmin(admin.ModelAdmin):
    """Admin interface for affiliate programs."""
    list_display = ('program_name', 'tool', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('program_name',)


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    """Admin interface for affiliate links."""
    list_display = ('program', 'is_active', 'created_at')
    list_filter = ('is_active',)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    """Admin interface for commissions."""
    list_display = ('id', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(PremiumTier)
class PremiumTierAdmin(admin.ModelAdmin):
    """Admin interface for premium subscription tiers."""
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)


@admin.register(PremiumSubscription)
class PremiumSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for premium subscriptions."""
    list_display = ('user', 'tier', 'status')
    list_filter = ('status',)


@admin.register(SponsoredContent)
class SponsoredContentAdmin(admin.ModelAdmin):
    """Admin interface for sponsored content."""
    list_display = ('id', 'status', 'created_at')
    list_filter = ('status',)
