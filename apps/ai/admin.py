from django.contrib import admin
from .models import (
    AIProvider, AIModel, ContentTemplate, ContentGeneration, 
    ContentQuality, AIUsageStatistics
)


@admin.register(AIProvider)
class AIProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'rate_limit_per_minute', 'cost_per_1k_tokens', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'provider', 'display_name', 'max_tokens', 'is_active', 'cost_per_1k_input_tokens']
    list_filter = ['provider', 'is_active', 'supports_functions', 'supports_vision']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'model', 'is_active', 'created_at']
    list_filter = ['template_type', 'model', 'is_active']
    search_fields = ['name', 'template_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template_type', 'model', 'is_active')
        }),
        ('Prompts', {
            'fields': ('system_prompt', 'user_prompt_template', 'output_format'),
            'classes': ['wide']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(ContentGeneration)
class ContentGenerationAdmin(admin.ModelAdmin):
    list_display = ['template', 'status', 'initiated_by', 'tokens_used', 'estimated_cost', 'created_at']
    list_filter = ['status', 'template__template_type', 'created_at']
    search_fields = ['template__name', 'initiated_by__username']
    readonly_fields = ['created_at', 'updated_at', 'completed_at', 'tokens_used', 'estimated_cost', 'processing_time']
    
    fieldsets = (
        ('Generation Info', {
            'fields': ('template', 'initiated_by', 'status')
        }),
        ('Input', {
            'fields': ('input_data', 'generated_prompt'),
            'classes': ['wide']
        }),
        ('Output', {
            'fields': ('generated_content', 'raw_response'),
            'classes': ['wide']
        }),
        ('Metrics', {
            'fields': ('tokens_used', 'estimated_cost', 'processing_time', 'error_message'),
            'classes': ['collapse']
        }),
        ('Related Content', {
            'fields': ('content_type', 'object_id'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(ContentQuality)
class ContentQualityAdmin(admin.ModelAdmin):
    list_display = ['generation', 'overall_score', 'technical_accuracy', 'clarity', 'approved_for_publishing', 'reviewed_by']
    list_filter = ['technical_accuracy', 'clarity', 'completeness', 'seo_optimization', 'approved_for_publishing', 'requires_human_review']
    search_fields = ['generation__template__name']
    readonly_fields = ['created_at', 'updated_at', 'overall_score']
    
    fieldsets = (
        ('Generation', {
            'fields': ('generation',)
        }),
        ('Automated Metrics', {
            'fields': ('readability_score', 'word_count', 'paragraph_count', 'has_headings', 'has_links', 'has_lists')
        }),
        ('Quality Scores', {
            'fields': ('technical_accuracy', 'clarity', 'completeness', 'seo_optimization', 'overall_score')
        }),
        ('Review', {
            'fields': ('requires_human_review', 'review_notes', 'reviewed_by', 'reviewed_at', 'approved_for_publishing')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(AIUsageStatistics)
class AIUsageStatisticsAdmin(admin.ModelAdmin):
    list_display = ['provider', 'model', 'date', 'total_requests', 'total_tokens', 'total_cost', 'success_rate']
    list_filter = ['provider', 'model', 'date']
    search_fields = ['provider__name', 'model__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('provider', 'model', 'date')
        }),
        ('Usage Metrics', {
            'fields': ('total_requests', 'total_tokens', 'total_input_tokens', 'total_output_tokens')
        }),
        ('Cost & Performance', {
            'fields': ('total_cost', 'average_response_time', 'success_rate', 'error_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
