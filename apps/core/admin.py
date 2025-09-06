"""
Core admin interface for CloudEngineered platform.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SiteConfiguration, NewsletterSubscriber


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for site configuration.
    """
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_description', 'site_logo', 'site_favicon')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'support_email')
        }),
        ('Social Media', {
            'fields': ('twitter_url', 'linkedin_url', 'github_url')
        }),
        ('Analytics & SEO', {
            'fields': ('google_analytics_id', 'google_search_console_code', 'default_meta_description')
        }),
        ('Feature Flags', {
            'fields': ('enable_user_registration', 'enable_comments', 'enable_newsletter', 'maintenance_mode')
        }),
    )
    
    def has_add_permission(self, request):
        """Only allow one site configuration instance."""
        return not SiteConfiguration.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Don't allow deletion of site configuration."""
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """
    Admin interface for newsletter subscribers.
    """
    list_display = ('email', 'is_active', 'source', 'created_at', 'subscriber_status')
    list_filter = ('is_active', 'source', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def subscriber_status(self, obj):
        """Display subscriber status with color coding."""
        if obj.is_active:
            return format_html('<span style="color: green;">Active</span>')
        return format_html('<span style="color: red;">Inactive</span>')
    subscriber_status.short_description = 'Status'
    
    def activate_subscribers(self, request, queryset):
        """Bulk activate subscribers."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscribers activated.')
    activate_subscribers.short_description = 'Activate selected subscribers'
    
    def deactivate_subscribers(self, request, queryset):
        """Bulk deactivate subscribers."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscribers deactivated.')
    deactivate_subscribers.short_description = 'Deactivate selected subscribers'
