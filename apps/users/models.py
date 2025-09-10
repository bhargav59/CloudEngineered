"""
User models for CloudEngineered platform.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Professional information
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('junior', 'Junior (0-2 years)'),
            ('mid', 'Mid-level (3-5 years)'),
            ('senior', 'Senior (6-10 years)'),
            ('lead', 'Lead/Principal (10+ years)'),
        ],
        blank=True
    )
    
    # Social links
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_username = models.CharField(max_length=100, blank=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    
    # Subscription and premium features
    is_premium = models.BooleanField(default=False)
    premium_expires = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'username': self.username})
    
    def get_full_name_or_username(self):
        """Return full name if available, otherwise username."""
        full_name = self.get_full_name()
        return full_name if full_name else self.username
    
    @property
    def is_premium_active(self):
        """Check if premium subscription is active."""
        if not self.is_premium:
            return False
        if self.premium_expires is None:
            return True
        from django.utils import timezone
        return timezone.now() < self.premium_expires


class UserProfile(TimeStampedModel):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional details
    skills = models.JSONField(default=list, help_text="List of technical skills")
    interests = models.JSONField(default=list, help_text="Areas of interest")
    tools_used = models.JSONField(default=list, help_text="Tools the user has experience with")
    
    # Activity tracking
    tools_reviewed = models.PositiveIntegerField(default=0)
    articles_read = models.PositiveIntegerField(default=0)
    comments_made = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Personalization
    favorite_categories = models.JSONField(default=list)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_skill(self, skill):
        """Add a skill to user's skill list."""
        if skill not in self.skills:
            self.skills.append(skill)
            self.save(update_fields=['skills'])
    
    def add_tool_experience(self, tool_name):
        """Add a tool to user's experience list."""
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)
            self.save(update_fields=['tools_used'])


class UserActivity(TimeStampedModel):
    """
    Track user activities for analytics and personalization.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    ACTIVITY_TYPES = [
        ('view_tool', 'Viewed Tool'),
        ('view_article', 'Viewed Article'),
        ('add_comment', 'Added Comment'),
        ('add_rating', 'Added Rating'),
        ('bookmark_tool', 'Bookmarked Tool'),
        ('share_content', 'Shared Content'),
        ('search', 'Performed Search'),
    ]
    
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    object_type = models.CharField(max_length=50)  # 'tool', 'article', etc.
    object_id = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, help_text="Additional activity data")
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class UserBookmark(TimeStampedModel):
    """
    User bookmarks for tools and articles.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.CharField(
        max_length=20,
        choices=[
            ('tool', 'Tool'),
            ('article', 'Article'),
            ('comparison', 'Tool Comparison'),
        ]
    )
    object_id = models.PositiveIntegerField()
    notes = models.TextField(blank=True, help_text="Personal notes about this bookmark")
    tags = models.JSONField(default=list, help_text="Personal tags for organization")
    
    class Meta:
        verbose_name = 'User Bookmark'
        verbose_name_plural = 'User Bookmarks'
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.content_type} #{self.object_id}"


class UserPreferences(TimeStampedModel):
    """
    User preferences and settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Dashboard preferences
    dashboard_layout = models.CharField(
        max_length=20,
        choices=[
            ('grid', 'Grid View'),
            ('list', 'List View'),
            ('cards', 'Card View'),
        ],
        default='cards'
    )
    items_per_page = models.PositiveIntegerField(default=20)
    
    # Content preferences
    preferred_tool_categories = models.JSONField(default=list)
    content_difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('all', 'All Levels'),
        ],
        default='all'
    )
    
    # Notification preferences
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('never', 'Never'),
        ],
        default='weekly'
    )
    notify_new_tools = models.BooleanField(default=True)
    notify_tool_updates = models.BooleanField(default=True)
    notify_new_articles = models.BooleanField(default=True)
    notify_comments = models.BooleanField(default=True)
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', 'Public'),
            ('authenticated', 'Authenticated Users Only'),
            ('private', 'Private'),
        ],
        default='public'
    )
    show_activity = models.BooleanField(default=True)
    show_bookmarks = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


class PremiumFeature(TimeStampedModel):
    """
    Define premium features available to subscribers.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    feature_key = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    required_plan = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic Premium'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='basic'
    )
    
    class Meta:
        verbose_name = 'Premium Feature'
        verbose_name_plural = 'Premium Features'
    
    def __str__(self):
        return self.name


class UserSubscription(TimeStampedModel):
    """
    Track user subscription details.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    
    SUBSCRIPTION_PLANS = [
        ('free', 'Free'),
        ('basic', 'Basic Premium'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    
    plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='free')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    
    # Payment information (for future integration)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    @property
    def is_premium(self):
        """Check if user has any premium plan."""
        return self.plan != 'free' and self.is_active
    
    def has_feature(self, feature_key):
        """Check if user's plan includes a specific feature."""
        if not self.is_premium:
            return False
        
        try:
            feature = PremiumFeature.objects.get(feature_key=feature_key, is_active=True)
            plan_hierarchy = ['basic', 'pro', 'enterprise']
            user_plan_level = plan_hierarchy.index(self.plan)
            required_plan_level = plan_hierarchy.index(feature.required_plan)
            return user_plan_level >= required_plan_level
        except (PremiumFeature.DoesNotExist, ValueError):
            return False
