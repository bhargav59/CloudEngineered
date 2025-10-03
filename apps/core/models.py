"""
Core models for CloudEngineered platform.
Base models that other apps can inherit from.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

# Don't import User at module level to avoid circular imports
# Use get_user_model() where needed in methods


class TimeStampedModel(models.Model):
    """
    Abstract base model with timestamp fields.
    """
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class SlugModel(models.Model):
    """
    Abstract base model with slug field.
    """
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """
    Abstract base model for content that can be published/unpublished.
    """
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    
    def publish(self):
        """Mark as published and set publish date."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=['is_published', 'published_at'])
    
    def unpublish(self):
        """Mark as unpublished."""
        self.is_published = False
        self.save(update_fields=['is_published'])
    
    class Meta:
        abstract = True


class SEOModel(models.Model):
    """
    Abstract base model for SEO metadata.
    """
    meta_title = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="SEO title (max 60 characters recommended)"
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True,
        help_text="SEO description (max 160 characters recommended)"
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Comma-separated keywords"
    )
    
    class Meta:
        abstract = True


class ViewCountModel(models.Model):
    """
    Abstract base model for tracking views.
    """
    view_count = models.PositiveIntegerField(default=0)
    
    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    class Meta:
        abstract = True


class RatingModel(models.Model):
    """
    Abstract base model for user ratings.
    """
    rating_sum = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    
    @property
    def average_rating(self):
        """Calculate average rating."""
        if self.rating_count == 0:
            return 0
        return round(self.rating_sum / self.rating_count, 2)
    
    def add_rating(self, rating_value):
        """Add a rating (1-5 stars)."""
        if 1 <= rating_value <= 5:
            self.rating_sum += rating_value
            self.rating_count += 1
            self.save(update_fields=['rating_sum', 'rating_count'])
    
    class Meta:
        abstract = True


class SiteConfiguration(models.Model):
    """
    Site-wide configuration settings.
    """
    site_name = models.CharField(max_length=100, default="CloudEngineered")
    site_description = models.TextField(
        default="Comprehensive reviews and comparisons of cloud engineering and DevOps tools"
    )
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Contact information
    contact_email = models.EmailField(default="contact@cloudengineered.io")
    support_email = models.EmailField(default="support@cloudengineered.io")
    
    # Social media links
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_search_console_code = models.TextField(blank=True)
    
    # SEO
    default_meta_description = models.TextField(
        max_length=160,
        default="Discover and compare the best cloud engineering and DevOps tools. In-depth reviews, comparisons, and insights for technical professionals."
    )
    
    # Features flags
    enable_user_registration = models.BooleanField(default=True)
    enable_comments = models.BooleanField(default=True)
    enable_newsletter = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_instance(cls):
        """Get or create site configuration instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class NewsletterSubscriber(TimeStampedModel):
    """
    Newsletter subscription model with email verification.
    """
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True, help_text="Subscriber's name (optional)")
    
    # Verification
    is_verified = models.BooleanField(default=False, help_text="Email verified")
    verification_token = models.CharField(max_length=64, unique=True, db_index=True, default='')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Active subscription")
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    # Source tracking
    source = models.CharField(
        max_length=50,
        default='website',
        help_text="Where the subscriber came from"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Preferences
    preferences = models.JSONField(
        default=dict,
        help_text="Subscriber preferences: {'frequency': 'weekly', 'categories': ['devops', 'cloud']}"
    )
    
    # Engagement tracking
    emails_sent = models.PositiveIntegerField(default=0)
    emails_opened = models.PositiveIntegerField(default=0)
    links_clicked = models.PositiveIntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'is_verified', 'is_active']),
            models.Index(fields=['verification_token']),
        ]
    
    def __str__(self):
        status = "✓" if self.is_verified else "?"
        return f"{status} {self.email}"
    
    def save(self, *args, **kwargs):
        """Generate verification token on creation."""
        if not self.verification_token:
            self.verification_token = self.generate_verification_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_verification_token():
        """Generate a secure verification token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def verify_email(self):
        """Mark email as verified."""
        from django.utils import timezone
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save(update_fields=['is_verified', 'verified_at'])
    
    def unsubscribe(self):
        """Unsubscribe user."""
        from django.utils import timezone
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=['is_active', 'unsubscribed_at'])
    
    def resubscribe(self):
        """Reactivate subscription."""
        self.is_active = True
        self.unsubscribed_at = None
        self.save(update_fields=['is_active', 'unsubscribed_at'])
    
    def get_verification_url(self, request=None):
        """Get verification URL."""
        from django.urls import reverse
        path = reverse('core:newsletter_verify', kwargs={'token': self.verification_token})
        if request:
            return request.build_absolute_uri(path)
        return path
    
    def get_unsubscribe_url(self, request=None):
        """Get unsubscribe URL."""
        from django.urls import reverse
        path = reverse('core:newsletter_unsubscribe', kwargs={'token': self.verification_token})
        if request:
            return request.build_absolute_uri(path)
        return path
    
    def record_email_sent(self):
        """Record that an email was sent."""
        from django.utils import timezone
        self.emails_sent += 1
        self.last_sent_at = timezone.now()
        self.save(update_fields=['emails_sent', 'last_sent_at'])
    
    def record_email_opened(self):
        """Record that an email was opened."""
        self.emails_opened += 1
        self.save(update_fields=['emails_opened'])
    
    def record_link_clicked(self):
        """Record that a link was clicked."""
        self.links_clicked += 1
        self.save(update_fields=['links_clicked'])
    
    @property
    def open_rate(self):
        """Calculate email open rate."""
        if self.emails_sent == 0:
            return 0
        return round((self.emails_opened / self.emails_sent) * 100, 2)
    
    @property
    def click_rate(self):
        """Calculate click-through rate."""
        if self.emails_sent == 0:
            return 0
        return round((self.links_clicked / self.emails_sent) * 100, 2)


# =============================================================================
# SEARCH MODELS
# =============================================================================

class SearchQuery(models.Model):
    """Track search queries for analytics and suggestions"""
    query = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='search_queries'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Search context
    content_type = models.CharField(max_length=50, blank=True)  # 'tools', 'articles', etc.
    category = models.CharField(max_length=100, blank=True)
    sort_by = models.CharField(max_length=50, blank=True)
    
    # Results metrics
    results_count = models.PositiveIntegerField(default=0)
    clicked_result = models.JSONField(null=True, blank=True)  # Store which result was clicked
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    response_time = models.FloatField(null=True, blank=True)  # Search response time in seconds
    
    class Meta:
        db_table = 'search_queries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['query', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class SearchSuggestion(models.Model):
    """Store and manage search suggestions"""
    suggestion = models.CharField(max_length=255, unique=True, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    priority = models.PositiveIntegerField(default=1)  # Higher = more important
    
    # Usage metrics
    search_count = models.PositiveIntegerField(default=0)
    last_searched = models.DateTimeField(null=True, blank=True)
    
    # Management
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_suggestions'
        ordering = ['-priority', '-search_count', 'suggestion']
        indexes = [
            models.Index(fields=['suggestion']),
            models.Index(fields=['-priority', '-search_count']),
            models.Index(fields=['is_active', '-priority']),
        ]

    def __str__(self):
        return f"Suggestion: {self.suggestion} (priority: {self.priority})"
    
    def increment_usage(self):
        """Increment search count and update last searched"""
        self.search_count += 1
        self.last_searched = timezone.now()
        self.save(update_fields=['search_count', 'last_searched'])


class PopularSearch(models.Model):
    """Track and display popular search terms"""
    query = models.CharField(max_length=255, unique=True, db_index=True)
    search_count = models.PositiveIntegerField(default=1)
    unique_users = models.PositiveIntegerField(default=1)
    
    # Time periods
    last_week_count = models.PositiveIntegerField(default=0)
    last_month_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    first_searched = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True)
    is_trending = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'popular_searches'
        ordering = ['-search_count', '-last_searched']
        indexes = [
            models.Index(fields=['-search_count']),
            models.Index(fields=['is_trending', '-search_count']),
            models.Index(fields=['-last_searched']),
        ]

    def __str__(self):
        return f"Popular: {self.query} ({self.search_count} searches)"
    
    @classmethod
    def increment_search(cls, query, user=None):
        """Increment search count for a query"""
        popular_search, created = cls.objects.get_or_create(
            query=query,
            defaults={
                'search_count': 1,
                'unique_users': 1 if user else 0,
                'last_week_count': 1,
                'last_month_count': 1,
            }
        )
        
        if not created:
            popular_search.search_count += 1
            popular_search.last_week_count += 1
            popular_search.last_month_count += 1
            popular_search.last_searched = timezone.now()
            popular_search.save()
        
        return popular_search


class SearchAnalytics(models.Model):
    """Aggregate search analytics data"""
    date = models.DateField(unique=True)
    
    # Query metrics
    total_searches = models.PositiveIntegerField(default=0)
    unique_queries = models.PositiveIntegerField(default=0)
    unique_users = models.PositiveIntegerField(default=0)
    
    # Result metrics
    avg_results_per_search = models.FloatField(default=0)
    zero_result_searches = models.PositiveIntegerField(default=0)
    avg_response_time = models.FloatField(default=0)
    
    # Top queries (JSON field with top 10 queries for the day)
    top_queries = models.JSONField(default=list)
    
    # Filters usage
    filter_usage = models.JSONField(default=dict)  # Track which filters are used most
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_analytics'
        ordering = ['-date']

    def __str__(self):
        return f"Search Analytics: {self.date} ({self.total_searches} searches)"
