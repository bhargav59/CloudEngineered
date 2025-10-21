"""
Admin Configuration for Monetization App
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AffiliateNetwork, 
    AffiliateProgram, 
    AffiliateLink, 
    Commission,
    PremiumTier,
    PremiumSubscription,
    SponsoredContent
)
from .premium_reports import ReportTemplate, PremiumReport, ReportPurchaseAnalytics
from .consulting import ConsultingPackage, ConsultingBooking, ConsultingResource, ConsultantAvailability
from .freemium import TechStackProfile, CustomRecommendation, Team, TeamMembership, IntegrationRoadmap, CostCalculator


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
    list_display = ('sponsor_name', 'tool', 'content_type', 'status', 'campaign_start', 'campaign_end')
    list_filter = ('status', 'content_type', 'placement')
    search_fields = ('sponsor_name', 'sponsor_company', 'tool__name')
    date_hierarchy = 'campaign_start'


# Premium Reports
@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin interface for report templates."""
    list_display = ('name', 'report_type', 'price_basic', 'price_standard', 'price_premium', 'is_active')
    list_filter = ('is_active', 'report_type')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PremiumReport)
class PremiumReportAdmin(admin.ModelAdmin):
    """Admin interface for premium reports."""
    list_display = ('id', 'user', 'template', 'tier', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'tier')
    search_fields = ('user__username', 'user__email', 'template__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(ReportPurchaseAnalytics)
class ReportPurchaseAnalyticsAdmin(admin.ModelAdmin):
    """Admin interface for report purchase analytics."""
    list_display = ('report', 'utm_source', 'utm_campaign')
    list_filter = ('utm_source',)
    search_fields = ('report__user__username', 'utm_campaign')


# Consulting
@admin.register(ConsultingPackage)
class ConsultingPackageAdmin(admin.ModelAdmin):
    """Admin interface for consulting packages."""
    list_display = ('name', 'package_type', 'price', 'duration_hours', 'is_active', 'sort_order')
    list_filter = ('is_active', 'package_type')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ConsultingBooking)
class ConsultingBookingAdmin(admin.ModelAdmin):
    """Admin interface for consulting bookings."""
    list_display = ('user', 'package', 'status', 'scheduled_date', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('user__username', 'user__email', 'package__name')
    date_hierarchy = 'scheduled_date'
    readonly_fields = ('created_at', 'updated_at', 'completed_at')


@admin.register(ConsultingResource)
class ConsultingResourceAdmin(admin.ModelAdmin):
    """Admin interface for consulting resources."""
    list_display = ('name', 'resource_type', 'is_public', 'created_at')
    list_filter = ('resource_type', 'is_public')
    search_fields = ('name', 'description')


@admin.register(ConsultantAvailability)
class ConsultantAvailabilityAdmin(admin.ModelAdmin):
    """Admin interface for consultant availability."""
    list_display = ('consultant', 'date', 'start_time', 'end_time', 'is_available', 'is_booked')
    list_filter = ('is_available', 'is_booked', 'date')
    search_fields = ('consultant__username',)
    date_hierarchy = 'date'


# Freemium Features
@admin.register(TechStackProfile)
class TechStackProfileAdmin(admin.ModelAdmin):
    """Admin interface for tech stack profiles."""
    list_display = ('user', 'industry', 'team_size', 'is_complete', 'updated_at')
    list_filter = ('industry', 'team_size', 'is_complete')
    search_fields = ('user__username', 'user__email', 'company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CustomRecommendation)
class CustomRecommendationAdmin(admin.ModelAdmin):
    """Admin interface for custom recommendations."""
    list_display = ('user', 'status', 'is_premium', 'access_tier', 'created_at')
    list_filter = ('status', 'is_premium', 'access_tier')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin interface for teams."""
    list_display = ('name', 'owner', 'subscription_tier', 'member_count', 'created_at')
    list_filter = ('subscription_tier',)
    search_fields = ('name', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """Admin interface for team memberships."""
    list_display = ('user', 'team', 'role', 'status', 'joined_at')
    list_filter = ('role', 'status')
    search_fields = ('user__username', 'team__name')
    readonly_fields = ('joined_at',)


@admin.register(IntegrationRoadmap)
class IntegrationRoadmapAdmin(admin.ModelAdmin):
    """Admin interface for integration roadmaps."""
    list_display = ('user', 'title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CostCalculator)
class CostCalculatorAdmin(admin.ModelAdmin):
    """Admin interface for cost calculators."""
    list_display = ('user', 'name', 'created_at')
    list_filter = ()
    search_fields = ('user__username', 'name')
    readonly_fields = ('created_at', 'updated_at')
