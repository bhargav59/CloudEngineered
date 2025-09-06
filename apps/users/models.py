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
    # bookmarked_tools = models.ManyToManyField(
    #     'tools.Tool', 
    #     blank=True, 
    #     related_name='bookmarked_by'
    # )
    
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
