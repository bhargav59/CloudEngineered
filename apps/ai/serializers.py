"""
Serializers for AI Content Generation API
"""

from rest_framework import serializers
from .models import (
    AIProvider, AIModel, ContentTemplate, ContentGeneration, 
    ContentQuality, AIUsageStatistics
)


class AIProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProvider
        fields = ['id', 'name', 'is_active', 'rate_limit_per_minute']


class AIModelSerializer(serializers.ModelSerializer):
    provider = AIProviderSerializer(read_only=True)
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'display_name', 'provider', 'max_tokens',
            'supports_functions', 'supports_vision', 'is_active',
            'cost_per_1k_input_tokens', 'cost_per_1k_output_tokens'
        ]


class ContentTemplateSerializer(serializers.ModelSerializer):
    model = AIModelSerializer(read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = ContentTemplate
        fields = [
            'id', 'name', 'template_type', 'template_type_display',
            'system_prompt', 'user_prompt_template', 'output_format',
            'model', 'is_active', 'created_at'
        ]


class ContentQualitySerializer(serializers.ModelSerializer):
    technical_accuracy_display = serializers.CharField(source='get_technical_accuracy_display', read_only=True)
    clarity_display = serializers.CharField(source='get_clarity_display', read_only=True)
    completeness_display = serializers.CharField(source='get_completeness_display', read_only=True)
    seo_optimization_display = serializers.CharField(source='get_seo_optimization_display', read_only=True)
    
    class Meta:
        model = ContentQuality
        fields = [
            'id', 'readability_score', 'word_count', 'paragraph_count',
            'has_headings', 'has_links', 'has_lists', 
            'technical_accuracy', 'technical_accuracy_display',
            'clarity', 'clarity_display',
            'completeness', 'completeness_display',
            'seo_optimization', 'seo_optimization_display',
            'overall_score', 'requires_human_review', 'review_notes',
            'approved_for_publishing', 'reviewed_by', 'reviewed_at'
        ]


class ContentGenerationSerializer(serializers.ModelSerializer):
    template = ContentTemplateSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    quality = ContentQualitySerializer(read_only=True)
    initiated_by_username = serializers.CharField(source='initiated_by.username', read_only=True)
    
    class Meta:
        model = ContentGeneration
        fields = [
            'id', 'template', 'initiated_by', 'initiated_by_username',
            'status', 'status_display', 'input_data', 'generated_prompt',
            'generated_content', 'tokens_used', 'estimated_cost',
            'processing_time', 'error_message', 'quality',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'initiated_by', 'tokens_used', 'estimated_cost',
            'processing_time', 'created_at', 'updated_at', 'completed_at'
        ]


class ContentGenerationCreateSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    input_data = serializers.JSONField()
    
    def validate_template_id(self, value):
        try:
            template = ContentTemplate.objects.get(id=value, is_active=True)
        except ContentTemplate.DoesNotExist:
            raise serializers.ValidationError("Template not found or inactive")
        return value
    
    def validate_input_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Input data must be a dictionary")
        if not value:
            raise serializers.ValidationError("Input data cannot be empty")
        return value


class ContentGenerationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentGeneration
        fields = ['generated_content', 'status']
        
    def validate_status(self, value):
        if value not in ['completed', 'failed', 'cancelled']:
            raise serializers.ValidationError("Invalid status")
        return value


class AIUsageStatisticsSerializer(serializers.ModelSerializer):
    provider = AIProviderSerializer(read_only=True)
    model = AIModelSerializer(read_only=True)
    
    class Meta:
        model = AIUsageStatistics
        fields = [
            'id', 'provider', 'model', 'date', 'total_requests',
            'total_tokens', 'total_input_tokens', 'total_output_tokens',
            'total_cost', 'average_response_time', 'success_rate', 'error_count'
        ]


class QuickToolReviewSerializer(serializers.Serializer):
    """Serializer for quick tool review generation"""
    tool_name = serializers.CharField(max_length=200)
    tool_description = serializers.CharField()
    features = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    website_url = serializers.URLField(required=False, allow_blank=True)
    github_url = serializers.URLField(required=False, allow_blank=True)


class ContentGenerationStatsSerializer(serializers.Serializer):
    """Serializer for content generation statistics"""
    total_generations = serializers.IntegerField()
    completed_generations = serializers.IntegerField()
    failed_generations = serializers.IntegerField()
    success_rate = serializers.FloatField()
    total_tokens_used = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=4)
    average_processing_time = serializers.FloatField()
    
    # Breakdown by template type
    by_template_type = serializers.DictField(child=serializers.IntegerField())
    
    # Recent activity (last 7 days)
    recent_activity = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )
