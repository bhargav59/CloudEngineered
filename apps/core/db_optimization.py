"""
Database optimization utilities for CloudEngineered platform
Provides database indexes, query optimization, and performance monitoring
"""

from django.db import models, connection
from django.db.models import Index, Q
from django.core.management.base import BaseCommand
from django.conf import settings
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def analyze_slow_queries(threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Analyze and return slow queries from connection."""
        return QueryOptimizer.get_slow_queries(threshold_seconds)
    
    @staticmethod
    def get_slow_queries(threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Get queries that took longer than threshold"""
        if not settings.DEBUG:
            return []
        
        from django.db import connection
        slow_queries = []
        
        for query in connection.queries:
            time_taken = float(query['time'])
            if time_taken >= threshold_seconds:
                slow_queries.append({
                    'sql': query['sql'],
                    'time': time_taken,
                    'formatted_time': f"{time_taken:.4f}s"
                })
        
        return slow_queries
    
    @staticmethod
    def analyze_query_patterns():
        """Analyze common query patterns for optimization"""
        if not settings.DEBUG:
            return {}
        
        from django.db import connection
        patterns = {
            'select_queries': 0,
            'insert_queries': 0,
            'update_queries': 0,
            'delete_queries': 0,
            'join_queries': 0,
            'where_queries': 0,
            'order_by_queries': 0,
            'group_by_queries': 0
        }
        
        for query in connection.queries:
            sql = query['sql'].upper()
            
            if 'SELECT' in sql:
                patterns['select_queries'] += 1
            if 'INSERT' in sql:
                patterns['insert_queries'] += 1
            if 'UPDATE' in sql:
                patterns['update_queries'] += 1
            if 'DELETE' in sql:
                patterns['delete_queries'] += 1
            if 'JOIN' in sql:
                patterns['join_queries'] += 1
            if 'WHERE' in sql:
                patterns['where_queries'] += 1
            if 'ORDER BY' in sql:
                patterns['order_by_queries'] += 1
            if 'GROUP BY' in sql:
                patterns['group_by_queries'] += 1
        
        patterns['total_queries'] = len(connection.queries)
        return patterns
    
    @staticmethod
    def reset_query_log():
        """Reset Django query log for testing"""
        if settings.DEBUG:
            connection.queries_log.clear()


class DatabaseIndexManager:
    """Manage database indexes for optimal performance"""
    
    @staticmethod
    def get_recommended_indexes():
        """Get recommended indexes for all models"""
        return {
            'tools_tool': [
                # Frequently queried fields
                Index(fields=['is_published'], name='tools_tool_is_published_idx'),
                Index(fields=['is_featured'], name='tools_tool_is_featured_idx'),
                Index(fields=['is_trending'], name='tools_tool_is_trending_idx'),
                Index(fields=['status'], name='tools_tool_status_idx'),
                Index(fields=['category', 'is_published'], name='tools_tool_cat_pub_idx'),
                Index(fields=['created_at'], name='tools_tool_created_idx'),
                Index(fields=['updated_at'], name='tools_tool_updated_idx'),
                Index(fields=['view_count'], name='tools_tool_views_idx'),
                
                # Search optimization
                Index(fields=['name'], name='tools_tool_name_idx'),
                Index(fields=['slug'], name='tools_tool_slug_idx'),
                
                # Composite indexes for common queries
                Index(fields=['category', 'is_published', 'created_at'], 
                     name='tools_tool_cat_pub_created_idx'),
                Index(fields=['is_featured', 'is_published'], 
                     name='tools_tool_feat_pub_idx'),
            ],
            
            'tools_category': [
                Index(fields=['is_featured'], name='tools_cat_featured_idx'),
                Index(fields=['sort_order'], name='tools_cat_sort_idx'),
                Index(fields=['slug'], name='tools_cat_slug_idx'),
                Index(fields=['is_featured', 'sort_order'], name='tools_cat_feat_sort_idx'),
            ],
            
            'ai_contentgeneration': [
                Index(fields=['status'], name='ai_gen_status_idx'),
                Index(fields=['initiated_by'], name='ai_gen_user_idx'),
                Index(fields=['template'], name='ai_gen_template_idx'),
                Index(fields=['created_at'], name='ai_gen_created_idx'),
                Index(fields=['completed_at'], name='ai_gen_completed_idx'),
                
                # Composite indexes
                Index(fields=['initiated_by', 'status'], name='ai_gen_user_status_idx'),
                Index(fields=['template', 'status'], name='ai_gen_tmpl_status_idx'),
                Index(fields=['initiated_by', 'created_at'], name='ai_gen_user_created_idx'),
            ],
            
            'ai_contenttemplate': [
                Index(fields=['is_active'], name='ai_tmpl_active_idx'),
                Index(fields=['template_type'], name='ai_tmpl_type_idx'),
                Index(fields=['model'], name='ai_tmpl_model_idx'),
                Index(fields=['template_type', 'is_active'], name='ai_tmpl_type_active_idx'),
            ],
            
            'ai_aimodel': [
                Index(fields=['is_active'], name='ai_model_active_idx'),
                Index(fields=['provider'], name='ai_model_provider_idx'),
                Index(fields=['provider', 'is_active'], name='ai_model_prov_active_idx'),
            ],
            
            'users_user': [
                Index(fields=['is_active'], name='users_active_idx'),
                Index(fields=['is_staff'], name='users_staff_idx'),
                Index(fields=['is_premium'], name='users_premium_idx'),
                Index(fields=['date_joined'], name='users_joined_idx'),
                Index(fields=['email'], name='users_email_idx'),
            ],
            
            'content_article': [
                Index(fields=['is_published'], name='content_art_published_idx'),
                Index(fields=['is_featured'], name='content_art_featured_idx'),
                Index(fields=['status'], name='content_art_status_idx'),
                Index(fields=['category'], name='content_art_category_idx'),
                Index(fields=['author'], name='content_art_author_idx'),
                Index(fields=['published_at'], name='content_art_pub_date_idx'),
                Index(fields=['created_at'], name='content_art_created_idx'),
                
                # Composite indexes
                Index(fields=['is_published', 'published_at'], 
                     name='content_art_pub_date_idx'),
                Index(fields=['category', 'is_published'], 
                     name='content_art_cat_pub_idx'),
                Index(fields=['author', 'is_published'], 
                     name='content_art_auth_pub_idx'),
            ]
        }


def optimize_queryset_tools():
    """Optimized queryset patterns for tools"""
    from apps.tools.models import Tool, Category
    
    # Example optimized queries
    optimized_queries = {
        'featured_tools_with_category': Tool.objects.select_related('category').filter(
            is_featured=True, is_published=True
        ).order_by('-created_at'),
        
        'tools_by_category_optimized': lambda category_slug: Tool.objects.select_related(
            'category'
        ).filter(
            category__slug=category_slug, is_published=True
        ).order_by('-view_count', '-created_at'),
        
        'trending_tools': Tool.objects.select_related('category').filter(
            is_trending=True, is_published=True
        ).order_by('-view_count')[:20],
        
        'popular_categories': Category.objects.prefetch_related(
            models.Prefetch(
                'tools',
                queryset=Tool.objects.filter(is_published=True)
            )
        ).filter(is_featured=True).order_by('sort_order'),
    }
    
    return optimized_queries


def optimize_queryset_ai():
    """Optimized queryset patterns for AI models"""
    from apps.ai.models import ContentGeneration, ContentTemplate, AIModel
    
    optimized_queries = {
        'user_generations': lambda user: ContentGeneration.objects.select_related(
            'template__model__provider', 'initiated_by', 'quality'
        ).filter(initiated_by=user).order_by('-created_at'),
        
        'active_templates': ContentTemplate.objects.select_related(
            'model__provider'
        ).filter(is_active=True).order_by('template_type', 'name'),
        
        'available_models': AIModel.objects.select_related('provider').filter(
            is_active=True
        ).order_by('provider__name', 'name'),
        
        'recent_successful_generations': ContentGeneration.objects.select_related(
            'template', 'initiated_by'
        ).filter(
            status='completed',
            created_at__gte=models.functions.Now() - models.DurationField(days=7)
        ).order_by('-created_at')[:50],
    }
    
    return optimized_queries


class PerformanceProfiler:
    """Profile database performance"""
    
    def __init__(self):
        self.start_time = None
        self.start_query_count = 0
        
    def start_profiling(self):
        """Start performance profiling"""
        self.start_time = time.time()
        if settings.DEBUG:
            self.start_query_count = len(connection.queries)
        
    def end_profiling(self) -> Dict[str, Any]:
        """End profiling and return results"""
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        result = {
            'execution_time': execution_time,
            'execution_time_ms': execution_time * 1000,
            'query_count': 0,
            'queries': []
        }
        
        if settings.DEBUG:
            current_query_count = len(connection.queries)
            result['query_count'] = current_query_count - self.start_query_count
            result['queries'] = connection.queries[self.start_query_count:]
        
        return result


def profile_function(func):
    """Decorator to profile function performance"""
    def wrapper(*args, **kwargs):
        profiler = PerformanceProfiler()
        profiler.start_profiling()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profile_result = profiler.end_profiling()
            logger.info(
                f"Function {func.__name__} executed in {profile_result['execution_time_ms']:.2f}ms "
                f"with {profile_result['query_count']} DB queries"
            )
    
    return wrapper


# Database optimization middleware
class QueryCountMiddleware:
    """Middleware to log query counts for each request"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if settings.DEBUG:
            start_query_count = len(connection.queries)
            start_time = time.time()
        
        response = self.get_response(request)
        
        if settings.DEBUG:
            end_time = time.time()
            query_count = len(connection.queries) - start_query_count
            execution_time = (end_time - start_time) * 1000
            
            # Log slow requests
            if execution_time > 500 or query_count > 10:
                logger.warning(
                    f"Slow request: {request.path} took {execution_time:.2f}ms "
                    f"with {query_count} DB queries"
                )
        
        return response