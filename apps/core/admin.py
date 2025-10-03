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
    Enhanced admin interface for newsletter subscribers with analytics.
    """
    list_display = (
        'email_display', 
        'name',
        'status_display',
        'verified_display',
        'engagement_display',
        'source', 
        'subscribed_date'
    )
    list_filter = (
        'is_active', 
        'is_verified',
        'source', 
        'created_at',
        'verified_at'
    )
    search_fields = ('email', 'name', 'ip_address')
    readonly_fields = (
        'verification_token',
        'created_at', 
        'updated_at',
        'verified_at',
        'unsubscribed_at',
        'last_sent_at',
        'engagement_stats',
        'subscriber_info'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Subscriber Information', {
            'fields': ('email', 'name', 'is_active', 'is_verified')
        }),
        ('Verification', {
            'fields': ('verification_token', 'verified_at', 'unsubscribed_at'),
            'classes': ('collapse',)
        }),
        ('Engagement Metrics', {
            'fields': (
                'engagement_stats',
                'emails_sent',
                'emails_opened',
                'links_clicked',
                'last_sent_at'
            )
        }),
        ('Preferences & Tracking', {
            'fields': ('preferences', 'source', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Subscriber Details', {
            'fields': ('subscriber_info',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = [
        'activate_subscribers', 
        'deactivate_subscribers',
        'send_verification_email',
        'export_subscribers_csv',
        'mark_as_verified'
    ]
    
    def email_display(self, obj):
        """Display email with verification status icon."""
        icon = '✅' if obj.is_verified else '⏳'
        return format_html(
            '<span title="{}">{} {}</span>',
            'Verified' if obj.is_verified else 'Pending verification',
            icon,
            obj.email
        )
    email_display.short_description = 'Email'
    email_display.admin_order_field = 'email'
    
    def status_display(self, obj):
        """Display subscriber status with color coding."""
        if obj.is_active:
            return format_html(
                '<span style="color: white; background-color: #28a745; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">ACTIVE</span>'
            )
        return format_html(
            '<span style="color: white; background-color: #dc3545; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">INACTIVE</span>'
        )
    status_display.short_description = 'Status'
    
    def verified_display(self, obj):
        """Display verification status."""
        if obj.is_verified:
            return format_html(
                '<span style="color: #28a745;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: #ffc107;">⏳ Pending</span>'
        )
    verified_display.short_description = 'Verification'
    
    def engagement_display(self, obj):
        """Display engagement metrics."""
        if obj.emails_sent == 0:
            return format_html('<span style="color: #6c757d;">No emails sent</span>')
        
        open_rate = obj.open_rate
        click_rate = obj.click_rate
        
        # Color code based on engagement
        if open_rate >= 30:
            color = '#28a745'  # Green
        elif open_rate >= 15:
            color = '#ffc107'  # Yellow
        else:
            color = '#dc3545'  # Red
            
        return format_html(
            '<span style="color: {};">📊 {}% open | {}% click</span>',
            color,
            open_rate,
            click_rate
        )
    engagement_display.short_description = 'Engagement'
    
    def subscribed_date(self, obj):
        """Format subscription date."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    subscribed_date.short_description = 'Subscribed'
    subscribed_date.admin_order_field = 'created_at'
    
    def engagement_stats(self, obj):
        """Display detailed engagement statistics."""
        if obj.emails_sent == 0:
            return format_html('<p style="color: #6c757d;">No engagement data yet.</p>')
        
        return format_html(
            '''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin-top: 0;">Engagement Metrics</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Emails Sent:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Emails Opened:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Links Clicked:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;"><strong>Open Rate:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;"><strong>Click Rate:</strong></td>
                        <td style="padding: 8px;">{}%</td>
                    </tr>
                </table>
            </div>
            ''',
            obj.emails_sent,
            obj.emails_opened,
            obj.links_clicked,
            obj.open_rate,
            obj.click_rate
        )
    engagement_stats.short_description = 'Engagement Statistics'
    
    def subscriber_info(self, obj):
        """Display comprehensive subscriber information."""
        preferences = obj.preferences
        interests = preferences.get('interests', [])
        
        return format_html(
            '''
            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h4 style="margin-top: 0;">Subscriber Details</h4>
                <p><strong>Email:</strong> {}</p>
                <p><strong>Name:</strong> {}</p>
                <p><strong>Source:</strong> {}</p>
                <p><strong>Subscribed:</strong> {}</p>
                <p><strong>Verified:</strong> {}</p>
                {}
                <p><strong>IP Address:</strong> {}</p>
            </div>
            ''',
            obj.email,
            obj.name or 'Not provided',
            obj.source,
            obj.created_at.strftime('%Y-%m-%d %H:%M'),
            obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else 'Not verified',
            format_html('<p><strong>Interests:</strong> {}</p>', ', '.join(interests)) if interests else '',
            obj.ip_address or 'Unknown'
        )
    subscriber_info.short_description = 'Subscriber Information'
    
    # Bulk Actions
    def activate_subscribers(self, request, queryset):
        """Bulk activate subscribers."""
        updated = 0
        for subscriber in queryset:
            if not subscriber.is_active:
                subscriber.resubscribe()
                updated += 1
        self.message_user(request, f'{updated} subscriber(s) activated successfully.')
    activate_subscribers.short_description = '✓ Activate selected subscribers'
    
    def deactivate_subscribers(self, request, queryset):
        """Bulk deactivate subscribers."""
        updated = 0
        for subscriber in queryset:
            if subscriber.is_active:
                subscriber.unsubscribe()
                updated += 1
        self.message_user(request, f'{updated} subscriber(s) deactivated successfully.')
    deactivate_subscribers.short_description = '✗ Deactivate selected subscribers'
    
    def mark_as_verified(self, request, queryset):
        """Bulk mark subscribers as verified."""
        updated = 0
        for subscriber in queryset:
            if not subscriber.is_verified:
                subscriber.verify_email()
                updated += 1
        self.message_user(request, f'{updated} subscriber(s) marked as verified.')
    mark_as_verified.short_description = '✓ Mark as verified'
    
    def send_verification_email(self, request, queryset):
        """Resend verification emails to selected subscribers."""
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.conf import settings
        
        sent = 0
        for subscriber in queryset.filter(is_verified=False):
            try:
                verification_url = request.build_absolute_uri(
                    subscriber.get_verification_url()
                )
                
                context = {
                    'subscriber': subscriber,
                    'verification_url': verification_url,
                    'site_name': getattr(settings, 'SITE_NAME', 'CloudEngineered'),
                }
                
                html_message = render_to_string('emails/newsletter_confirmation.html', context)
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject='Confirm Your Newsletter Subscription',
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                sent += 1
            except Exception as e:
                self.message_user(request, f'Error sending to {subscriber.email}: {e}', level='error')
        
        self.message_user(request, f'{sent} verification email(s) sent successfully.')
    send_verification_email.short_description = '📧 Send verification emails'
    
    def export_subscribers_csv(self, request, queryset):
        """Export subscribers to CSV."""
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="newsletter_subscribers_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Name', 'Active', 'Verified', 'Source', 
            'Emails Sent', 'Open Rate %', 'Click Rate %', 
            'Subscribed Date', 'Verified Date'
        ])
        
        for obj in queryset:
            writer.writerow([
                obj.email,
                obj.name or '',
                'Yes' if obj.is_active else 'No',
                'Yes' if obj.is_verified else 'No',
                obj.source,
                obj.emails_sent,
                obj.open_rate,
                obj.click_rate,
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
                obj.verified_at.strftime('%Y-%m-%d %H:%M') if obj.verified_at else ''
            ])
        
        return response
    export_subscribers_csv.short_description = '📥 Export to CSV'
