"""
Admin interface for Tools app including AI Comparison Bot.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Tool, ToolComparison, ToolReview, ComparisonRequest


@admin.register(ComparisonRequest)
class ComparisonRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for AI comparison requests.
    """
    list_display = (
        'id',
        'comparison_title_display',
        'status_display',
        'user_display',
        'created_at_display',
        'processing_time_display',
        'feedback_display'
    )
    list_filter = (
        'status',
        'was_helpful',
        'ai_model_used',
        'created_at'
    )
    search_fields = (
        'user__username',
        'user__email',
        'user_query',
        'tool1__name',
        'tool2__name',
        'session_id'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'session_id',
        'ip_address',
        'user_agent',
        'processing_time',
        'tokens_used',
        'cost_estimate',
        'comparison_preview'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Comparison Details', {
            'fields': (
                'tool1',
                'tool2',
                'user_query',
                'comparison_context'
            )
        }),
        ('User Information', {
            'fields': (
                'user',
                'session_id',
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': (
                'status',
                'ai_model_used',
                'processing_time',
                'tokens_used',
                'cost_estimate'
            )
        }),
        ('Results', {
            'fields': (
                'comparison_preview',
                'comparison_result',
                'raw_response'
            ),
            'classes': ('collapse',)
        }),
        ('Feedback', {
            'fields': (
                'was_helpful',
                'feedback_comment'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def comparison_title_display(self, obj):
        """Display comparison title."""
        return format_html(
            '<strong>{} vs {}</strong>',
            obj.tool1.name,
            obj.tool2.name
        )
    comparison_title_display.short_description = 'Comparison'
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': 'gray',
            'processing': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    status_display.short_description = 'Status'
    
    def user_display(self, obj):
        """Display user or session."""
        if obj.user:
            return format_html(
                '<a href="/admin/users/user/{}/change/">{}</a>',
                obj.user.id,
                obj.user.username
            )
        return format_html('<span style="color: #999;">Anonymous ({})</span>', obj.session_id[:8])
    user_display.short_description = 'User'
    
    def created_at_display(self, obj):
        """Format created date."""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'
    created_at_display.admin_order_field = 'created_at'
    
    def processing_time_display(self, obj):
        """Display processing time."""
        if obj.processing_time:
            return format_html('{}s', round(obj.processing_time, 2))
        return '-'
    processing_time_display.short_description = 'Time'
    
    def feedback_display(self, obj):
        """Display feedback status."""
        if obj.was_helpful is None:
            return format_html('<span style="color: #999;">No feedback</span>')
        elif obj.was_helpful:
            return format_html('<span style="color: green;">👍 Helpful</span>')
        else:
            return format_html('<span style="color: red;">👎 Not helpful</span>')
    feedback_display.short_description = 'Feedback'
    
    def comparison_preview(self, obj):
        """Display preview of comparison result."""
        if obj.status != 'completed' or not obj.comparison_result:
            return 'No results available'
        
        result = obj.comparison_result
        full_text = result.get('full_text', '')
        
        if full_text:
            preview = full_text[:500] + '...' if len(full_text) > 500 else full_text
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap;">{}</div>',
                preview
            )
        return 'No content'
    comparison_preview.short_description = 'Comparison Preview'
