from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SearchQuery(models.Model):
    """Track search queries for analytics and suggestions"""
    query = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
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


class SearchFilter(models.Model):
    """Define available search filters and facets"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    filter_type = models.CharField(max_length=50, choices=[
        ('category', 'Category'),
        ('content_type', 'Content Type'),
        ('tag', 'Tag'),
        ('date_range', 'Date Range'),
        ('custom', 'Custom'),
    ])
    
    # Filter configuration
    values = models.JSONField(default=list)  # Available filter values
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_filters'
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"Filter: {self.name} ({self.filter_type})"


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
