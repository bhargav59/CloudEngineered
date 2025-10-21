"""
Monetization Models - Affiliate Marketing, Premium Subscriptions, Sponsored Content
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

# Import new model modules
from .premium_reports import ReportTemplate, PremiumReport, ReportPurchaseAnalytics
from .consulting import ConsultingPackage, ConsultingBooking, ConsultingResource, ConsultantAvailability
from .freemium import TechStackProfile, CustomRecommendation, Team, TeamMembership, IntegrationRoadmap, CostCalculator

User = get_user_model()


class AffiliateNetwork(models.Model):
    """Affiliate networks like ShareASale, CJ, Amazon Associates"""
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField()
    api_key = models.CharField(max_length=255, blank=True)
    api_secret = models.CharField(max_length=255, blank=True)
    cookie_duration_days = models.IntegerField(default=30)
    commission_structure = models.JSONField(default=dict, help_text="Commission rates structure")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AffiliateProgram(models.Model):
    """Individual affiliate programs for specific tools or vendors"""
    tool = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, related_name='affiliate_programs')
    network = models.ForeignKey(AffiliateNetwork, on_delete=models.SET_NULL, null=True, blank=True)
    program_name = models.CharField(max_length=200)
    program_id = models.CharField(max_length=100, blank=True)
    
    # Commission details
    commission_type = models.CharField(
        max_length=20,
        choices=[
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed Amount'),
            ('tiered', 'Tiered'),
            ('hybrid', 'Hybrid')
        ],
        default='percentage'
    )
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage or fixed amount"
    )
    commission_tiers = models.JSONField(default=dict, blank=True, help_text="For tiered commission structures")
    
    # Tracking
    cookie_duration_days = models.IntegerField(default=30)
    average_conversion_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Percentage"
    )
    average_commission_per_sale = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    # Metadata
    terms_url = models.URLField(blank=True)
    payout_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('50.00'))
    payout_frequency = models.CharField(max_length=50, default='monthly')
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', 'program_name']
        unique_together = ['tool', 'network']

    def __str__(self):
        return f"{self.program_name} - {self.tool.name}"


class AffiliateLink(models.Model):
    """Individual affiliate tracking links"""
    program = models.ForeignKey(AffiliateProgram, on_delete=models.CASCADE, related_name='links')
    tool = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, related_name='affiliate_links')
    
    # Link details
    link_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text Link'),
            ('button', 'Button'),
            ('banner', 'Banner'),
            ('widget', 'Widget')
        ],
        default='text'
    )
    placement = models.CharField(
        max_length=50,
        choices=[
            ('review_header', 'Review Header'),
            ('review_body', 'Review Body'),
            ('review_footer', 'Review Footer'),
            ('sidebar', 'Sidebar'),
            ('comparison_table', 'Comparison Table'),
            ('cta_button', 'CTA Button')
        ],
        default='review_body'
    )
    
    # URLs
    destination_url = models.URLField(help_text="Original product URL")
    tracking_url = models.URLField(help_text="Affiliate tracking URL")
    short_url = models.CharField(max_length=200, blank=True, help_text="Shortened URL for cleaner display")
    
    # Tracking parameters
    tracking_id = models.CharField(max_length=100, blank=True)
    campaign_name = models.CharField(max_length=100, blank=True)
    utm_source = models.CharField(max_length=50, default='cloudengineered')
    utm_medium = models.CharField(max_length=50, default='affiliate')
    utm_campaign = models.CharField(max_length=100, blank=True)
    custom_parameters = models.JSONField(default=dict, blank=True)
    
    # Performance tracking
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    revenue_generated = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # A/B Testing
    variant = models.CharField(max_length=10, default='A', help_text="A/B test variant")
    is_control = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_nofollow = models.BooleanField(default=True, help_text="Add nofollow attribute")
    is_sponsored = models.BooleanField(default=True, help_text="Add sponsored attribute")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_clicked = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tool', 'is_active']),
            models.Index(fields=['tracking_id']),
        ]

    def __str__(self):
        return f"{self.tool.name} - {self.placement}"

    @property
    def conversion_rate(self):
        """Calculate conversion rate"""
        if self.clicks == 0:
            return Decimal('0.00')
        return Decimal(self.conversions / self.clicks * 100).quantize(Decimal('0.01'))

    def record_click(self):
        """Record a click on this affiliate link"""
        self.clicks += 1
        self.last_clicked = timezone.now()
        self.save(update_fields=['clicks', 'last_clicked'])


class Commission(models.Model):
    """Track affiliate commissions earned"""
    link = models.ForeignKey(AffiliateLink, on_delete=models.CASCADE, related_name='commissions')
    program = models.ForeignKey(AffiliateProgram, on_delete=models.CASCADE, related_name='commissions')
    
    # Transaction details
    transaction_id = models.CharField(max_length=100, unique=True)
    transaction_date = models.DateTimeField()
    
    # Financial details
    order_value = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('rejected', 'Rejected'),
            ('reversed', 'Reversed')
        ],
        default='pending'
    )
    
    # Payout tracking
    payout_date = models.DateField(null=True, blank=True)
    payout_method = models.CharField(max_length=50, blank=True)
    payout_reference = models.CharField(max_length=100, blank=True)
    
    # Metadata
    customer_id = models.CharField(max_length=100, blank=True)
    product_info = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['status', 'transaction_date']),
            models.Index(fields=['program', 'status']),
        ]

    def __str__(self):
        return f"{self.transaction_id} - ${self.commission_amount}"


class PremiumTier(models.Model):
    """Premium subscription tiers"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(default=0, help_text="Annual discount percentage")
    
    # Features
    features = models.JSONField(default=list, help_text="List of features included")
    limits = models.JSONField(default=dict, help_text="Feature limits (API calls, downloads, etc.)")
    
    # Access levels
    access_level = models.IntegerField(default=1, help_text="Higher = more access")
    max_team_members = models.IntegerField(default=1)
    
    # Display
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    badge_text = models.CharField(max_length=50, blank=True, help_text="E.g., 'Most Popular'")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price_monthly']

    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/mo"


class PremiumSubscription(models.Model):
    """User premium subscriptions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_subscriptions')
    tier = models.ForeignKey(PremiumTier, on_delete=models.PROTECT, related_name='subscriptions')
    
    # Subscription details
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('canceled', 'Canceled'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
            ('trial', 'Trial')
        ],
        default='trial'
    )
    
    # Billing
    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly')
        ],
        default='monthly'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    # Payment integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    # Metadata
    referral_code = models.CharField(max_length=50, blank=True)
    discount_code = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['stripe_subscription_id']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.tier.name} ({self.status})"

    @property
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and (not self.end_date or self.end_date > timezone.now())

    @property
    def days_until_renewal(self):
        """Days until next billing"""
        if self.next_billing_date:
            delta = self.next_billing_date - timezone.now()
            return delta.days
        return None


class SponsoredContent(models.Model):
    """Sponsored content and tool placements"""
    tool = models.ForeignKey('tools.Tool', on_delete=models.CASCADE, related_name='sponsored_content')
    article = models.ForeignKey('content.Article', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Sponsor details
    sponsor_name = models.CharField(max_length=200)
    sponsor_contact_email = models.EmailField()
    sponsor_company = models.CharField(max_length=200, blank=True)
    
    # Content details
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('review', 'Sponsored Review'),
            ('comparison', 'Sponsored Comparison'),
            ('featured', 'Featured Placement'),
            ('banner', 'Banner Ad'),
            ('newsletter', 'Newsletter Sponsorship'),
            ('webinar', 'Webinar Sponsorship')
        ],
        default='featured'
    )
    placement = models.CharField(
        max_length=50,
        choices=[
            ('homepage_hero', 'Homepage Hero'),
            ('sidebar', 'Sidebar'),
            ('article_top', 'Article Top'),
            ('article_inline', 'Article Inline'),
            ('comparison_featured', 'Comparison Featured'),
            ('newsletter', 'Newsletter')
        ],
        default='sidebar'
    )
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    billing_frequency = models.CharField(max_length=20, default='one-time')
    
    # Campaign details
    campaign_start = models.DateTimeField()
    campaign_end = models.DateTimeField()
    impressions_target = models.IntegerField(default=0)
    clicks_target = models.IntegerField(default=0)
    
    # Actual performance
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    
    # Content
    disclosure_text = models.TextField(
        default="This content is sponsored by {sponsor}",
        help_text="Disclosure text for sponsored content"
    )
    custom_content = models.JSONField(default=dict, blank=True, help_text="Custom content blocks")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled')
        ],
        default='draft'
    )
    is_approved = models.BooleanField(default=False)
    
    # Metadata
    contract_reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-campaign_start']
        indexes = [
            models.Index(fields=['status', 'campaign_start']),
            models.Index(fields=['tool', 'status']),
        ]

    def __str__(self):
        return f"{self.sponsor_name} - {self.tool.name} ({self.content_type})"

    @property
    def is_active(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        return (
            self.status == 'active' and 
            self.campaign_start <= now <= self.campaign_end
        )

    @property
    def days_remaining(self):
        """Days remaining in campaign"""
        if self.campaign_end:
            delta = self.campaign_end - timezone.now()
            return max(0, delta.days)
        return 0
