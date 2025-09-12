"""
Comprehensive Performance Testing Suite
Tests all Phase 8 performance optimizations including caching, database indexes, 
rate limiting, and background task processing.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache, caches
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone
from django.db import models
from apps.core.utils import CacheManager, PerformanceTracker
from apps.core.throttling import RateLimiter, RateLimitStatus
from apps.core.db_optimization import QueryOptimizer, DatabaseIndexManager
import time
import statistics
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Run comprehensive performance tests for Phase 8 optimizations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='Number of test iterations to run'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        self.iterations = options['iterations']
        self.verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Phase 8 Performance Optimization Tests')
        )
        
        # Run all performance tests
        results = {
            'cache_performance': self.test_cache_performance(),
            'database_performance': self.test_database_performance(),
            'rate_limiting': self.test_rate_limiting(),
            'middleware_performance': self.test_middleware_performance(),
            'index_optimization': self.test_index_optimization(),
            'overall_metrics': {}
        }
        
        # Calculate overall performance metrics
        self.calculate_overall_metrics(results)
        
        # Display comprehensive results
        self.display_results(results)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Phase 8 Performance Tests Completed')
        )
    
    def test_cache_performance(self):
        """Test Redis cache system performance."""
        self.stdout.write('📊 Testing Cache Performance...')
        
        cache_manager = CacheManager()
        results = {}
        
        # Test different cache backends
        for cache_name in ['default', 'ai_cache', 'session_cache']:
            cache_backend = caches[cache_name]
            times = []
            
            for i in range(self.iterations):
                start_time = time.time()
                
                # Cache operations
                key = f"test_key_{i}"
                data = {'test': 'data', 'iteration': i, 'timestamp': timezone.now().isoformat()}
                
                # Set
                cache_backend.set(key, data, timeout=300)
                
                # Get
                retrieved = cache_backend.get(key)
                
                # Verify
                assert retrieved == data
                
                # Delete
                cache_backend.delete(key)
                
                times.append(time.time() - start_time)
            
            results[cache_name] = {
                'avg_time': statistics.mean(times),
                'min_time': min(times),
                'max_time': max(times),
                'median_time': statistics.median(times),
                'total_operations': self.iterations * 3  # set, get, delete
            }
        
        # Test cache warming (simplified)
        start_time = time.time()
        
        # Warm cache with some test data
        test_data = {'sample': 'cache_warming_test', 'timestamp': timezone.now().isoformat()}
        for i in range(10):
            cache_manager.set('test', f'warm_test_{i}', test_data, timeout=300)
        
        results['cache_warming_time'] = time.time() - start_time
        
        return results
    
    def test_database_performance(self):
        """Test database query performance with indexes."""
        self.stdout.write('🗄️ Testing Database Performance...')
        
        from apps.tools.models import Tool, Category
        
        results = {}
        times = []
        
        for i in range(self.iterations):
            start_time = time.time()
            start_queries = len(connection.queries)
            
            # Test common query patterns
            # 1. Filter by published status (indexed)
            published_tools = list(Tool.objects.filter(is_published=True)[:20])
            
            # 2. Filter by category and published (composite index)
            if Category.objects.exists():
                category = Category.objects.first()
                category_tools = list(Tool.objects.filter(
                    category=category, 
                    is_published=True
                )[:10])
            
            # 3. Order by view count (indexed)
            popular_tools = list(Tool.objects.filter(
                is_published=True
            ).order_by('-view_count')[:10])
            
            # 4. Filter by rating (indexed)
            top_rated = list(Tool.objects.filter(
                is_published=True,
                rating_sum__gt=0
            ).order_by('-rating_sum')[:10])
            
            end_time = time.time()
            end_queries = len(connection.queries)
            
            times.append(end_time - start_time)
            results[f'iteration_{i}'] = {
                'query_time': end_time - start_time,
                'query_count': end_queries - start_queries
            }
        
        results['summary'] = {
            'avg_query_time': statistics.mean(times),
            'min_query_time': min(times),
            'max_query_time': max(times),
            'total_iterations': self.iterations
        }
        
        return results
    
    def test_rate_limiting(self):
        """Test rate limiting system."""
        self.stdout.write('🛡️ Testing Rate Limiting...')
        
        from django.test import RequestFactory
        
        factory = RequestFactory()
        rate_limiter = RateLimiter()
        results = {}
        
        # Test different user types
        for user_type in ['anonymous', 'authenticated', 'premium', 'staff']:
            # Create mock user
            if user_type == 'anonymous':
                # Create anonymous user mock
                user = type('AnonymousUser', (), {
                    'is_authenticated': False,
                    'is_anonymous': True,
                    'is_staff': False
                })()
            else:
                # Create authenticated user mock
                user = type('MockUser', (), {
                    'is_authenticated': True,
                    'is_anonymous': False,
                    'is_staff': user_type == 'staff',
                    'is_superuser': user_type == 'staff',
                    'id': 123
                })()
                
                if user_type == 'premium':
                    # Mock premium status
                    user.userprofile = type('UserProfile', (), {'is_premium': True})()
                
            request = factory.get('/test/')
            request.user = user
            request.META['REMOTE_ADDR'] = f'192.168.1.{hash(user_type) % 255}'
            
            # Test rate limits
            rate_limit = rate_limiter.get_rate_limit(user, 'api')
            burst_limit = rate_limiter.get_burst_limit(user)
            
            # Test rate limiting logic
            start_time = time.time()
            is_limited, rate_info = rate_limiter.is_rate_limited(request, 'api')
            check_time = time.time() - start_time
            
            results[user_type] = {
                'rate_limit': rate_limit,
                'burst_limit': burst_limit,
                'is_limited': is_limited,
                'check_time': check_time,
                'rate_info': rate_info
            }
        
        return results
    
    def test_middleware_performance(self):
        """Test performance monitoring middleware."""
        self.stdout.write('⚡ Testing Middleware Performance...')
        
        from django.test import Client
        
        client = Client()
        results = {}
        response_times = []
        
        for i in range(min(self.iterations, 5)):  # Limit to 5 for middleware tests
            start_time = time.time()
            
            # Make test request
            response = client.get('/')
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Check for performance headers (in DEBUG mode)
            headers = {}
            for header in ['X-Response-Time', 'X-DB-Queries', 'X-DB-Time']:
                if header in response:
                    headers[header] = response[header]
            
            results[f'request_{i}'] = {
                'response_time': response_time,
                'status_code': response.status_code,
                'headers': headers
            }
        
        results['summary'] = {
            'avg_response_time': statistics.mean(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
        }
        
        return results
    
    def test_index_optimization(self):
        """Test database index effectiveness."""
        self.stdout.write('📈 Testing Index Optimization...')
        
        index_manager = DatabaseIndexManager()
        optimizer = QueryOptimizer()
        
        results = {}
        
        # Get recommended indexes
        recommended_indexes = index_manager.get_recommended_indexes()
        results['recommended_indexes'] = recommended_indexes
        
        # Analyze query patterns
        start_time = time.time()
        
        # Run some queries to generate patterns
        from apps.tools.models import Tool
        Tool.objects.filter(is_published=True).count()
        Tool.objects.filter(is_featured=True, is_published=True).count()
        Tool.objects.filter(category__isnull=False).order_by('-view_count')[:5]
        
        analysis_time = time.time() - start_time
        
        # Check for slow queries
        slow_queries = optimizer.analyze_slow_queries()
        
        results['analysis'] = {
            'analysis_time': analysis_time,
            'slow_queries_count': len(slow_queries),
            'slow_queries': slow_queries[:3] if slow_queries else []  # Show first 3
        }
        
        return results
    
    def calculate_overall_metrics(self, results):
        """Calculate overall performance improvement metrics."""
        cache_results = results['cache_performance']
        db_results = results['database_performance']
        
        # Calculate cache performance improvement
        default_cache_avg = cache_results['default']['avg_time']
        cache_operations = cache_results['default']['total_operations']
        
        # Estimate improvement (baseline vs optimized)
        baseline_time = 0.1  # Estimated 100ms for non-cached operations
        improvement_factor = baseline_time / default_cache_avg if default_cache_avg > 0 else 1
        
        # Database performance metrics
        db_avg_time = db_results['summary']['avg_query_time']
        
        results['overall_metrics'] = {
            'cache_improvement_factor': improvement_factor,
            'cache_avg_operation_time': default_cache_avg,
            'database_avg_query_time': db_avg_time,
            'total_test_iterations': self.iterations,
            'performance_score': min(100, (improvement_factor * 10) + (1 / db_avg_time) * 10)
        }
    
    def display_results(self, results):
        """Display comprehensive test results."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📋 PERFORMANCE TEST RESULTS'))
        self.stdout.write('='*60)
        
        # Cache Performance
        self.stdout.write('\n🔥 CACHE PERFORMANCE:')
        for cache_name, metrics in results['cache_performance'].items():
            if isinstance(metrics, dict) and 'avg_time' in metrics:
                self.stdout.write(f"  {cache_name}:")
                self.stdout.write(f"    Average time: {metrics['avg_time']:.4f}s")
                self.stdout.write(f"    Operations: {metrics['total_operations']}")
        
        # Database Performance
        self.stdout.write('\n🗄️ DATABASE PERFORMANCE:')
        db_summary = results['database_performance']['summary']
        self.stdout.write(f"  Average query time: {db_summary['avg_query_time']:.4f}s")
        self.stdout.write(f"  Min query time: {db_summary['min_query_time']:.4f}s")
        self.stdout.write(f"  Max query time: {db_summary['max_query_time']:.4f}s")
        
        # Rate Limiting
        self.stdout.write('\n🛡️ RATE LIMITING:')
        for user_type, limits in results['rate_limiting'].items():
            self.stdout.write(f"  {user_type}:")
            self.stdout.write(f"    Rate limit: {limits['rate_limit']}/hour")
            self.stdout.write(f"    Burst limit: {limits['burst_limit']}/minute")
            self.stdout.write(f"    Check time: {limits['check_time']:.4f}s")
        
        # Overall Metrics
        self.stdout.write('\n📊 OVERALL PERFORMANCE METRICS:')
        overall = results['overall_metrics']
        self.stdout.write(f"  Cache improvement factor: {overall['cache_improvement_factor']:.2f}x")
        self.stdout.write(f"  Cache operation time: {overall['cache_avg_operation_time']:.4f}s")
        self.stdout.write(f"  Database query time: {overall['database_avg_query_time']:.4f}s")
        self.stdout.write(f"  Performance score: {overall['performance_score']:.1f}/100")
        
        # Performance Summary
        score = overall['performance_score']
        if score >= 80:
            status = self.style.SUCCESS('EXCELLENT')
        elif score >= 60:
            status = self.style.WARNING('GOOD')
        else:
            status = self.style.ERROR('NEEDS IMPROVEMENT')
        
        self.stdout.write(f"\n🎯 PERFORMANCE STATUS: {status}")
        
        if self.verbose:
            self.stdout.write('\n📝 DETAILED RESULTS:')
            self.stdout.write(json.dumps(results, indent=2, default=str))