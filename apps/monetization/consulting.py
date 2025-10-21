"""
Consulting Services - DevOps Tool Selection Consulting
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class ConsultingPackage(models.Model):
    """Different consulting service packages"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    # Package details
    package_type = models.CharField(
        max_length=50,
        choices=[
            ('discovery', 'Discovery Call - 30 min'),
            ('strategy', 'Strategy Session - 1 hour'),
            ('deep_dive', 'Deep Dive - 2 hours'),
            ('workshop', 'Team Workshop - Half Day'),
            ('comprehensive', 'Comprehensive Assessment - Full Day'),
            ('ongoing', 'Ongoing Retainer')
        ],
        default='strategy'
    )
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="For retainer packages"
    )
    currency = models.CharField(max_length=3, default='USD')
    
    # Duration
    duration_hours = models.DecimalField(max_digits=4, decimal_places=1)
    preparation_time_hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('1.0')
    )
    
    # What's included
    deliverables = models.JSONField(
        default=list,
        help_text="List of deliverables included"
    )
    features = models.JSONField(default=list, help_text="Features of this package")
    
    # Requirements
    prerequisites = models.JSONField(
        default=list,
        help_text="What client needs to provide"
    )
    ideal_for = models.JSONField(
        default=list,
        help_text="Ideal client scenarios"
    )
    
    # Availability
    max_bookings_per_month = models.IntegerField(default=4)
    advance_booking_days = models.IntegerField(
        default=7,
        help_text="Minimum days notice required"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    # Stats
    total_bookings = models.IntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price']

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def bookings_this_month(self):
        """Get count of bookings for current month"""
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.consultations.filter(
            scheduled_date__gte=month_start,
            status__in=['scheduled', 'completed']
        ).count()

    @property
    def is_available(self):
        """Check if package is available for booking this month"""
        return (
            self.is_active and 
            self.bookings_this_month < self.max_bookings_per_month
        )


class ConsultingBooking(models.Model):
    """Individual consulting bookings"""
    package = models.ForeignKey(
        ConsultingPackage,
        on_delete=models.PROTECT,
        related_name='consultations'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consulting_bookings'
    )
    
    # Contact information
    company_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50, blank=True)
    company_size = models.CharField(
        max_length=50,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('501+', '501+ employees')
        ],
        default='11-50'
    )
    
    # Booking details
    status = models.CharField(
        max_length=20,
        choices=[
            ('inquiry', 'Initial Inquiry'),
            ('pending_payment', 'Pending Payment'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
            ('rescheduled', 'Rescheduled')
        ],
        default='inquiry'
    )
    
    # Scheduling
    preferred_dates = models.JSONField(
        default=list,
        help_text="List of preferred date/time slots"
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    meeting_link = models.URLField(blank=True, help_text="Zoom/Meet link")
    
    # Project details
    project_description = models.TextField(
        help_text="What are you trying to achieve?"
    )
    current_tech_stack = models.JSONField(
        default=list,
        help_text="Current tools and technologies"
    )
    pain_points = models.JSONField(
        default=list,
        help_text="Current challenges"
    )
    goals = models.JSONField(
        default=list,
        help_text="Desired outcomes"
    )
    budget_range = models.CharField(
        max_length=50,
        choices=[
            ('0-10k', '$0-$10,000'),
            ('10k-50k', '$10,000-$50,000'),
            ('50k-100k', '$50,000-$100,000'),
            ('100k-500k', '$100,000-$500,000'),
            ('500k+', '$500,000+'),
            ('flexible', 'Flexible')
        ],
        default='flexible'
    )
    timeline = models.CharField(
        max_length=50,
        choices=[
            ('immediate', 'Immediate (< 1 month)'),
            ('short', 'Short term (1-3 months)'),
            ('medium', 'Medium term (3-6 months)'),
            ('long', 'Long term (6+ months)'),
            ('exploratory', 'Just exploring')
        ],
        default='medium'
    )
    
    # Payment
    price_quoted = models.DecimalField(max_digits=10, decimal_places=2)
    price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
            ('partial', 'Partially Paid')
        ],
        default='pending'
    )
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    
    # Deliverables
    assessment_report = models.FileField(
        upload_to='consulting/reports/',
        blank=True,
        null=True
    )
    recommendations = models.JSONField(
        default=dict,
        help_text="Tool and strategy recommendations"
    )
    implementation_roadmap = models.JSONField(
        default=dict,
        help_text="Step-by-step implementation plan"
    )
    cost_analysis = models.JSONField(
        default=dict,
        help_text="Cost projections and ROI analysis"
    )
    
    # Session notes
    prep_notes = models.TextField(
        blank=True,
        help_text="Consultant preparation notes"
    )
    session_notes = models.TextField(
        blank=True,
        help_text="Notes from the consultation"
    )
    action_items = models.JSONField(
        default=list,
        help_text="Follow-up action items"
    )
    
    # Follow-up
    follow_up_scheduled = models.DateTimeField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    client_questions = models.JSONField(
        default=list,
        help_text="Questions from client after consultation"
    )
    
    # Feedback
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    testimonial = models.TextField(blank=True)
    can_publish_testimonial = models.BooleanField(default=False)
    feedback_date = models.DateTimeField(null=True, blank=True)
    
    # Internal notes
    internal_notes = models.TextField(blank=True)
    revenue_category = models.CharField(
        max_length=50,
        choices=[
            ('new_client', 'New Client'),
            ('repeat_client', 'Repeat Client'),
            ('upsell', 'Upsell'),
            ('referral', 'Referral')
        ],
        default='new_client'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['status', 'scheduled_date']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.company_name} - {self.package.name}"


class ConsultingResource(models.Model):
    """Resources and templates used in consulting"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('template', 'Template'),
            ('checklist', 'Checklist'),
            ('framework', 'Framework'),
            ('worksheet', 'Worksheet'),
            ('case_study', 'Case Study'),
            ('whitepaper', 'White Paper')
        ],
        default='template'
    )
    
    # Files
    file = models.FileField(upload_to='consulting/resources/', blank=True, null=True)
    preview_url = models.URLField(blank=True)
    
    # Access control
    is_public = models.BooleanField(
        default=False,
        help_text="Available to all users or only clients?"
    )
    requires_package = models.ForeignKey(
        ConsultingPackage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        help_text="Only available to clients who booked this package"
    )
    
    # Metadata
    tags = models.JSONField(default=list)
    download_count = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ConsultantAvailability(models.Model):
    """Manage consultant availability calendar"""
    consultant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        limit_choices_to={'is_staff': True}
    )
    
    # Time slot
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Status
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    booking = models.ForeignKey(
        ConsultingBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_slots'
    )
    
    # Recurring
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly')
        ],
        blank=True
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['consultant', 'date', 'start_time']
        indexes = [
            models.Index(fields=['consultant', 'date', 'is_available']),
        ]

    def __str__(self):
        return f"{self.consultant.username} - {self.date} {self.start_time}"
