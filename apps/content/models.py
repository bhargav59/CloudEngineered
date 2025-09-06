"""
Content models for CloudEngineered platform.
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
from apps.tools.models import Category

User = get_user_model()


class Article(TimeStampedModel, SlugModel, SEOModel, PublishableModel, ViewCountModel, RatingModel):
    """
    Blog articles, reviews, and guides.
    """
    ARTICLE_TYPES = [
        ('review', 'Tool Review'),
        ('comparison', 'Tool Comparison'),
        ('guide', 'How-to Guide'),
        ('analysis', 'Trend Analysis'),
        ('news', 'Industry News'),
        ('tutorial', 'Tutorial'),
        ('opinion', 'Opinion'),
    ]
    
    title = models.CharField(max_length=200)
    excerpt = models.TextField(
        max_length=300,
        help_text="Short description for cards and previews"
    )
    content = models.TextField()
    
    # Article classification
    article_type = models.CharField(max_length=20, choices=ARTICLE_TYPES, default='review')
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='articles'
    )
    
    # Author and attribution
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='articles'
    )
    author_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Display name if different from user"
    )
    
    # Media
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=200, blank=True)
    
    # Content organization
    tags = models.JSONField(default=list, help_text="Article tags")
    related_tools = models.JSONField(
        default=list, 
        help_text="List of related tool IDs"
    )
    
    # Reading metrics
    reading_time = models.PositiveIntegerField(
        default=5,
        help_text="Estimated reading time in minutes"
    )
    word_count = models.PositiveIntegerField(default=0)
    
    # AI generation tracking
    ai_generated = models.BooleanField(default=False)
    ai_provider = models.CharField(max_length=50, blank=True)
    ai_model = models.CharField(max_length=100, blank=True)
    ai_prompt_used = models.TextField(blank=True)
    
    # Content status
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    
    # Newsletter inclusion
    include_in_newsletter = models.BooleanField(default=True)
    newsletter_sent = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['article_type', 'is_published']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['is_featured', 'is_published']),
            models.Index(fields=['published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Calculate reading time and word count
        if self.content:
            words = len(self.content.split())
            self.word_count = words
            self.reading_time = max(1, round(words / 200))  # ~200 words per minute
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            # Extract first paragraph or 150 characters
            first_para = self.content.split('\n')[0]
            self.excerpt = first_para[:150] + '...' if len(first_para) > 150 else first_para
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('content:article_detail', kwargs={'slug': self.slug})
    
    @property
    def get_author_name(self):
        """Get display author name."""
        if self.author_name:
            return self.author_name
        elif self.author:
            return self.author.get_full_name_or_username()
        return "CloudEngineered Team"
    
    def get_related_tools(self):
        """Get related Tool objects."""
        from apps.tools.models import Tool
        if self.related_tools:
            return Tool.objects.filter(id__in=self.related_tools, is_published=True)
        return Tool.objects.none()


class Comment(TimeStampedModel):
    """
    Comments on articles and tools.
    """
    # Content being commented on
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('article', 'Article'),
            ('tool', 'Tool'),
        ]
    )
    object_id = models.PositiveIntegerField()
    
    # Comment details
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    
    # Threading support
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_type} #{self.object_id}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class Newsletter(TimeStampedModel):
    """
    Newsletter issues and campaigns.
    """
    NEWSLETTER_TYPES = [
        ('weekly', 'Weekly Digest'),
        ('monthly', 'Monthly Roundup'),
        ('special', 'Special Edition'),
        ('announcement', 'Announcement'),
    ]
    
    title = models.CharField(max_length=200)
    subject_line = models.CharField(max_length=200)
    content = models.TextField()
    
    newsletter_type = models.CharField(max_length=20, choices=NEWSLETTER_TYPES, default='weekly')
    
    # Content inclusion
    featured_articles = models.ManyToManyField(
        Article, 
        blank=True,
        related_name='newsletters'
    )
    featured_tools = models.JSONField(
        default=list,
        help_text="List of featured tool IDs"
    )
    
    # Campaign details
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    
    # Analytics
    recipients_count = models.PositiveIntegerField(default=0)
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    
    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_newsletter_type_display()}"


class ContentTag(TimeStampedModel):
    """
    Tags for organizing content.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(max_length=200, blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Content Tag'
        verbose_name_plural = 'Content Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FAQ(TimeStampedModel):
    """
    Frequently Asked Questions.
    """
    question = models.CharField(max_length=200)
    answer = models.TextField()
    
    category = models.CharField(
        max_length=50,
        choices=[
            ('general', 'General'),
            ('tools', 'Tools'),
            ('platform', 'Platform'),
            ('subscription', 'Subscription'),
            ('technical', 'Technical'),
        ],
        default='general'
    )
    
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'sort_order', 'question']
    
    def __str__(self):
        return self.question
