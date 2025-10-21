"""
Freemium SaaS Features - Custom tool recommendations, team collaboration, etc.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class TechStackProfile(models.Model):
    """User's technology stack profile for custom recommendations"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tech_stack_profile'
    )
    
    # Company info
    company_name = models.CharField(max_length=200, blank=True)
    industry = models.CharField(
        max_length=100,
        choices=[
            ('fintech', 'Financial Technology'),
            ('healthcare', 'Healthcare'),
            ('ecommerce', 'E-commerce'),
            ('saas', 'SaaS'),
            ('enterprise', 'Enterprise Software'),
            ('startup', 'Startup'),
            ('agency', 'Agency'),
            ('education', 'Education'),
            ('gaming', 'Gaming'),
            ('other', 'Other')
        ],
        blank=True
    )
    team_size = models.CharField(
        max_length=20,
        choices=[
            ('solo', 'Solo Developer'),
            ('2-5', '2-5 people'),
            ('6-10', '6-10 people'),
            ('11-50', '11-50 people'),
            ('51-200', '51-200 people'),
            ('201+', '201+ people')
        ],
        blank=True
    )
    
    # Current stack
    programming_languages = models.JSONField(
        default=list,
        help_text="Languages: Python, JavaScript, Go, Java, etc."
    )
    frameworks = models.JSONField(
        default=list,
        help_text="Frameworks: Django, React, Spring Boot, etc."
    )
    cloud_providers = models.JSONField(
        default=list,
        help_text="AWS, GCP, Azure, Digital Ocean, etc."
    )
    databases = models.JSONField(
        default=list,
        help_text="PostgreSQL, MongoDB, MySQL, etc."
    )
    current_tools = models.JSONField(
        default=dict,
        help_text="Current DevOps tools by category"
    )
    
    # Deployment & infrastructure
    deployment_frequency = models.CharField(
        max_length=50,
        choices=[
            ('multiple_daily', 'Multiple times per day'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly')
        ],
        blank=True
    )
    infrastructure_type = models.CharField(
        max_length=50,
        choices=[
            ('cloud', 'Cloud-native'),
            ('hybrid', 'Hybrid Cloud'),
            ('on_premise', 'On-premise'),
            ('containerized', 'Containerized'),
            ('serverless', 'Serverless'),
            ('mixed', 'Mixed')
        ],
        blank=True
    )
    
    # Requirements & preferences
    compliance_requirements = models.JSONField(
        default=list,
        help_text="SOC2, HIPAA, GDPR, PCI-DSS, etc."
    )
    budget_constraints = models.CharField(
        max_length=50,
        choices=[
            ('bootstrap', 'Bootstrap/Minimal'),
            ('moderate', 'Moderate'),
            ('enterprise', 'Enterprise'),
            ('unlimited', 'Budget not a constraint')
        ],
        blank=True
    )
    priorities = models.JSONField(
        default=list,
        help_text="speed, cost, security, scalability, ease_of_use, etc."
    )
    
    # Pain points
    current_challenges = models.JSONField(
        default=list,
        help_text="What problems are you trying to solve?"
    )
    goals = models.JSONField(
        default=list,
        help_text="What are you trying to achieve?"
    )
    
    # Profile completeness
    is_complete = models.BooleanField(default=False)
    completion_percentage = models.IntegerField(default=0)
    
    # Recommendations
    last_recommendation_date = models.DateTimeField(null=True, blank=True)
    recommendation_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Tech Stack Profile"

    def calculate_completion(self):
        """Calculate profile completion percentage"""
        required_fields = [
            self.industry,
            self.team_size,
            self.programming_languages,
            self.frameworks,
            self.cloud_providers,
            self.deployment_frequency,
            self.infrastructure_type,
            self.priorities
        ]
        completed = sum(1 for field in required_fields if field)
        percentage = int((completed / len(required_fields)) * 100)
        
        self.completion_percentage = percentage
        self.is_complete = percentage >= 80
        self.save(update_fields=['completion_percentage', 'is_complete'])
        return percentage


class CustomRecommendation(models.Model):
    """AI-generated custom tool recommendations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_recommendations'
    )
    tech_stack_profile = models.ForeignKey(
        TechStackProfile,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Recommendation details
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    # Recommended tools
    recommended_tools = models.JSONField(
        default=list,
        help_text="List of recommended tools with reasons"
    )
    alternative_tools = models.JSONField(
        default=list,
        help_text="Alternative options"
    )
    tools_to_replace = models.JSONField(
        default=list,
        help_text="Current tools that should be replaced"
    )
    
    # Implementation plan
    implementation_phases = models.JSONField(
        default=list,
        help_text="Step-by-step implementation plan"
    )
    estimated_implementation_time = models.CharField(max_length=100)
    estimated_cost = models.JSONField(
        default=dict,
        help_text="Cost breakdown by tool/phase"
    )
    
    # ROI & benefits
    expected_benefits = models.JSONField(default=list)
    roi_analysis = models.JSONField(
        default=dict,
        help_text="Return on investment analysis"
    )
    risk_assessment = models.JSONField(
        default=dict,
        help_text="Potential risks and mitigation strategies"
    )
    
    # Access control
    is_premium = models.BooleanField(
        default=False,
        help_text="Premium recommendations require payment"
    )
    access_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free Basic'),
            ('pro', 'Pro User'),
            ('enterprise', 'Enterprise')
        ],
        default='free'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('generating', 'Generating'),
            ('ready', 'Ready'),
            ('archived', 'Archived')
        ],
        default='draft'
    )
    
    # Interaction
    viewed_count = models.IntegerField(default=0)
    shared_count = models.IntegerField(default=0)
    tools_adopted = models.JSONField(
        default=list,
        help_text="Tools user actually adopted"
    )
    
    # Feedback
    was_helpful = models.BooleanField(null=True, blank=True)
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback = models.TextField(blank=True)
    
    # Generation metadata
    ai_model_used = models.CharField(max_length=100, blank=True)
    generation_time_seconds = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Recommendations expire and need refresh"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['is_premium', 'access_tier']),
        ]

    def __str__(self):
        return f"{self.title} for {self.user.username}"


class Team(models.Model):
    """Team collaboration feature"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_teams'
    )
    members = models.ManyToManyField(
        User,
        through='TeamMembership',
        related_name='teams'
    )
    
    # Team settings
    tech_stack = models.ForeignKey(
        TechStackProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teams'
    )
    
    # Subscription
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free (up to 3 members)'),
            ('pro', 'Pro (up to 10 members)'),
            ('enterprise', 'Enterprise (unlimited)')
        ],
        default='free'
    )
    max_members = models.IntegerField(default=3)
    
    # Features enabled
    features_enabled = models.JSONField(
        default=dict,
        help_text="Which features are enabled for this team"
    )
    
    # Shared resources
    shared_reports = models.ManyToManyField(
        'monetization.PremiumReport',
        blank=True,
        related_name='shared_with_teams'
    )
    shared_recommendations = models.ManyToManyField(
        CustomRecommendation,
        blank=True,
        related_name='shared_with_teams'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Current number of members"""
        return self.members.count()

    def can_add_member(self):
        """Check if team can add more members"""
        return self.member_count < self.max_members


class TeamMembership(models.Model):
    """Team membership with roles"""
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    role = models.CharField(
        max_length=20,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'),
            ('member', 'Member'),
            ('viewer', 'Viewer')
        ],
        default='member'
    )
    
    # Permissions
    can_invite = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    can_create_reports = models.BooleanField(default=True)
    can_view_analytics = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('invited', 'Invited'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('left', 'Left')
        ],
        default='invited'
    )
    
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['team', 'user']
        indexes = [
            models.Index(fields=['team', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.team.name} ({self.role})"


class IntegrationRoadmap(models.Model):
    """Tool integration roadmaps - premium feature"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='integration_roadmaps'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='integration_roadmaps'
    )
    
    # Roadmap details
    title = models.CharField(max_length=300)
    description = models.TextField()
    
    # Tools to integrate
    tools = models.ManyToManyField(
        'tools.Tool',
        related_name='integration_roadmaps'
    )
    integration_points = models.JSONField(
        default=list,
        help_text="How tools will integrate with each other"
    )
    
    # Timeline
    phases = models.JSONField(
        default=list,
        help_text="Implementation phases with timelines"
    )
    total_duration_weeks = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    
    # Resources
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    required_skills = models.JSONField(default=list)
    external_consultants_needed = models.BooleanField(default=False)
    
    # Dependencies
    dependencies = models.JSONField(
        default=list,
        help_text="Prerequisites and dependencies"
    )
    blockers = models.JSONField(
        default=list,
        help_text="Current blockers"
    )
    
    # Progress tracking
    current_phase = models.IntegerField(default=0)
    completion_percentage = models.IntegerField(default=0)
    milestones_completed = models.JSONField(default=list)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('planned', 'Planned'),
            ('in_progress', 'In Progress'),
            ('on_hold', 'On Hold'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ],
        default='draft'
    )
    
    # Access control (premium feature)
    is_premium = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CostCalculator(models.Model):
    """Tool cost calculations - premium feature"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cost_calculations'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cost_calculations'
    )
    
    # Calculation details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Tools being calculated
    tools = models.ManyToManyField(
        'tools.Tool',
        related_name='cost_calculations'
    )
    
    # Usage parameters
    team_size = models.IntegerField(default=5)
    monthly_active_users = models.IntegerField(default=100)
    api_calls_per_month = models.IntegerField(default=10000)
    storage_gb = models.IntegerField(default=100)
    bandwidth_gb = models.IntegerField(default=500)
    
    # Custom usage metrics
    custom_metrics = models.JSONField(
        default=dict,
        help_text="Tool-specific usage metrics"
    )
    
    # Cost breakdown
    tool_costs = models.JSONField(
        default=dict,
        help_text="Individual tool costs"
    )
    total_monthly_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_yearly_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Comparison scenarios
    scenarios = models.JSONField(
        default=list,
        help_text="Different tool combination scenarios"
    )
    recommended_scenario = models.IntegerField(null=True, blank=True)
    
    # Savings analysis
    potential_savings = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    savings_opportunities = models.JSONField(default=list)
    
    # Hidden costs identified
    hidden_costs = models.JSONField(
        default=list,
        help_text="Often-overlooked costs"
    )
    
    # Access control
    is_premium = models.BooleanField(default=True)
    
    # Sharing
    is_shared = models.BooleanField(default=False)
    share_url = models.CharField(max_length=200, blank=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - ${self.total_monthly_cost}/mo"

    def calculate_costs(self):
        """Recalculate costs based on current parameters"""
        # This would be implemented with actual pricing logic
        pass
