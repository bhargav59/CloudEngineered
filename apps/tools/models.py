"""
Tool models for CloudEngineered platform.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from apps.core.models import (
    TimeStampedModel, 
    SlugModel, 
    SEOModel, 
    PublishableModel, 
    ViewCountModel,
    RatingModel
)

User = get_user_model()


class Category(TimeStampedModel, SlugModel):
    """
    Tool categories (e.g., CI/CD, Monitoring, Security, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=500)
    icon = models.CharField(
        max_length=50, 
        blank=True,
        help_text="CSS class or icon name (e.g., 'fas fa-server')"
    )
    color = models.CharField(
        max_length=7, 
        default='#3B82F6',
        help_text="Hex color code for category theming"
    )
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tools:tool_list', kwargs={'category': self.slug})
    
    @property
    def tool_count(self):
        return self.tools.filter(is_published=True).count()


class Tool(TimeStampedModel, SlugModel, SEOModel, PublishableModel, ViewCountModel, RatingModel):
    """
    Core tool model representing cloud engineering and DevOps tools.
    """
    # Basic Information
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(max_length=1000)
    tagline = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Short catchy description"
    )
    
    # Categorization
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='tools'
    )
    tags = models.JSONField(
        default=list,
        help_text="List of tags for better discoverability"
    )
    
    # Media
    logo = models.ImageField(upload_to='tools/logos/', blank=True, null=True)
    screenshot = models.ImageField(upload_to='tools/screenshots/', blank=True, null=True)
    
    # External Links
    website_url = models.URLField()
    github_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)
    pricing_url = models.URLField(blank=True)
    
    # Tool Details
    pricing_model = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('freemium', 'Freemium'),
            ('paid', 'Paid'),
            ('open_source', 'Open Source'),
            ('enterprise', 'Enterprise'),
        ],
        default='freemium'
    )
    
    deployment_types = models.JSONField(
        default=list,
        help_text="List of deployment options (cloud, on-premise, hybrid, etc.)"
    )
    
    supported_platforms = models.JSONField(
        default=list,
        help_text="List of supported platforms (AWS, GCP, Azure, etc.)"
    )
    
    languages = models.JSONField(
        default=list,
        help_text="Programming languages supported or used"
    )
    
    # Features and capabilities
    features = models.JSONField(
        default=list,
        help_text="List of key features"
    )
    
    integrations = models.JSONField(
        default=list,
        help_text="List of tools/services it integrates with"
    )
    
    use_cases = models.JSONField(
        default=list,
        help_text="Common use cases and scenarios"
    )
    
    # Content and Review
    detailed_description = models.TextField(blank=True)
    pros = models.JSONField(
        default=list,
        help_text="List of pros/advantages"
    )
    cons = models.JSONField(
        default=list,
        help_text="List of cons/disadvantages"
    )
    
    # Metadata
    company = models.CharField(max_length=200, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    team_size = models.CharField(max_length=50, blank=True)
    
    # GitHub Stats (updated automatically)
    github_stars = models.PositiveIntegerField(default=0)
    github_forks = models.PositiveIntegerField(default=0)
    github_last_commit = models.DateTimeField(null=True, blank=True)
    github_issues = models.PositiveIntegerField(default=0)
    github_open_issues = models.PositiveIntegerField(default=0)
    github_closed_issues = models.PositiveIntegerField(default=0)
    github_pull_requests = models.PositiveIntegerField(default=0)
    github_contributors = models.PositiveIntegerField(default=0)
    github_watchers = models.PositiveIntegerField(default=0)
    github_release_count = models.PositiveIntegerField(default=0)
    github_latest_release = models.CharField(max_length=100, blank=True)
    github_latest_release_date = models.DateTimeField(null=True, blank=True)
    github_created_at = models.DateTimeField(null=True, blank=True)
    github_updated_at = models.DateTimeField(null=True, blank=True)
    github_stats_last_updated = models.DateTimeField(null=True, blank=True)
    
    # Performance Metrics
    performance_score = models.FloatField(
        default=0.0,
        help_text="Overall performance score (0-100)"
    )
    performance_metrics = models.JSONField(
        default=dict,
        help_text="Performance benchmarks: response_time_ms, throughput, uptime_percentage, etc."
    )
    
    # Documentation & Support
    documentation_url = models.URLField(blank=True)
    documentation_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
            ('none', 'None'),
        ],
        default='good'
    )
    api_documentation_url = models.URLField(blank=True)
    changelog_url = models.URLField(blank=True)
    
    # Support Channels
    support_channels = models.JSONField(
        default=list,
        help_text="Available support channels: email, chat, phone, forum, slack, discord, etc."
    )
    support_email = models.EmailField(blank=True)
    community_forum_url = models.URLField(blank=True)
    discord_url = models.URLField(blank=True)
    slack_url = models.URLField(blank=True)
    
    # Pricing Details (Enhanced)
    pricing_tiers = models.JSONField(
        default=list,
        help_text="Detailed pricing tiers with features: [{name, price, features, limits}]"
    )
    free_tier_available = models.BooleanField(default=False)
    free_trial_days = models.PositiveIntegerField(null=True, blank=True)
    
    # Technical Details
    tech_stack = models.JSONField(
        default=list,
        help_text="Technologies used: languages, frameworks, databases, etc."
    )
    api_available = models.BooleanField(default=False)
    api_rate_limits = models.JSONField(
        default=dict,
        help_text="API rate limits and quotas"
    )
    
    # Compliance & Security
    security_features = models.JSONField(
        default=list,
        help_text="Security features: encryption, SSO, 2FA, audit logs, etc."
    )
    compliance_certifications = models.JSONField(
        default=list,
        help_text="Compliance certifications: SOC2, GDPR, HIPAA, ISO27001, etc."
    )
    
    # Community Metrics
    community_size = models.PositiveIntegerField(
        default=0,
        help_text="Estimated community size (users, contributors, forum members)"
    )
    stackoverflow_questions = models.PositiveIntegerField(default=0)
    reddit_subscribers = models.PositiveIntegerField(default=0)
    twitter_followers = models.PositiveIntegerField(default=0)
    
    # Media & Screenshots
    screenshots = models.JSONField(
        default=list,
        help_text="List of screenshot URLs with captions"
    )
    demo_video_url = models.URLField(blank=True)
    demo_url = models.URLField(
        blank=True,
        help_text="Live demo or playground URL"
    )
    
    # Version & Release Info
    current_version = models.CharField(max_length=50, blank=True)
    release_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('biannual', 'Twice a Year'),
            ('annual', 'Annually'),
            ('irregular', 'Irregular'),
        ],
        blank=True
    )
    
    # Popularity and Status
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active Development'),
            ('maintained', 'Maintained'),
            ('deprecated', 'Deprecated'),
            ('archived', 'Archived'),
        ],
        default='active'
    )
    
    # AI Generated Content
    ai_summary = models.TextField(blank=True)
    ai_review_generated = models.BooleanField(default=False)
    ai_last_updated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'
        ordering = ['-created_at']
        indexes = [
            # Publishing and visibility
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['is_featured', 'is_published']),
            models.Index(fields=['is_trending', 'is_published']),
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['is_published', '-view_count']),
            models.Index(fields=['is_published', '-rating_sum']),
            
            # Performance optimization
            models.Index(fields=['view_count']),
            models.Index(fields=['rating_sum']),
            models.Index(fields=['rating_count']),
            models.Index(fields=['status']),
            models.Index(fields=['pricing_model']),
            
            # Search and filtering
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'pricing_model']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['github_stars']),
            
            # Time-based queries
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
            models.Index(fields=['-ai_last_updated']),
            
            # Composite indexes for common queries
            models.Index(fields=['category', 'is_published', '-view_count']),
            models.Index(fields=['is_featured', 'is_published', '-created_at']),
            models.Index(fields=['is_trending', 'is_published', '-rating_sum']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tools:tool_detail', kwargs={'category': self.category.slug, 'slug': self.slug})
    
    @property
    def rating(self):
        """Calculate average rating from rating_sum and rating_count."""
        if self.rating_count > 0:
            return round(self.rating_sum / self.rating_count, 1)
        return 0.0
    
    @property
    def github_repo_name(self):
        """Extract GitHub repository name from URL."""
        if self.github_url:
            parts = self.github_url.rstrip('/').split('/')
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
        return None
    
    def add_tag(self, tag):
        """Add a tag to the tool."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag):
        """Remove a tag from the tool."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])


class ToolComparison(TimeStampedModel, SlugModel, SEOModel, PublishableModel, ViewCountModel):
    """
    Tool comparison model for side-by-side comparisons.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    
    tools = models.ManyToManyField(Tool, related_name='comparisons')
    
    # Comparison content
    introduction = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)
    recommendation = models.TextField(blank=True)
    
    # Detailed comparison sections
    sections = models.JSONField(
        default=dict,
        help_text="Structured comparison sections with detailed analysis"
    )
    
    # Feature comparison matrix
    feature_matrix = models.JSONField(
        default=dict,
        help_text="Feature comparison matrix with detailed scoring"
    )
    
    # Pros and cons for each tool
    tool_analysis = models.JSONField(
        default=dict,
        help_text="Detailed analysis for each tool including pros/cons"
    )
    
    # Use case recommendations
    use_case_recommendations = models.JSONField(
        default=dict,
        help_text="Specific use cases and recommendations for each tool"
    )
    
    # Summary table data
    summary_table = models.JSONField(
        default=dict,
        help_text="Summary comparison table data"
    )
    
    # Comparison criteria (kept for backward compatibility)
    criteria = models.JSONField(
        default=list,
        help_text="List of comparison criteria (features, pricing, etc.)"
    )
    
    # AI Generated
    ai_generated = models.BooleanField(default=False)
    ai_last_updated = models.DateTimeField(null=True, blank=True)
    
    # Author
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tool_comparisons'
    )
    
    class Meta:
        verbose_name = 'Tool Comparison'
        verbose_name_plural = 'Tool Comparisons'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['is_published', '-view_count']),
            models.Index(fields=['slug']),
            models.Index(fields=['author']),
            models.Index(fields=['ai_generated']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tools:comparison', kwargs={'slug': self.slug})


class ToolReview(TimeStampedModel, RatingModel):
    """
    User reviews for tools.
    """
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tool_reviews')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Rating (1-5 stars)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    
    # Experience details
    usage_duration = models.CharField(
        max_length=20,
        choices=[
            ('days', 'A few days'),
            ('weeks', 'A few weeks'),
            ('months', 'A few months'),
            ('year', 'About a year'),
            ('years', 'Several years'),
        ],
        blank=True
    )
    
    use_case = models.CharField(max_length=200, blank=True)
    team_size = models.CharField(max_length=50, blank=True)
    
    # Review status
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Helpfulness tracking
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Tool Review'
        verbose_name_plural = 'Tool Reviews'
        ordering = ['-created_at']
        unique_together = ['tool', 'user']  # One review per user per tool
        indexes = [
            models.Index(fields=['tool', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['tool', 'rating']),
            models.Index(fields=['tool', 'is_verified']),
            models.Index(fields=['tool', 'is_featured']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['helpful_count']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tool.name} ({self.rating}★)"
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return round(self.helpful_count / total, 2)


# =============================================================================
# AI COMPARISON BOT MODELS
# =============================================================================

class ComparisonRequest(TimeStampedModel):
    """
    Real-time AI-powered tool comparison requests from users.
    Stores user queries and AI-generated comparison results.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Request details
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='comparison_requests'
    )
    session_id = models.CharField(
        max_length=100, 
        db_index=True,
        help_text="Anonymous session ID for non-logged-in users"
    )
    
    # Tools being compared
    tool1 = models.ForeignKey(
        'Tool',
        on_delete=models.CASCADE,
        related_name='comparisons_as_tool1'
    )
    tool2 = models.ForeignKey(
        'Tool',
        on_delete=models.CASCADE,
        related_name='comparisons_as_tool2'
    )
    
    # User query
    user_query = models.TextField(
        help_text="User's specific comparison question or requirements"
    )
    comparison_context = models.JSONField(
        default=dict,
        help_text="Additional context: use case, team size, budget, etc."
    )
    
    # Processing
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    ai_model_used = models.CharField(
        max_length=100, 
        default='openai/gpt-4o-mini',
        help_text="AI model used for generation"
    )
    processing_time = models.FloatField(
        null=True, 
        blank=True,
        help_text="Time taken to generate comparison (seconds)"
    )
    
    # AI-generated response
    comparison_result = models.JSONField(
        default=dict,
        help_text="Structured AI-generated comparison data"
    )
    raw_response = models.TextField(
        blank=True,
        help_text="Raw AI response for debugging"
    )
    
    # Metadata
    tokens_used = models.IntegerField(default=0)
    cost_estimate = models.DecimalField(
        max_digits=10, 
        decimal_places=6, 
        default=0.0
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Feedback
    was_helpful = models.BooleanField(
        null=True, 
        blank=True,
        help_text="User feedback on comparison quality"
    )
    feedback_comment = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'AI Comparison Request'
        verbose_name_plural = 'AI Comparison Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tool1', 'tool2', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.tool1.name} vs {self.tool2.name} - {self.get_status_display()}"
    
    def get_comparison_title(self):
        """Generate a title for this comparison."""
        return f"{self.tool1.name} vs {self.tool2.name}"
    
    def mark_as_processing(self):
        """Mark comparison as currently processing."""
        self.status = 'processing'
        self.save(update_fields=['status'])
    
    def mark_as_completed(self, result: dict, tokens: int = 0, time_taken: float = 0):
        """Mark comparison as completed with results."""
        self.status = 'completed'
        self.comparison_result = result
        self.tokens_used = tokens
        self.processing_time = time_taken
        self.save(update_fields=['status', 'comparison_result', 'tokens_used', 'processing_time'])
    
    def mark_as_failed(self, error_message: str):
        """Mark comparison as failed with error message."""
        self.status = 'failed'
        self.comparison_result = {'error': error_message}
        self.save(update_fields=['status', 'comparison_result'])
    
    def record_feedback(self, helpful: bool, comment: str = ''):
        """Record user feedback on comparison quality."""
        self.was_helpful = helpful
        self.feedback_comment = comment
        self.save(update_fields=['was_helpful', 'feedback_comment'])
