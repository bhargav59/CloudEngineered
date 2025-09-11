from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json

User = get_user_model()


class AIProvider(models.Model):
    """AI service providers (OpenAI, Claude, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    api_key_name = models.CharField(max_length=100, help_text="Environment variable name for API key")
    base_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    cost_per_1k_tokens = models.DecimalField(max_digits=10, decimal_places=6, default=0.002)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AIModel(models.Model):
    """AI models available from providers"""
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    max_tokens = models.IntegerField(default=4096)
    supports_functions = models.BooleanField(default=False)
    supports_vision = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    cost_per_1k_input_tokens = models.DecimalField(max_digits=10, decimal_places=6, default=0.0015)
    cost_per_1k_output_tokens = models.DecimalField(max_digits=10, decimal_places=6, default=0.002)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['provider', 'name']
        unique_together = ['provider', 'name']

    def __str__(self):
        return f"{self.provider.name} - {self.display_name}"


class ContentTemplate(models.Model):
    """Templates for different types of AI-generated content"""
    TEMPLATE_TYPES = [
        ('tool_review', 'Tool Review'),
        ('comparison', 'Tool Comparison'),
        ('guide', 'How-to Guide'),
        ('news', 'News Article'),
        ('tutorial', 'Tutorial'),
        ('overview', 'Tool Overview'),
    ]

    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    system_prompt = models.TextField(help_text="System prompt for AI model")
    user_prompt_template = models.TextField(help_text="User prompt template with placeholders")
    output_format = models.TextField(help_text="Expected output format/structure")
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='templates')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"


class ContentGeneration(models.Model):
    """Track AI content generation requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    template = models.ForeignKey(ContentTemplate, on_delete=models.CASCADE, related_name='generations')
    initiated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_generations', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Input data
    input_data = models.JSONField(help_text="Input parameters for content generation")
    generated_prompt = models.TextField(blank=True, help_text="Final prompt sent to AI")
    
    # Output data
    generated_content = models.TextField(blank=True)
    raw_response = models.JSONField(blank=True, null=True, help_text="Raw AI response")
    
    # Metadata
    tokens_used = models.IntegerField(default=0)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    processing_time = models.FloatField(default=0.0, help_text="Processing time in seconds")
    error_message = models.TextField(blank=True)
    
    # Related content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.status} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def mark_completed(self):
        """Mark generation as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        """Mark generation as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()


class ContentQuality(models.Model):
    """Quality assessment for AI-generated content"""
    QUALITY_SCORES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    generation = models.OneToOneField(ContentGeneration, on_delete=models.CASCADE, related_name='quality')
    
    # Automated quality metrics
    readability_score = models.FloatField(null=True, blank=True)
    word_count = models.IntegerField(default=0)
    paragraph_count = models.IntegerField(default=0)
    has_headings = models.BooleanField(default=False)
    has_links = models.BooleanField(default=False)
    has_lists = models.BooleanField(default=False)
    
    # Content quality scores
    technical_accuracy = models.IntegerField(choices=QUALITY_SCORES, null=True, blank=True)
    clarity = models.IntegerField(choices=QUALITY_SCORES, null=True, blank=True)
    completeness = models.IntegerField(choices=QUALITY_SCORES, null=True, blank=True)
    seo_optimization = models.IntegerField(choices=QUALITY_SCORES, null=True, blank=True)
    
    # Overall assessment
    overall_score = models.FloatField(null=True, blank=True)
    requires_human_review = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True)
    
    # Human review
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_content')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_for_publishing = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quality for {self.generation} - Score: {self.overall_score or 'Not assessed'}"

    def calculate_overall_score(self):
        """Calculate overall quality score from individual metrics"""
        scores = [
            self.technical_accuracy,
            self.clarity,
            self.completeness,
            self.seo_optimization
        ]
        valid_scores = [score for score in scores if score is not None]
        if valid_scores:
            self.overall_score = sum(valid_scores) / len(valid_scores)
            self.save()
        return self.overall_score


class AIUsageStatistics(models.Model):
    """Track AI usage and costs"""
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE, related_name='usage_stats')
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='usage_stats')
    date = models.DateField()
    
    # Usage metrics
    total_requests = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    total_input_tokens = models.IntegerField(default=0)
    total_output_tokens = models.IntegerField(default=0)
    
    # Cost metrics
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    
    # Performance metrics
    average_response_time = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)
    error_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['provider', 'model', 'date']

    def __str__(self):
        return f"{self.provider.name} {self.model.name} - {self.date}"
