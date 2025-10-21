"""
Premium Comparison Reports - Detailed AI-generated reports ($29-$99)
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class ReportTemplate(models.Model):
    """Templates for different types of premium reports"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Report details
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('tool_comparison', 'Tool Comparison Report'),
            ('tech_stack', 'Tech Stack Recommendation'),
            ('migration_plan', 'Migration Planning Report'),
            ('cost_analysis', 'Cost Analysis Report'),
            ('security_audit', 'Security Audit Report'),
            ('performance_benchmark', 'Performance Benchmark')
        ],
        default='tool_comparison'
    )
    
    # Pricing tiers
    price_basic = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('29.00'),
        help_text="Basic report price"
    )
    price_standard = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('59.00'),
        help_text="Standard report with more details"
    )
    price_premium = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('99.00'),
        help_text="Premium report with consultation call"
    )
    
    # What's included at each tier
    basic_features = models.JSONField(default=list, help_text="Features in basic tier")
    standard_features = models.JSONField(default=list, help_text="Features in standard tier")
    premium_features = models.JSONField(default=list, help_text="Features in premium tier")
    
    # Report structure
    sections = models.JSONField(
        default=list, 
        help_text="List of section templates for the report"
    )
    required_inputs = models.JSONField(
        default=list,
        help_text="Required user inputs for report generation"
    )
    
    # AI generation settings
    ai_prompts = models.JSONField(
        default=dict,
        help_text="AI prompts for each section"
    )
    generation_time_minutes = models.IntegerField(
        default=15,
        help_text="Estimated time to generate report"
    )
    
    # Display
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    sample_url = models.URLField(blank=True, help_text="Link to sample report")
    
    # Stats
    total_purchases = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class PremiumReport(models.Model):
    """Individual premium report purchases"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='premium_reports')
    template = models.ForeignKey(ReportTemplate, on_delete=models.PROTECT, related_name='reports')
    
    # Purchase details
    tier = models.CharField(
        max_length=20,
        choices=[
            ('basic', 'Basic - $29'),
            ('standard', 'Standard - $59'),
            ('premium', 'Premium - $99')
        ],
        default='basic'
    )
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Payment info
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Payment'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Report generation
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Input'),
            ('generating', 'Generating'),
            ('ready', 'Ready'),
            ('failed', 'Failed'),
            ('expired', 'Expired')
        ],
        default='pending'
    )
    
    # User inputs
    user_inputs = models.JSONField(
        default=dict,
        help_text="User-provided information for report customization"
    )
    
    # Generated content
    report_data = models.JSONField(
        default=dict,
        help_text="Generated report content"
    )
    pdf_file = models.FileField(
        upload_to='premium_reports/',
        blank=True,
        null=True
    )
    
    # Report metadata
    title = models.CharField(max_length=300)
    executive_summary = models.TextField(blank=True)
    page_count = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    
    # Access control
    download_count = models.IntegerField(default=0)
    max_downloads = models.IntegerField(default=10)
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Report access expires after this date"
    )
    share_url = models.CharField(max_length=200, blank=True, unique=True)
    
    # Premium tier extras
    consultation_scheduled = models.BooleanField(default=False)
    consultation_date = models.DateTimeField(null=True, blank=True)
    consultation_notes = models.TextField(blank=True)
    
    # Feedback
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback = models.TextField(blank=True)
    
    # Timestamps
    generation_started = models.DateTimeField(null=True, blank=True)
    generation_completed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_status', 'status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def can_download(self):
        """Check if user can still download the report"""
        if self.status != 'ready':
            return False
        if self.download_count >= self.max_downloads:
            return False
        if self.expiry_date and timezone.now() > self.expiry_date:
            return False
        return True

    def record_download(self):
        """Record a download"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class ReportPurchaseAnalytics(models.Model):
    """Track analytics for report purchases"""
    report = models.OneToOneField(
        PremiumReport,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    # Traffic source
    referrer = models.URLField(blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    
    # User behavior
    time_on_sales_page_seconds = models.IntegerField(default=0)
    viewed_samples = models.BooleanField(default=False)
    viewed_testimonials = models.BooleanField(default=False)
    
    # Conversion funnel
    funnel_stage_reached = models.CharField(
        max_length=50,
        choices=[
            ('landing', 'Landed on Page'),
            ('form_started', 'Started Form'),
            ('form_completed', 'Completed Form'),
            ('payment_initiated', 'Payment Initiated'),
            ('payment_completed', 'Payment Completed')
        ],
        default='landing'
    )
    
    # A/B testing
    test_variant = models.CharField(max_length=20, default='A')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.report.title}"
