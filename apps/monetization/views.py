"""
Views for Monetization App
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import stripe
import json
import logging

from .models import (
    AffiliateLink, 
    PremiumTier, 
    PremiumSubscription,
    SponsoredContent
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def track_affiliate_click(request, link_id):
    """
    Track affiliate link click and redirect to target URL.
    """
    link = get_object_or_404(AffiliateLink, id=link_id, is_active=True)
    
    # Track click
    link.clicks += 1
    link.last_clicked_at = timezone.now()
    link.save(update_fields=['clicks', 'last_clicked_at'])
    
    # Get user info for tracking
    user = request.user if request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # TODO: Create ClickEvent record for detailed analytics
    
    logger.info(f"Affiliate click tracked: {link.program.name} by {user or 'Anonymous'}")
    
    return redirect(link.get_tracking_url())


def pricing_page(request):
    """
    Display pricing tiers for premium subscriptions.
    """
    tiers = PremiumTier.objects.filter(is_active=True).order_by('price')
    
    # Check if user already has subscription
    user_subscription = None
    if request.user.is_authenticated:
        user_subscription = PremiumSubscription.objects.filter(
            user=request.user,
            status__in=['active', 'trialing']
        ).first()
    
    context = {
        'tiers': tiers,
        'user_subscription': user_subscription,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    
    return render(request, 'monetization/pricing.html', context)


@login_required
def subscribe(request, tier_slug):
    """
    Create Stripe checkout session for subscription.
    """
    tier = get_object_or_404(PremiumTier, slug=tier_slug, is_active=True)
    
    # Check if user already has active subscription
    existing_subscription = PremiumSubscription.objects.filter(
        user=request.user,
        status__in=['active', 'trialing']
    ).first()
    
    if existing_subscription:
        return JsonResponse({
            'error': 'You already have an active subscription'
        }, status=400)
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': tier.stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/billing/?success=true'),
            cancel_url=request.build_absolute_uri('/pricing/?canceled=true'),
            metadata={
                'user_id': request.user.id,
                'tier_id': tier.id,
            }
        )
        
        return JsonResponse({'checkout_url': checkout_session.url})
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def billing_portal(request):
    """
    Redirect to Stripe customer portal for subscription management.
    """
    subscription = PremiumSubscription.objects.filter(
        user=request.user,
        status__in=['active', 'trialing', 'past_due']
    ).first()
    
    if not subscription or not subscription.stripe_customer_id:
        return redirect('monetization:pricing')
    
    try:
        # Create Stripe billing portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=request.build_absolute_uri('/billing/'),
        )
        
        return redirect(portal_session.url)
        
    except Exception as e:
        logger.error(f"Stripe portal error: {str(e)}")
        return redirect('monetization:pricing')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for subscription events.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle specific events
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_completed(session)
        
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
        
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return HttpResponse(status=200)


def handle_checkout_completed(session):
    """Handle successful checkout completion."""
    try:
        user_id = session['metadata']['user_id']
        tier_id = session['metadata']['tier_id']
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        tier = PremiumTier.objects.get(id=tier_id)
        
        # Create or update subscription
        subscription, created = PremiumSubscription.objects.get_or_create(
            user=user,
            defaults={
                'tier': tier,
                'stripe_subscription_id': session['subscription'],
                'stripe_customer_id': session['customer'],
                'status': 'active',
            }
        )
        
        if not created:
            subscription.tier = tier
            subscription.stripe_subscription_id = session['subscription']
            subscription.stripe_customer_id = session['customer']
            subscription.status = 'active'
            subscription.save()
        
        logger.info(f"Subscription created/updated for user {user.id}")
        
    except Exception as e:
        logger.error(f"Error handling checkout: {str(e)}")


def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates."""
    try:
        subscription = PremiumSubscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        
        subscription.status = stripe_subscription['status']
        subscription.current_period_start = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_start']
        )
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            stripe_subscription['current_period_end']
        )
        subscription.save()
        
        logger.info(f"Subscription updated: {subscription.id}")
        
    except PremiumSubscription.DoesNotExist:
        logger.warning(f"Subscription not found: {stripe_subscription['id']}")


def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation."""
    try:
        subscription = PremiumSubscription.objects.get(
            stripe_subscription_id=stripe_subscription['id']
        )
        
        subscription.status = 'canceled'
        subscription.canceled_at = timezone.now()
        subscription.save()
        
        logger.info(f"Subscription canceled: {subscription.id}")
        
    except PremiumSubscription.DoesNotExist:
        logger.warning(f"Subscription not found: {stripe_subscription['id']}")


def handle_payment_failed(invoice):
    """Handle failed payment."""
    try:
        subscription = PremiumSubscription.objects.get(
            stripe_customer_id=invoice['customer']
        )
        
        subscription.status = 'past_due'
        subscription.save()
        
        # TODO: Send notification email to user
        
        logger.warning(f"Payment failed for subscription: {subscription.id}")
        
    except PremiumSubscription.DoesNotExist:
        logger.warning(f"Subscription not found for customer: {invoice['customer']}")


def advertise_page(request):
    """
    Display advertising options and sponsored content information.
    """
    context = {
        'min_budget': settings.SPONSORED_CONTENT_MIN_BUDGET if hasattr(settings, 'SPONSORED_CONTENT_MIN_BUDGET') else 500,
        'cpm': settings.SPONSORED_CONTENT_CPM if hasattr(settings, 'SPONSORED_CONTENT_CPM') else 10,
        'cpc': settings.SPONSORED_CONTENT_CPC if hasattr(settings, 'SPONSORED_CONTENT_CPC') else 2,
    }
    
    return render(request, 'monetization/advertise.html', context)


# Additional views for new features
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .premium_reports import ReportTemplate, PremiumReport
from .consulting import ConsultingPackage, ConsultingBooking
from .freemium import (
    TechStackProfile, CustomRecommendation, 
    Team, CostCalculator, IntegrationRoadmap
)


# Premium Reports Views
class ReportListView(ListView):
    """List all available report templates"""
    model = ReportTemplate
    template_name = 'monetization/reports/list.html'
    context_object_name = 'templates'
    
    def get_queryset(self):
        return ReportTemplate.objects.filter(is_active=True).order_by('sort_order')


class ReportDetailView(DetailView):
    """Detail view for a specific report template"""
    model = ReportTemplate
    template_name = 'monetization/reports/detail.html'
    context_object_name = 'template'


class ReportPurchaseView(LoginRequiredMixin, CreateView):
    """Purchase a premium report"""
    model = PremiumReport
    template_name = 'monetization/reports/purchase.html'
    fields = ['user_inputs']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = get_object_or_404(
            ReportTemplate,
            pk=self.kwargs.get('pk')
        )
        return context


class MyReportsView(LoginRequiredMixin, ListView):
    """User's purchased reports"""
    model = PremiumReport
    template_name = 'monetization/reports/my_reports.html'
    context_object_name = 'reports'
    
    def get_queryset(self):
        return PremiumReport.objects.filter(user=self.request.user).order_by('-created_at')


# Consulting Views
class ConsultingListView(ListView):
    """List all consulting packages"""
    model = ConsultingPackage
    template_name = 'monetization/consulting/list.html'
    context_object_name = 'packages'
    
    def get_queryset(self):
        return ConsultingPackage.objects.filter(is_active=True).order_by('sort_order')


class ConsultingDetailView(DetailView):
    """Detail view for a consulting package"""
    model = ConsultingPackage
    template_name = 'monetization/consulting/detail.html'
    context_object_name = 'package'


class ConsultingBookView(LoginRequiredMixin, CreateView):
    """Book a consulting session"""
    model = ConsultingBooking
    template_name = 'monetization/consulting/book.html'
    fields = [
        'company_name', 'contact_email', 'contact_phone', 
        'company_size', 'project_description', 'pain_points', 'goals'
    ]


class MyConsultationsView(LoginRequiredMixin, ListView):
    """User's consulting bookings"""
    model = ConsultingBooking
    template_name = 'monetization/consulting/my_consultations.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return ConsultingBooking.objects.filter(user=self.request.user).order_by('-scheduled_date')


# Affiliate Views
class AffiliateDashboardView(LoginRequiredMixin, ListView):
    """Affiliate marketing dashboard"""
    template_name = 'monetization/affiliate/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get affiliate stats
        from django.db.models import Sum
        context['total_clicks'] = AffiliateLink.objects.aggregate(Sum('clicks'))['clicks__sum'] or 0
        context['total_conversions'] = AffiliateLink.objects.aggregate(Sum('conversions'))['conversions__sum'] or 0
        context['total_revenue'] = AffiliateLink.objects.aggregate(Sum('revenue_generated'))['revenue_generated__sum'] or 0
        
        # Get recent affiliate links
        context['recent_links'] = AffiliateLink.objects.filter(
            is_active=True
        ).order_by('-created_at')[:10]
        
        return context
    
    def get_queryset(self):
        return AffiliateLink.objects.filter(is_active=True)


class AffiliateClickView(LoginRequiredMixin, DetailView):
    """Handle affiliate link clicks"""
    model = AffiliateLink
    
    def get(self, request, *args, **kwargs):
        link = self.get_object()
        link.record_click()
        return redirect(link.tracking_url)


# Sponsored Content View
class SponsoredContentView(ListView):
    """Display sponsored content"""
    model = SponsoredContent
    template_name = 'monetization/sponsored/list.html'
    context_object_name = 'sponsored_content'
    
    def get_queryset(self):
        return SponsoredContent.objects.filter(
            status='active',
            campaign_start__lte=timezone.now(),
            campaign_end__gte=timezone.now()
        )


# Freemium Features Views
class TechStackProfileView(LoginRequiredMixin, UpdateView):
    """User's tech stack profile"""
    model = TechStackProfile
    template_name = 'monetization/freemium/tech_stack.html'
    fields = [
        'company_name', 'industry', 'team_size',
        'programming_languages', 'frameworks', 'cloud_providers',
        'databases', 'current_tools', 'deployment_frequency',
        'infrastructure_type', 'priorities'
    ]
    
    def get_object(self):
        profile, created = TechStackProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class RecommendationsView(LoginRequiredMixin, ListView):
    """User's custom recommendations"""
    model = CustomRecommendation
    template_name = 'monetization/freemium/recommendations.html'
    context_object_name = 'recommendations'
    
    def get_queryset(self):
        return CustomRecommendation.objects.filter(
            user=self.request.user,
            status='ready'
        ).order_by('-created_at')


class TeamListView(LoginRequiredMixin, ListView):
    """User's teams"""
    model = Team
    template_name = 'monetization/freemium/teams.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)


class TeamDetailView(LoginRequiredMixin, DetailView):
    """Team detail and management"""
    model = Team
    template_name = 'monetization/freemium/team_detail.html'
    context_object_name = 'team'


class CostCalculatorView(LoginRequiredMixin, ListView):
    """Cost calculator tool"""
    model = CostCalculator
    template_name = 'monetization/freemium/cost_calculator.html'
    context_object_name = 'calculations'
    
    def get_queryset(self):
        return CostCalculator.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class IntegrationRoadmapView(LoginRequiredMixin, ListView):
    """Integration roadmaps"""
    model = IntegrationRoadmap
    template_name = 'monetization/freemium/roadmap.html'
    context_object_name = 'roadmaps'
    
    def get_queryset(self):
        return IntegrationRoadmap.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
