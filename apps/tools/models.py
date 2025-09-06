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
        return reverse('tools:category', kwargs={'slug': self.slug})
    
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
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['is_featured', 'is_published']),
            models.Index(fields=['is_trending', 'is_published']),
            models.Index(fields=['view_count']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('tools:detail', kwargs={'slug': self.slug})
    
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
    
    # Comparison criteria
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
    
    def __str__(self):
        return f"{self.user.username} - {self.tool.name} ({self.rating}★)"
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return round(self.helpful_count / total, 2)
