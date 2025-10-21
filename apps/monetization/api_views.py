"""
API Views for Monetization Features
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from decimal import Decimal

from .models import (
    AffiliateProgram, AffiliateLink, Commission,
    PremiumTier, PremiumSubscription, SponsoredContent
)
from .premium_reports import ReportTemplate, PremiumReport
from .consulting import ConsultingPackage, ConsultingBooking, ConsultantAvailability
from .freemium import (
    TechStackProfile, CustomRecommendation, Team, TeamMembership,
    IntegrationRoadmap, CostCalculator
)


class AffiliateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for affiliate programs
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get affiliate dashboard metrics"""
        # Get affiliate performance metrics
        total_clicks = AffiliateLink.objects.aggregate(Sum('clicks'))['clicks__sum'] or 0
        total_conversions = AffiliateLink.objects.aggregate(Sum('conversions'))['conversions__sum'] or 0
        total_revenue = AffiliateLink.objects.aggregate(Sum('revenue_generated'))['revenue_generated__sum'] or Decimal('0.00')
        
        # Commission stats
        paid_commissions = Commission.objects.filter(status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        pending_commissions = Commission.objects.filter(status='pending').aggregate(Sum('commission_amount'))['commission_amount__sum'] or Decimal('0.00')
        
        # Top performing programs
        top_programs = AffiliateProgram.objects.filter(
            is_active=True
        ).order_by('-average_commission_per_sale')[:5]
        
        return Response({
            'overview': {
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_revenue': float(total_revenue),
                'conversion_rate': round((total_conversions / total_clicks * 100) if total_clicks > 0 else 0, 2)
            },
            'commissions': {
                'paid': float(paid_commissions),
                'pending': float(pending_commissions),
                'total': float(paid_commissions + pending_commissions)
            },
            'top_programs': [
                {
                    'name': p.program_name,
                    'tool': p.tool.name,
                    'commission_rate': float(p.commission_rate),
                    'avg_commission': float(p.average_commission_per_sale)
                }
                for p in top_programs
            ]
        })


class PremiumReportViewSet(viewsets.ModelViewSet):
    """
    API endpoints for premium reports
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PremiumReport.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """List available report templates"""
        templates = ReportTemplate.objects.filter(is_active=True)
        
        return Response([
            {
                'id': t.id,
                'name': t.name,
                'slug': t.slug,
                'description': t.description,
                'report_type': t.report_type,
                'pricing': {
                    'basic': float(t.price_basic),
                    'standard': float(t.price_standard),
                    'premium': float(t.price_premium)
                },
                'features': {
                    'basic': t.basic_features,
                    'standard': t.standard_features,
                    'premium': t.premium_features
                },
                'generation_time_minutes': t.generation_time_minutes,
                'sample_url': t.sample_url,
                'is_featured': t.is_featured
            }
            for t in templates
        ])
    
    @action(detail=False, methods=['post'])
    def purchase(self, request):
        """Purchase a premium report"""
        template_id = request.data.get('template_id')
        tier = request.data.get('tier', 'basic')
        user_inputs = request.data.get('user_inputs', {})
        
        try:
            template = ReportTemplate.objects.get(id=template_id, is_active=True)
        except ReportTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine price based on tier
        price_map = {
            'basic': template.price_basic,
            'standard': template.price_standard,
            'premium': template.price_premium
        }
        price = price_map.get(tier, template.price_basic)
        
        # Create report purchase
        report = PremiumReport.objects.create(
            user=request.user,
            template=template,
            tier=tier,
            price_paid=price,
            title=f"{template.name} Report",
            user_inputs=user_inputs,
            status='pending'
        )
        
        return Response({
            'report_id': str(report.id),
            'status': 'pending_payment',
            'price': float(price),
            'payment_url': f'/payment/reports/{report.id}/',
            'message': 'Report created. Please complete payment.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download a completed report"""
        report = self.get_object()
        
        if not report.can_download():
            return Response(
                {'error': 'Report cannot be downloaded'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        report.record_download()
        
        return Response({
            'download_url': report.pdf_file.url if report.pdf_file else None,
            'downloads_remaining': report.max_downloads - report.download_count,
            'expires_at': report.expiry_date
        })


class ConsultingViewSet(viewsets.ModelViewSet):
    """
    API endpoints for consulting services
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ConsultingBooking.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def packages(self, request):
        """List available consulting packages"""
        packages = ConsultingPackage.objects.filter(is_active=True)
        
        return Response([
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'description': p.description,
                'package_type': p.package_type,
                'price': float(p.price),
                'duration_hours': float(p.duration_hours),
                'deliverables': p.deliverables,
                'features': p.features,
                'is_available': p.is_available,
                'bookings_this_month': p.bookings_this_month,
                'is_featured': p.is_featured
            }
            for p in packages
        ])
    
    @action(detail=False, methods=['post'])
    def book(self, request):
        """Book a consulting session"""
        package_id = request.data.get('package_id')
        
        try:
            package = ConsultingPackage.objects.get(id=package_id, is_active=True)
        except ConsultingPackage.DoesNotExist:
            return Response(
                {'error': 'Package not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not package.is_available:
            return Response(
                {'error': 'Package is not available this month'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create booking
        booking = ConsultingBooking.objects.create(
            package=package,
            user=request.user,
            company_name=request.data.get('company_name', ''),
            contact_email=request.data.get('contact_email', request.user.email),
            contact_phone=request.data.get('contact_phone', ''),
            company_size=request.data.get('company_size', '11-50'),
            project_description=request.data.get('project_description', ''),
            current_tech_stack=request.data.get('current_tech_stack', []),
            pain_points=request.data.get('pain_points', []),
            goals=request.data.get('goals', []),
            budget_range=request.data.get('budget_range', 'flexible'),
            timeline=request.data.get('timeline', 'medium'),
            price_quoted=package.price,
            status='pending_payment'
        )
        
        return Response({
            'booking_id': booking.id,
            'status': 'pending_payment',
            'price': float(package.price),
            'payment_url': f'/payment/consulting/{booking.id}/',
            'message': 'Booking created. Please complete payment to schedule.'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """Get available time slots"""
        # Get available slots for next 30 days
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=30)
        
        slots = ConsultantAvailability.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_available=True,
            is_booked=False
        ).order_by('date', 'start_time')
        
        # Group by date
        availability_by_date = {}
        for slot in slots:
            date_str = slot.date.isoformat()
            if date_str not in availability_by_date:
                availability_by_date[date_str] = []
            
            availability_by_date[date_str].append({
                'id': slot.id,
                'start_time': slot.start_time.strftime('%H:%M'),
                'end_time': slot.end_time.strftime('%H:%M'),
                'timezone': slot.timezone
            })
        
        return Response(availability_by_date)


class TechStackProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoints for tech stack profiles
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TechStackProfile.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate_recommendations(self, request, pk=None):
        """Generate AI-powered tool recommendations"""
        profile = self.get_object()
        
        if not profile.is_complete:
            return Response(
                {
                    'error': 'Profile incomplete',
                    'completion_percentage': profile.completion_percentage,
                    'message': 'Please complete your tech stack profile first'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has premium access
        has_premium = request.user.premium_subscriptions.filter(
            status='active'
        ).exists()
        
        # Create recommendation (would trigger AI generation)
        recommendation = CustomRecommendation.objects.create(
            user=request.user,
            tech_stack_profile=profile,
            title=f"Custom Recommendations for {profile.company_name or request.user.username}",
            description="AI-generated tool recommendations based on your tech stack",
            is_premium=not has_premium,  # Free users get limited version
            access_tier='pro' if has_premium else 'free',
            status='generating'
        )
        
        # In production, this would trigger async AI generation
        # For now, return the recommendation ID
        return Response({
            'recommendation_id': str(recommendation.id),
            'status': 'generating',
            'estimated_time_seconds': 60,
            'message': 'Your recommendations are being generated...'
        }, status=status.HTTP_202_ACCEPTED)


class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoints for team collaboration
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a team member"""
        team = self.get_object()
        
        # Check if user has permission to invite
        membership = TeamMembership.objects.get(
            team=team,
            user=request.user
        )
        
        if not membership.can_invite and membership.role not in ['owner', 'admin']:
            return Response(
                {'error': 'You do not have permission to invite members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not team.can_add_member():
            return Response(
                {
                    'error': 'Team member limit reached',
                    'current_members': team.member_count,
                    'max_members': team.max_members,
                    'message': 'Upgrade to add more members'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = request.data.get('email')
        role = request.data.get('role', 'member')
        
        # In production, this would send an invitation email
        return Response({
            'message': f'Invitation sent to {email}',
            'status': 'invited'
        })


class CostCalculatorViewSet(viewsets.ModelViewSet):
    """
    API endpoints for cost calculator
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CostCalculator.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate costs based on current parameters"""
        calculator = self.get_object()
        
        # In production, this would call actual pricing APIs
        # and generate detailed cost breakdown
        
        calculator.calculate_costs()
        
        return Response({
            'total_monthly_cost': float(calculator.total_monthly_cost),
            'total_yearly_cost': float(calculator.total_yearly_cost),
            'tool_costs': calculator.tool_costs,
            'potential_savings': float(calculator.potential_savings),
            'savings_opportunities': calculator.savings_opportunities,
            'scenarios': calculator.scenarios
        })
