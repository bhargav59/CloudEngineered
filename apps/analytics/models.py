from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.db.models import JSONField
from apps.core.models import TimeStampedModel
import uuid

User = get_user_model()


class AnalyticsEvent(TimeStampedModel):
    """Track user interactions and events across the platform"""
    
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('tool_view', 'Tool View'),
        ('article_view', 'Article View'),
        ('comparison_view', 'Comparison View'),
        ('search', 'Search'),
        ('bookmark_add', 'Bookmark Added'),
        ('bookmark_remove', 'Bookmark Removed'),
        ('user_signup', 'User Signup'),
        ('user_login', 'User Login'),
        ('subscription_upgrade', 'Subscription Upgrade'),
        ('subscription_downgrade', 'Subscription Downgrade'),
        ('email_subscribe', 'Email Subscribe'),
        ('tool_rating', 'Tool Rating'),
        ('comment_add', 'Comment Added'),
        ('share_content', 'Content Shared'),
        ('download', 'Download'),
        ('api_call', 'API Call'),
        ('export_data', 'Data Export'),
        ('custom', 'Custom Event'),
    ]
    
    # Event identification
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    event_name = models.CharField(max_length=200, blank=True)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True, db_index=True)
    anonymous_id = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Content tracking (generic foreign key for any model)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    page_url = models.URLField(blank=True)
    
    # Event data
    properties = JSONField(default=dict, blank=True)  # Custom event properties
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Event value (e.g., revenue)
    
    # Timing
    duration = models.PositiveIntegerField(null=True, blank=True)  # Duration in seconds
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            # Core event tracking
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['session_id', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
            
            # Performance optimization
            models.Index(fields=['timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            
            # Analytics queries
            models.Index(fields=['event_type', 'user', 'timestamp']),
            models.Index(fields=['content_type', 'object_id', 'timestamp']),
            models.Index(fields=['user', 'event_type']),
            
            # Time-based aggregations
            models.Index(fields=['-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.user or 'Anonymous'} - {self.timestamp}"


class PageView(TimeStampedModel):
    """Detailed page view tracking"""
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    
    # Page information
    page_url = models.URLField()
    page_title = models.CharField(max_length=500, blank=True)
    page_type = models.CharField(max_length=50, blank=True)  # home, tool, article, etc.
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Device and browser info
    device_type = models.CharField(max_length=50, blank=True)  # mobile, tablet, desktop
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    # Engagement metrics
    time_on_page = models.PositiveIntegerField(null=True, blank=True)  # seconds
    scroll_depth = models.PositiveIntegerField(null=True, blank=True)  # percentage
    bounce = models.BooleanField(default=False)
    
    # Geographic data
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # UTM parameters
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    utm_term = models.CharField(max_length=100, blank=True)
    utm_content = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Core page view tracking
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['page_type', 'created_at']),
            models.Index(fields=['country', 'created_at']),
            
            # Performance optimization
            models.Index(fields=['page_url']),
            models.Index(fields=['page_type']),
            models.Index(fields=['device_type']),
            models.Index(fields=['browser']),
            models.Index(fields=['country']),
            
            # UTM tracking
            models.Index(fields=['utm_source', 'created_at']),
            models.Index(fields=['utm_medium', 'created_at']),
            models.Index(fields=['utm_campaign', 'created_at']),
            
            # Analytics queries
            models.Index(fields=['page_type', 'country', 'created_at']),
            models.Index(fields=['device_type', 'browser', 'created_at']),
            models.Index(fields=['user', 'page_type']),
            
            # Time-based queries
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.page_url} - {self.user or 'Anonymous'} - {self.created_at}"


class ContentMetrics(TimeStampedModel):
    """Track metrics for specific content (tools, articles, etc.)"""
    
    # Content reference
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Date for aggregation
    date = models.DateField(db_index=True)
    
    # View metrics
    views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    authenticated_views = models.PositiveIntegerField(default=0)
    anonymous_views = models.PositiveIntegerField(default=0)
    
    # Engagement metrics
    average_time_on_page = models.PositiveIntegerField(default=0)  # seconds
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    scroll_depth_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # percentage
    
    # Social metrics
    shares = models.PositiveIntegerField(default=0)
    bookmarks = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    ratings = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Conversion metrics
    conversions = models.PositiveIntegerField(default=0)  # Any tracked conversion
    click_through_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Geographic data
    top_countries = JSONField(default=list, blank=True)  # List of country data
    top_cities = JSONField(default=list, blank=True)  # List of city data
    
    # Traffic sources
    traffic_sources = JSONField(default=dict, blank=True)  # Source breakdown
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'date']),
            models.Index(fields=['date', 'views']),
        ]
    
    def __str__(self):
        return f"{self.content_object} - {self.date} - {self.views} views"


class UserMetrics(TimeStampedModel):
    """Track user-specific metrics and behavior"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    
    # Activity metrics
    sessions = models.PositiveIntegerField(default=0)
    page_views = models.PositiveIntegerField(default=0)
    time_on_site = models.PositiveIntegerField(default=0)  # total seconds
    
    # Content engagement
    tools_viewed = models.PositiveIntegerField(default=0)
    articles_read = models.PositiveIntegerField(default=0)
    comparisons_made = models.PositiveIntegerField(default=0)
    searches_performed = models.PositiveIntegerField(default=0)
    
    # Actions taken
    bookmarks_added = models.PositiveIntegerField(default=0)
    comments_posted = models.PositiveIntegerField(default=0)
    content_shared = models.PositiveIntegerField(default=0)
    ratings_given = models.PositiveIntegerField(default=0)
    
    # Premium features (if applicable)
    premium_features_used = models.PositiveIntegerField(default=0)
    api_calls_made = models.PositiveIntegerField(default=0)
    
    # Content creation (if applicable)
    content_created = models.PositiveIntegerField(default=0)
    content_updated = models.PositiveIntegerField(default=0)
    
    # Device usage
    mobile_sessions = models.PositiveIntegerField(default=0)
    desktop_sessions = models.PositiveIntegerField(default=0)
    tablet_sessions = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'page_views']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.page_views} views"


class SearchMetrics(TimeStampedModel):
    """Track search queries and results"""
    
    # Search query
    query = models.CharField(max_length=500, db_index=True)
    normalized_query = models.CharField(max_length=500, db_index=True)  # lowercase, trimmed
    
    # User context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    
    # Search context
    search_type = models.CharField(max_length=50, default='general')  # general, tools, articles
    filters_applied = JSONField(default=dict, blank=True)
    
    # Results
    results_count = models.PositiveIntegerField(default=0)
    results_clicked = models.PositiveIntegerField(default=0)
    first_click_position = models.PositiveIntegerField(null=True, blank=True)
    
    # Performance
    search_duration = models.PositiveIntegerField(null=True, blank=True)  # milliseconds
    
    # Follow-up actions
    refined_search = models.BooleanField(default=False)
    resulted_in_conversion = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['normalized_query', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['search_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"'{self.query}' - {self.results_count} results - {self.created_at}"


class PerformanceMetrics(TimeStampedModel):
    """Track system performance metrics"""
    
    METRIC_TYPES = [
        ('page_load', 'Page Load Time'),
        ('api_response', 'API Response Time'),
        ('search_performance', 'Search Performance'),
        ('database_query', 'Database Query Time'),
        ('cache_hit_rate', 'Cache Hit Rate'),
        ('error_rate', 'Error Rate'),
        ('uptime', 'System Uptime'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, db_index=True)
    metric_name = models.CharField(max_length=200)
    
    # Metric values
    value = models.DecimalField(max_digits=15, decimal_places=6)
    unit = models.CharField(max_length=20)  # ms, seconds, percentage, etc.
    
    # Context
    endpoint = models.CharField(max_length=500, blank=True)  # URL or API endpoint
    user_agent = models.CharField(max_length=500, blank=True)
    
    # Additional data
    metadata = JSONField(default=dict, blank=True)
    
    # Aggregation date
    date = models.DateField(db_index=True)
    hour = models.PositiveIntegerField()  # 0-23 for hourly aggregation
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['metric_type', 'date']),
            models.Index(fields=['endpoint', 'date']),
            models.Index(fields=['date', 'hour']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.value}{self.unit} - {self.date}"
