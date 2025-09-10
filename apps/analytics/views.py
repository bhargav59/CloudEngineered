from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Q, F, Max, Min
from django.db.models.functions import TruncDay, TruncHour, TruncWeek, TruncMonth
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
import json

from .models import (
    AnalyticsEvent, PageView, ContentMetrics, UserMetrics, 
    SearchMetrics, PerformanceMetrics
)
from apps.tools.models import Tool
from apps.content.models import Article


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Main analytics dashboard for administrators"""
    template_name = 'analytics/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Override with query parameters if provided
        if self.request.GET.get('start_date'):
            start_date = datetime.strptime(self.request.GET.get('start_date'), '%Y-%m-%d').date()
        if self.request.GET.get('end_date'):
            end_date = datetime.strptime(self.request.GET.get('end_date'), '%Y-%m-%d').date()
        
        # Key metrics
        context.update({
            'date_range': {
                'start': start_date,
                'end': end_date,
            },
            'total_page_views': self.get_total_page_views(start_date, end_date),
            'unique_visitors': self.get_unique_visitors(start_date, end_date),
            'total_users': self.get_total_users(start_date, end_date),
            'bounce_rate': self.get_bounce_rate(start_date, end_date),
            'popular_content': self.get_popular_content(start_date, end_date),
            'traffic_sources': self.get_traffic_sources(start_date, end_date),
            'user_engagement': self.get_user_engagement(start_date, end_date),
            'search_insights': self.get_search_insights(start_date, end_date),
        })
        
        return context
    
    def get_total_page_views(self, start_date, end_date):
        return PageView.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count()
    
    def get_unique_visitors(self, start_date, end_date):
        return PageView.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).values('session_id').distinct().count()
    
    def get_total_users(self, start_date, end_date):
        return PageView.objects.filter(
            created_at__date__range=[start_date, end_date],
            user__isnull=False
        ).values('user').distinct().count()
    
    def get_bounce_rate(self, start_date, end_date):
        total_sessions = PageView.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).values('session_id').distinct().count()
        
        if total_sessions == 0:
            return 0
        
        bounce_sessions = PageView.objects.filter(
            created_at__date__range=[start_date, end_date],
            bounce=True
        ).values('session_id').distinct().count()
        
        return round((bounce_sessions / total_sessions) * 100, 2)
    
    def get_popular_content(self, start_date, end_date):
        return ContentMetrics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('-views')[:10]
    
    def get_traffic_sources(self, start_date, end_date):
        sources = PageView.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).exclude(utm_source='').values('utm_source').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return list(sources)
    
    def get_user_engagement(self, start_date, end_date):
        return UserMetrics.objects.filter(
            date__range=[start_date, end_date]
        ).aggregate(
            avg_time_on_site=Avg('time_on_site'),
            avg_page_views=Avg('page_views'),
            avg_sessions=Avg('sessions'),
        )
    
    def get_search_insights(self, start_date, end_date):
        return SearchMetrics.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).values('normalized_query').annotate(
            count=Count('id'),
            avg_results=Avg('results_count')
        ).order_by('-count')[:10]


@method_decorator(login_required, name='dispatch')
class UserAnalyticsView(LoginRequiredMixin, TemplateView):
    """Analytics dashboard for regular users (premium feature)"""
    template_name = 'analytics/user_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user has premium access
        if not request.user.is_premium_active:
            return render(request, 'analytics/premium_required.html')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Date range (default to last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # User's personal analytics
        context.update({
            'user_metrics': self.get_user_metrics(user, start_date, end_date),
            'content_engagement': self.get_content_engagement(user, start_date, end_date),
            'activity_timeline': self.get_activity_timeline(user, start_date, end_date),
            'personal_insights': self.get_personal_insights(user, start_date, end_date),
        })
        
        return context
    
    def get_user_metrics(self, user, start_date, end_date):
        return UserMetrics.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).aggregate(
            total_sessions=Sum('sessions'),
            total_page_views=Sum('page_views'),
            total_time_on_site=Sum('time_on_site'),
            tools_viewed=Sum('tools_viewed'),
            articles_read=Sum('articles_read'),
            bookmarks_added=Sum('bookmarks_added'),
        )
    
    def get_content_engagement(self, user, start_date, end_date):
        return AnalyticsEvent.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date],
            event_type__in=['tool_view', 'article_view', 'bookmark_add']
        ).values('event_type').annotate(count=Count('id'))
    
    def get_activity_timeline(self, user, start_date, end_date):
        return AnalyticsEvent.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date]
        ).annotate(
            day=TruncDay('timestamp')
        ).values('day').annotate(
            events=Count('id')
        ).order_by('day')
    
    def get_personal_insights(self, user, start_date, end_date):
        # Most viewed content types
        content_types = AnalyticsEvent.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date]
        ).values('event_type').annotate(count=Count('id')).order_by('-count')
        
        # Peak activity hours
        peak_hours = AnalyticsEvent.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date]
        ).annotate(
            hour=TruncHour('timestamp')
        ).values('hour').annotate(
            events=Count('id')
        ).order_by('-events')[:3]
        
        return {
            'content_preferences': list(content_types[:5]),
            'peak_activity_hours': list(peak_hours),
        }


@login_required
def analytics_api_events(request):
    """API endpoint for event analytics data"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Parse parameters
    event_type = request.GET.get('event_type', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    granularity = request.GET.get('granularity', 'day')  # hour, day, week, month
    
    # Build query
    queryset = AnalyticsEvent.objects.all()
    
    if event_type:
        queryset = queryset.filter(event_type=event_type)
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        queryset = queryset.filter(timestamp__date__gte=start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        queryset = queryset.filter(timestamp__date__lte=end_date)
    
    # Aggregate by granularity
    if granularity == 'hour':
        trunc_func = TruncHour
    elif granularity == 'week':
        trunc_func = TruncWeek
    elif granularity == 'month':
        trunc_func = TruncMonth
    else:
        trunc_func = TruncDay
    
    data = queryset.annotate(
        period=trunc_func('timestamp')
    ).values('period').annotate(
        count=Count('id')
    ).order_by('period')
    
    return JsonResponse({
        'data': list(data),
        'total_events': queryset.count(),
    })


@login_required
def analytics_api_content(request):
    """API endpoint for content performance data"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    content_type_name = request.GET.get('content_type', 'tool')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    limit = int(request.GET.get('limit', 10))
    
    # Get content type
    try:
        if content_type_name == 'tool':
            content_type = ContentType.objects.get_for_model(Tool)
        elif content_type_name == 'article':
            content_type = ContentType.objects.get_for_model(Article)
        else:
            return JsonResponse({'error': 'Invalid content type'}, status=400)
    except ContentType.DoesNotExist:
        return JsonResponse({'error': 'Content type not found'}, status=404)
    
    # Build query
    queryset = ContentMetrics.objects.filter(content_type=content_type)
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        queryset = queryset.filter(date__gte=start_date)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        queryset = queryset.filter(date__lte=end_date)
    
    # Aggregate by content object
    data = queryset.values('object_id').annotate(
        total_views=Sum('views'),
        total_unique_views=Sum('unique_views'),
        avg_time_on_page=Avg('average_time_on_page'),
        total_bookmarks=Sum('bookmarks'),
        avg_rating=Avg('average_rating'),
    ).order_by('-total_views')[:limit]
    
    # Add content object details
    for item in data:
        try:
            obj = content_type.get_object_for_this_type(id=item['object_id'])
            item['title'] = getattr(obj, 'title', getattr(obj, 'name', str(obj)))
            item['url'] = getattr(obj, 'get_absolute_url', lambda: '#')()
        except:
            item['title'] = f"Unknown {content_type_name}"
            item['url'] = '#'
    
    return JsonResponse({'data': list(data)})


@login_required
def analytics_api_realtime(request):
    """API endpoint for real-time analytics"""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get recent activity (last hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    recent_events = AnalyticsEvent.objects.filter(
        timestamp__gte=one_hour_ago
    ).values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    recent_page_views = PageView.objects.filter(
        created_at__gte=one_hour_ago
    ).count()
    
    active_users = PageView.objects.filter(
        created_at__gte=one_hour_ago,
        user__isnull=False
    ).values('user').distinct().count()
    
    return JsonResponse({
        'recent_events': list(recent_events),
        'recent_page_views': recent_page_views,
        'active_users': active_users,
        'timestamp': timezone.now().isoformat(),
    })


@login_required
def track_event(request):
    """API endpoint to track custom events from frontend"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Create analytics event
        event = AnalyticsEvent.objects.create(
            event_type=data.get('event_type', 'custom'),
            event_name=data.get('event_name', ''),
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or '',
            properties=data.get('properties', {}),
            value=data.get('value'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', ''),
            page_url=data.get('page_url', ''),
        )
        
        return JsonResponse({
            'success': True,
            'event_id': str(event.event_id),
        })
        
    except (json.JSONDecodeError, KeyError) as e:
        return JsonResponse({'error': 'Invalid data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)


class ReportsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Advanced reporting interface"""
    template_name = 'analytics/reports.html'
    
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Available report types
        context['report_types'] = [
            {'id': 'content_performance', 'name': 'Content Performance'},
            {'id': 'user_engagement', 'name': 'User Engagement'},
            {'id': 'traffic_analysis', 'name': 'Traffic Analysis'},
            {'id': 'search_analysis', 'name': 'Search Analysis'},
            {'id': 'conversion_funnel', 'name': 'Conversion Funnel'},
            {'id': 'performance_metrics', 'name': 'Performance Metrics'},
        ]
        
        return context
