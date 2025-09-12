"""
Core utilities for the CloudEngineered platform.
"""

import time
from django.db import connection
from django.core.cache import cache, caches
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities."""
    
    def __init__(self):
        self.slow_query_threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0)
    
    def analyze_slow_queries(self):
        """Analyze and return slow queries from connection."""
        slow_queries = []
        
        # Get queries from connection
        if hasattr(connection, 'queries'):
            for query in connection.queries:
                if float(query['time']) > self.slow_query_threshold:
                    slow_queries.append({
                        'sql': query['sql'][:200] + '...' if len(query['sql']) > 200 else query['sql'],
                        'time': query['time'],
                        'duration': float(query['time'])
                    })
        
        return slow_queries
    
    def optimize_queries(self):
        """Provide query optimization suggestions."""
        suggestions = []
        slow_queries = self.analyze_slow_queries()
        
        for query in slow_queries:
            if 'WHERE' not in query['sql'].upper():
                suggestions.append({
                    'query': query['sql'][:100] + '...',
                    'suggestion': 'Consider adding WHERE clause to filter results',
                    'priority': 'high'
                })
            elif 'ORDER BY' in query['sql'].upper() and 'LIMIT' not in query['sql'].upper():
                suggestions.append({
                    'query': query['sql'][:100] + '...',
                    'suggestion': 'Consider adding LIMIT to ORDER BY queries',
                    'priority': 'medium'
                })
            elif query['duration'] > 2.0:
                suggestions.append({
                    'query': query['sql'][:100] + '...',
                    'suggestion': 'Query exceeds 2s threshold - needs index optimization',
                    'priority': 'critical'
                })
        
        return suggestions


class CacheManager:
    """Cache management utilities."""
    
    def __init__(self):
        self.default_timeout = getattr(settings, 'CACHE_DEFAULT_TIMEOUT', 300)
    
    def set(self, cache_name, key, value, timeout=None):
        """Set cache value in specified cache."""
        if timeout is None:
            timeout = self.default_timeout
        
        if cache_name == 'default':
            cache.set(key, value, timeout)
        else:
            cache_backend = caches[cache_name] if cache_name in ['ai_cache', 'session_cache'] else cache
            cache_backend.set(key, value, timeout)
        
        logger.debug(f"Cached {key} for {timeout}s")
    
    def get(self, cache_name, key):
        """Get cache value from specified cache."""
        if cache_name == 'default':
            return cache.get(key)
        else:
            cache_backend = caches[cache_name] if cache_name in ['ai_cache', 'session_cache'] else cache
            return cache_backend.get(key)
    
    def get_cache_stats(self, cache_name='default'):
        """Get cache statistics for specified cache."""
        try:
            from django_redis import get_redis_connection
            
            # Map cache names to Redis connection names
            connection_name = 'default'
            if cache_name == 'ai_cache':
                connection_name = 'ai_cache'
            elif cache_name == 'session_cache':
                connection_name = 'session_cache'
            
            r = get_redis_connection(connection_name)
            info = r.info()
            
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / max(1, total)) * 100
            
            return {
                'hits': hits,
                'misses': misses,
                'hit_rate': round(hit_rate, 2),
                'memory_usage': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_operations': total
            }
        except Exception as e:
            logger.warning(f"Could not get cache stats for {cache_name}: {e}")
            return {
                'hits': 0,
                'misses': 0,
                'hit_rate': 0,
                'memory_usage': 'N/A',
                'connected_clients': 0,
                'total_operations': 0
            }
    
    def warm_cache(self, key_prefix="warm_test", count=10):
        """Warm up cache with test data."""
        warmed_keys = []
        
        for i in range(count):
            key = f"{key_prefix}_{i}"
            cache.set(key, f"test_data_{i}", self.default_timeout)
            warmed_keys.append(key)
            logger.debug(f"Cached {key} for {self.default_timeout}s")
        
        return warmed_keys
    
    def clear_pattern(self, pattern):
        """Clear cache keys matching pattern."""
        try:
            from django_redis import get_redis_connection
            r = get_redis_connection("default")
            keys = r.keys(pattern)
            if keys:
                r.delete(*keys)
            return len(keys)
        except Exception as e:
            logger.warning(f"Could not clear cache pattern {pattern}: {e}")
            return 0


class PerformanceTracker:
    """Performance tracking utilities."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.db_queries_start = None
        self.db_queries_end = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.db_queries_start = len(connection.queries)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.db_queries_end = len(connection.queries)
    
    @property
    def duration(self):
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    @property
    def query_count(self):
        """Get number of queries executed."""
        if self.db_queries_start is not None and self.db_queries_end is not None:
            return self.db_queries_end - self.db_queries_start
        return 0
    
    def get_stats(self):
        """Get performance statistics."""
        return {
            'duration': round(self.duration, 3),
            'query_count': self.query_count,
            'avg_query_time': round(self.duration / max(1, self.query_count), 3)
        }


def track_performance(func):
    """Decorator to track function performance."""
    def wrapper(*args, **kwargs):
        with PerformanceTracker() as tracker:
            result = func(*args, **kwargs)
        
        logger.info(f"Performance for {func.__name__}: {tracker.get_stats()}")
        return result
    
    return wrapper


def get_system_stats():
    """Get system performance statistics."""
    try:
        import psutil
        
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
    except ImportError:
        logger.warning("psutil not available, returning mock system stats")
        return {
            'cpu_percent': 25.0,
            'memory_percent': 60.0,
            'disk_usage': 45.0,
            'load_average': [0.5, 0.7, 0.8]
        }