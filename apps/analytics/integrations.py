"""
Analytics Integration - Google Analytics 4 and Custom Tracking
"""
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional
import logging
import requests
import json

logger = logging.getLogger(__name__)


class GoogleAnalytics4Service:
    """
    Google Analytics 4 integration for tracking events and conversions.
    """
    
    def __init__(self):
        self.measurement_id = getattr(settings, 'GA4_MEASUREMENT_ID', '')
        self.api_secret = getattr(settings, 'GA4_API_SECRET', '')
        self.endpoint = f"https://www.google-analytics.com/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
        self.debug_endpoint = f"https://www.google-analytics.com/debug/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
    
    def track_event(self, client_id: str, event_name: str, event_params: Dict[str, Any] = None, user_properties: Dict[str, Any] = None) -> bool:
        """
        Track a custom event in GA4.
        
        Args:
            client_id: Unique identifier for the user
            event_name: Name of the event (e.g., 'tool_view', 'comparison_create')
            event_params: Event parameters
            user_properties: User properties
        
        Returns:
            True if successful, False otherwise
        """
        if not self.measurement_id or not self.api_secret:
            logger.warning("GA4 credentials not configured")
            return False
        
        payload = {
            'client_id': client_id,
            'events': [{
                'name': event_name,
                'params': event_params or {}
            }]
        }
        
        if user_properties:
            payload['user_properties'] = user_properties
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=5
            )
            return response.status_code == 204
        except Exception as e:
            logger.error(f"GA4 tracking error: {str(e)}")
            return False
    
    def track_page_view(self, client_id: str, page_path: str, page_title: str = '', user_id: Optional[str] = None) -> bool:
        """Track a page view."""
        params = {
            'page_path': page_path,
            'page_title': page_title,
        }
        
        if user_id:
            params['user_id'] = user_id
        
        return self.track_event(client_id, 'page_view', params)
    
    def track_tool_view(self, client_id: str, tool_name: str, tool_category: str, tool_id: int) -> bool:
        """Track tool detail page view."""
        return self.track_event(
            client_id,
            'tool_view',
            {
                'tool_name': tool_name,
                'tool_category': tool_category,
                'tool_id': tool_id,
            }
        )
    
    def track_comparison_create(self, client_id: str, tool_names: list, comparison_id: int) -> bool:
        """Track comparison creation."""
        return self.track_event(
            client_id,
            'comparison_create',
            {
                'tools': ', '.join(tool_names),
                'tool_count': len(tool_names),
                'comparison_id': comparison_id,
            }
        )
    
    def track_affiliate_click(self, client_id: str, program_name: str, tool_name: str, link_id: int) -> bool:
        """Track affiliate link click."""
        return self.track_event(
            client_id,
            'affiliate_click',
            {
                'program_name': program_name,
                'tool_name': tool_name,
                'link_id': link_id,
                'value': 1,  # Value for conversion tracking
            }
        )
    
    def track_subscription_start(self, client_id: str, tier_name: str, price: float, user_id: int) -> bool:
        """Track premium subscription start."""
        return self.track_event(
            client_id,
            'subscription_start',
            {
                'tier_name': tier_name,
                'value': price,
                'currency': 'USD',
                'transaction_id': f'sub_{user_id}_{int(timezone.now().timestamp())}',
            }
        )
    
    def track_search(self, client_id: str, search_term: str, results_count: int) -> bool:
        """Track search query."""
        return self.track_event(
            client_id,
            'search',
            {
                'search_term': search_term,
                'results_count': results_count,
            }
        )


class ConversionTracker:
    """
    Custom conversion tracking for affiliate and premium subscriptions.
    """
    
    @staticmethod
    def track_affiliate_conversion(link_id: int, order_value: float, commission: float, user_id: Optional[int] = None):
        """
        Track affiliate conversion.
        
        Creates commission record and triggers analytics events.
        """
        from apps.monetization.models import AffiliateLink, Commission
        
        try:
            link = AffiliateLink.objects.get(id=link_id)
            
            # Create commission record
            commission_record = Commission.objects.create(
                link=link,
                program=link.program,
                order_value=order_value,
                commission_amount=commission,
                status='pending',
                transaction_id=f'txn_{link_id}_{int(timezone.now().timestamp())}',
            )
            
            # Update link stats
            link.conversions += 1
            link.revenue_generated += commission
            link.save(update_fields=['conversions', 'revenue_generated'])
            
            # Update program stats
            link.program.average_commission_per_sale = (
                (link.program.average_commission_per_sale * (link.program.total_sales or 0) + commission) /
                ((link.program.total_sales or 0) + 1)
            )
            link.program.save()
            
            logger.info(f"Affiliate conversion tracked: link={link_id}, commission={commission}")
            return commission_record
            
        except Exception as e:
            logger.error(f"Error tracking affiliate conversion: {str(e)}")
            return None
    
    @staticmethod
    def track_premium_conversion(user_id: int, tier_id: int, amount: float):
        """Track premium subscription conversion."""
        from apps.monetization.models import PremiumTier
        
        try:
            tier = PremiumTier.objects.get(id=tier_id)
            
            # Analytics event
            ga4 = GoogleAnalytics4Service()
            ga4.track_event(
                client_id=f'user_{user_id}',
                event_name='purchase',
                event_params={
                    'transaction_id': f'premium_{user_id}_{int(timezone.now().timestamp())}',
                    'value': amount,
                    'currency': 'USD',
                    'items': [{
                        'item_id': f'tier_{tier_id}',
                        'item_name': tier.name,
                        'price': amount,
                        'quantity': 1,
                    }]
                }
            )
            
            logger.info(f"Premium conversion tracked: user={user_id}, tier={tier.name}, amount={amount}")
            
        except Exception as e:
            logger.error(f"Error tracking premium conversion: {str(e)}")


class AnalyticsMiddleware:
    """
    Middleware for automatic page view tracking.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.ga4 = GoogleAnalytics4Service()
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Track page view for successful GET requests
        if request.method == 'GET' and response.status_code == 200:
            self._track_page_view(request)
        
        return response
    
    def _track_page_view(self, request):
        """Track page view in GA4."""
        try:
            # Get or create client ID from session
            if 'ga_client_id' not in request.session:
                import uuid
                request.session['ga_client_id'] = str(uuid.uuid4())
            
            client_id = request.session['ga_client_id']
            page_path = request.path
            page_title = self._get_page_title(request)
            
            user_id = None
            if request.user.is_authenticated:
                user_id = str(request.user.id)
            
            self.ga4.track_page_view(client_id, page_path, page_title, user_id)
            
        except Exception as e:
            logger.error(f"Error in analytics middleware: {str(e)}")
    
    def _get_page_title(self, request):
        """Extract page title from request."""
        # This can be enhanced based on your URL patterns
        path_parts = request.path.strip('/').split('/')
        if path_parts:
            return ' '.join(word.capitalize() for word in path_parts)
        return 'Home'


class RevenueAnalytics:
    """
    Revenue analytics and reporting.
    """
    
    @staticmethod
    def get_affiliate_revenue(start_date=None, end_date=None) -> Dict[str, Any]:
        """Get affiliate revenue metrics."""
        from apps.monetization.models import Commission
        from django.db.models import Sum, Count, Avg
        
        queryset = Commission.objects.filter(status__in=['approved', 'paid'])
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        
        metrics = queryset.aggregate(
            total_revenue=Sum('commission_amount'),
            total_transactions=Count('id'),
            avg_commission=Avg('commission_amount'),
            total_order_value=Sum('order_value'),
        )
        
        return {
            'total_revenue': float(metrics['total_revenue'] or 0),
            'total_transactions': metrics['total_transactions'],
            'avg_commission': float(metrics['avg_commission'] or 0),
            'total_order_value': float(metrics['total_order_value'] or 0),
        }
    
    @staticmethod
    def get_subscription_revenue(start_date=None, end_date=None) -> Dict[str, Any]:
        """Get subscription revenue metrics."""
        from apps.monetization.models import PremiumSubscription
        from django.db.models import Sum, Count
        
        queryset = PremiumSubscription.objects.filter(status='active')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)
        
        metrics = queryset.aggregate(
            total_mrr=Sum('amount'),
            active_subscriptions=Count('id'),
        )
        
        return {
            'monthly_recurring_revenue': float(metrics['total_mrr'] or 0),
            'active_subscriptions': metrics['active_subscriptions'],
            'annual_run_rate': float(metrics['total_mrr'] or 0) * 12,
        }
    
    @staticmethod
    def get_sponsored_revenue(start_date=None, end_date=None) -> Dict[str, Any]:
        """Get sponsored content revenue metrics."""
        from apps.monetization.models import SponsoredContent
        from django.db.models import Sum, Count
        
        queryset = SponsoredContent.objects.filter(status='active')
        
        if start_date:
            queryset = queryset.filter(campaign_start__gte=start_date)
        if end_date:
            queryset = queryset.filter(campaign_start__lte=end_date)
        
        metrics = queryset.aggregate(
            total_revenue=Sum('price'),
            active_campaigns=Count('id'),
        )
        
        return {
            'total_revenue': float(metrics['total_revenue'] or 0),
            'active_campaigns': metrics['active_campaigns'],
        }
