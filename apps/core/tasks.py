"""
Background tasks for core functionality.
Performance optimization, caching, and maintenance tasks.
"""

from celery import shared_task
from django.core.cache import cache
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def warm_cache(self):
    """
    Warm up cache with frequently accessed data.
    """
    try:
        from apps.tools.models import Tool, Category
        from apps.core.cache_utils import CacheManager
        
        cache_manager = CacheManager()
        
        # Cache popular tools
        popular_tools = Tool.objects.filter(
            is_published=True
        ).order_by('-view_count')[:20]
        
        for tool in popular_tools:
            cache_key = f"tool_detail:{tool.slug}"
            cache_manager.set(cache_key, tool, timeout=3600)
        
        # Cache categories with tool counts
        categories = Category.objects.annotate(
            tool_count=Count('tools', filter=models.Q(tools__is_published=True))
        )
        
        for category in categories:
            cache_key = f"category_detail:{category.slug}"
            cache_manager.set(cache_key, category, timeout=3600)
        
        # Cache popular searches
        from apps.core.models import PopularSearch
        popular_searches = PopularSearch.objects.order_by('-search_count')[:50]
        cache_manager.set('popular_searches', popular_searches, timeout=1800)
        
        logger.info("Cache warming completed successfully")
        return {"status": "success", "cached_items": len(popular_tools) + len(categories) + 1}
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True)
def cleanup_expired_cache(self):
    """
    Clean up expired cache entries and optimize cache usage.
    """
    try:
        # This would typically be handled by Redis automatically,
        # but we can implement custom cleanup logic here
        
        # Clear specific cache patterns that might be stale
        from apps.core.cache_utils import CacheManager
        cache_manager = CacheManager()
        
        # Clear old search results
        cache_manager.delete_pattern('search_results:*')
        
        # Clear old analytics data
        cache_manager.delete_pattern('analytics:*')
        
        logger.info("Cache cleanup completed")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=3)
def optimize_database_queries(self):
    """
    Analyze and optimize database queries.
    """
    try:
        from django.db import connection
        from apps.core.db_optimization import QueryOptimizer, DatabaseIndexManager
        
        optimizer = QueryOptimizer()
        index_manager = DatabaseIndexManager()
        
        # Analyze slow queries
        slow_queries = optimizer.analyze_slow_queries()
        
        # Check index usage
        index_analysis = index_manager.analyze_index_usage()
        
        # Generate optimization recommendations
        recommendations = {
            'slow_queries': len(slow_queries),
            'index_analysis': index_analysis,
            'optimization_suggestions': optimizer.get_optimization_suggestions()
        }
        
        logger.info(f"Database optimization analysis completed: {recommendations}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True)
def generate_performance_report(self):
    """
    Generate performance report and send alerts if needed.
    """
    try:
        from apps.analytics.models import PerformanceMetrics
        
        # Get performance data from last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_metrics = PerformanceMetrics.objects.filter(
            timestamp__gte=one_hour_ago
        )
        
        if not recent_metrics.exists():
            return {"status": "no_data"}
        
        # Calculate averages
        avg_response_time = recent_metrics.aggregate(
            avg_time=Avg('response_time')
        )['avg_time']
        
        avg_db_time = recent_metrics.aggregate(
            avg_time=Avg('database_time')
        )['avg_time']
        
        avg_queries = recent_metrics.aggregate(
            avg_queries=Avg('query_count')
        )['avg_queries']
        
        # Check for performance issues
        slow_requests = recent_metrics.filter(response_time__gt=2.0).count()
        total_requests = recent_metrics.count()
        
        report = {
            'timestamp': timezone.now().isoformat(),
            'avg_response_time': float(avg_response_time or 0),
            'avg_database_time': float(avg_db_time or 0),
            'avg_query_count': float(avg_queries or 0),
            'slow_requests': slow_requests,
            'total_requests': total_requests,
            'slow_request_percentage': (slow_requests / total_requests * 100) if total_requests > 0 else 0
        }
        
        # Send alert if performance is degraded
        if report['slow_request_percentage'] > 10:  # More than 10% slow requests
            send_performance_alert.delay(report)
        
        logger.info(f"Performance report generated: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Performance report generation failed: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True)
def send_performance_alert(self, report):
    """
    Send performance alert to administrators.
    """
    try:
        # In a real implementation, this would send email/slack notifications
        logger.warning(f"PERFORMANCE ALERT: {report}")
        
        # Could integrate with:
        # - Email notifications
        # - Slack webhooks
        # - PagerDuty
        # - Custom monitoring systems
        
        return {"status": "alert_sent", "report": report}
        
    except Exception as e:
        logger.error(f"Failed to send performance alert: {e}")
        return {"status": "error", "message": str(e)}


@shared_task(bind=True, max_retries=2)
def update_search_suggestions(self):
    """
    Update search suggestions based on recent queries.
    """
    try:
        from apps.core.models import SearchQuery, SearchSuggestion
        
        # Get recent searches
        recent_queries = SearchQuery.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('query').annotate(
            count=Count('id')
        ).filter(count__gte=5).order_by('-count')[:100]
        
        # Update suggestions
        for query_data in recent_queries:
            query = query_data['query']
            count = query_data['count']
            
            SearchSuggestion.objects.update_or_create(
                query=query,
                defaults={
                    'frequency': count,
                    'is_active': True
                }
            )
        
        # Disable old suggestions
        old_threshold = timezone.now() - timedelta(days=30)
        SearchSuggestion.objects.filter(
            updated_at__lt=old_threshold
        ).update(is_active=False)
        
        logger.info(f"Updated {len(recent_queries)} search suggestions")
        return {"status": "success", "updated_count": len(recent_queries)}
        
    except Exception as e:
        logger.error(f"Search suggestion update failed: {e}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True)
def compress_old_analytics(self):
    """
    Compress or aggregate old analytics data.
    """
    try:
        from apps.analytics.models import AnalyticsEvent, PageView
        
        # Archive data older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Count records to be processed
        old_events = AnalyticsEvent.objects.filter(timestamp__lt=cutoff_date)
        old_pageviews = PageView.objects.filter(created_at__lt=cutoff_date)
        
        events_count = old_events.count()
        pageviews_count = old_pageviews.count()
        
        # In a real implementation, we might:
        # 1. Aggregate data into daily/weekly summaries
        # 2. Move to cold storage
        # 3. Delete raw records after aggregation
        
        # For now, just log the counts
        logger.info(f"Found {events_count} old events and {pageviews_count} old pageviews to process")
        
        return {
            "status": "success",
            "old_events": events_count,
            "old_pageviews": pageviews_count
        }
        
    except Exception as e:
        logger.error(f"Analytics compression failed: {e}")
        return {"status": "error", "message": str(e)}