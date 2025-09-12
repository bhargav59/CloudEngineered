"""
Performance analysis management command for comprehensive system monitoring.
"""

import time
import statistics
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from django.test.utils import override_settings

from apps.tools.models import Tool, Category
from apps.content.models import Article
from apps.core.utils import CacheManager


class Command(BaseCommand):
    help = 'Analyze system performance and generate detailed metrics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iterations',
            type=int,
            default=10,
            help='Number of test iterations for performance measurements'
        )
        parser.add_argument(
            '--query-analysis',
            action='store_true',
            help='Include detailed database query analysis'
        )
        parser.add_argument(
            '--cache-analysis',
            action='store_true',
            help='Include detailed cache performance analysis'
        )
        parser.add_argument(
            '--load-test',
            action='store_true',
            help='Run load testing scenarios'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting Performance Analysis')
        )
        
        iterations = options['iterations']
        results = {
            'timestamp': timezone.now().isoformat(),
            'test_iterations': iterations,
            'database_performance': {},
            'cache_performance': {},
            'query_analysis': {},
            'system_metrics': {}
        }
        
        # Basic system metrics
        self.stdout.write('📊 Collecting system metrics...')
        results['system_metrics'] = self._collect_system_metrics()
        
        # Database performance testing
        self.stdout.write('🗄️ Testing database performance...')
        results['database_performance'] = self._test_database_performance(iterations)
        
        # Cache performance testing
        self.stdout.write('⚡ Testing cache performance...')
        results['cache_performance'] = self._test_cache_performance(iterations)
        
        # Query analysis
        if options['query_analysis']:
            self.stdout.write('🔍 Analyzing database queries...')
            results['query_analysis'] = self._analyze_queries()
        
        # Cache analysis
        if options['cache_analysis']:
            self.stdout.write('📈 Analyzing cache performance...')
            results['cache_analysis'] = self._analyze_cache_performance()
        
        # Load testing
        if options['load_test']:
            self.stdout.write('🔥 Running load testing scenarios...')
            results['load_testing'] = self._run_load_tests(iterations)
        
        # Generate report
        self._generate_report(results)
        
        self.stdout.write(
            self.style.SUCCESS('✅ Performance analysis completed!')
        )

    def _collect_system_metrics(self):
        """Collect basic system metrics."""
        return {
            'total_tools': Tool.objects.count(),
            'published_tools': Tool.objects.filter(is_published=True).count(),
            'featured_tools': Tool.objects.filter(is_featured=True).count(),
            'total_categories': Category.objects.count(),
            'total_articles': Article.objects.count(),
            'published_articles': Article.objects.filter(is_published=True).count(),
        }

    def _test_database_performance(self, iterations):
        """Test database query performance."""
        results = {}
        
        # Test basic queries
        query_tests = {
            'tools_list': lambda: list(Tool.objects.all()[:20]),
            'tools_with_category': lambda: list(Tool.objects.select_related('category')[:20]),
            'featured_tools': lambda: list(Tool.objects.filter(is_featured=True)[:10]),
            'category_with_tools': lambda: list(Category.objects.prefetch_related('tools')[:10]),
            'published_articles': lambda: list(Article.objects.filter(is_published=True)[:20])
        }
        
        for test_name, query_func in query_tests.items():
            times = []
            
            for _ in range(iterations):
                start_time = time.time()
                query_func()
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to milliseconds
            
            results[test_name] = {
                'min_time_ms': min(times),
                'max_time_ms': max(times),
                'avg_time_ms': statistics.mean(times),
                'median_time_ms': statistics.median(times),
                'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0
            }
        
        return results

    def _test_cache_performance(self, iterations):
        """Test cache performance."""
        cache_manager = CacheManager()
        results = {}
        
        # Test cache operations
        cache_tests = {
            'set_operation': self._test_cache_set,
            'get_operation': self._test_cache_get,
            'delete_operation': self._test_cache_delete
        }
        
        for test_name, test_func in cache_tests.items():
            times = []
            
            for i in range(iterations):
                start_time = time.time()
                test_func(f"perf_test_{i}")
                end_time = time.time()
                times.append((end_time - start_time) * 1000)
            
            results[test_name] = {
                'min_time_ms': min(times),
                'max_time_ms': max(times),
                'avg_time_ms': statistics.mean(times),
                'median_time_ms': statistics.median(times),
                'std_dev_ms': statistics.stdev(times) if len(times) > 1 else 0
            }
        
        # Test content cache if available
        try:
            from apps.core.content_cache import content_cache
            results['content_cache_stats'] = content_cache.get_cache_statistics()
        except ImportError:
            results['content_cache_stats'] = {'error': 'Content cache not available'}
        
        return results

    def _test_cache_set(self, key):
        """Test cache set operation."""
        cache.set(key, f"test_data_{key}", 300)

    def _test_cache_get(self, key):
        """Test cache get operation."""
        cache.set(key, f"test_data_{key}", 300)
        return cache.get(key)

    def _test_cache_delete(self, key):
        """Test cache delete operation."""
        cache.set(key, f"test_data_{key}", 300)
        cache.delete(key)

    def _analyze_queries(self):
        """Analyze database queries with connection monitoring."""
        query_count_before = len(connection.queries)
        
        # Run sample operations
        Tool.objects.select_related('category').filter(is_published=True)[:10].count()
        Category.objects.prefetch_related('tools').all()[:5].count()
        Article.objects.filter(is_published=True)[:5].count()
        
        query_count_after = len(connection.queries)
        queries_executed = query_count_after - query_count_before
        
        return {
            'queries_executed': queries_executed,
            'query_details': connection.queries[-queries_executed:] if queries_executed > 0 else []
        }

    def _analyze_cache_performance(self):
        """Analyze cache performance metrics."""
        cache_manager = CacheManager()
        
        return {
            'default_cache': cache_manager.get_cache_stats('default'),
            'ai_cache': cache_manager.get_cache_stats('ai_cache'),
            'session_cache': cache_manager.get_cache_stats('session_cache')
        }

    def _run_load_tests(self, iterations):
        """Run load testing scenarios."""
        results = {}
        
        # Simulate concurrent operations
        load_scenarios = {
            'concurrent_tool_queries': self._simulate_concurrent_tool_queries,
            'mixed_operations': self._simulate_mixed_operations,
            'cache_stress_test': self._simulate_cache_stress
        }
        
        for scenario_name, scenario_func in load_scenarios.items():
            start_time = time.time()
            scenario_func(iterations)
            end_time = time.time()
            
            results[scenario_name] = {
                'total_time_ms': (end_time - start_time) * 1000,
                'operations_per_second': iterations / (end_time - start_time)
            }
        
        return results

    def _simulate_concurrent_tool_queries(self, iterations):
        """Simulate concurrent tool queries."""
        for i in range(iterations):
            Tool.objects.filter(is_published=True)[:5].count()

    def _simulate_mixed_operations(self, iterations):
        """Simulate mixed database and cache operations."""
        for i in range(iterations):
            # Database operation
            Tool.objects.filter(is_featured=True).count()
            
            # Cache operation
            cache.set(f"load_test_{i}", f"data_{i}", 60)
            cache.get(f"load_test_{i}")

    def _simulate_cache_stress(self, iterations):
        """Simulate cache stress testing."""
        for i in range(iterations):
            cache.set(f"stress_test_{i}", f"stress_data_{i}" * 100, 60)
            cache.get(f"stress_test_{i}")
            cache.delete(f"stress_test_{i}")

    def _generate_report(self, results):
        """Generate performance analysis report."""
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('📈 PERFORMANCE ANALYSIS REPORT'))
        self.stdout.write('='*80)
        
        # System metrics
        self.stdout.write('\n🏗️ System Metrics:')
        for metric, value in results['system_metrics'].items():
            self.stdout.write(f"  {metric}: {value}")
        
        # Database performance
        self.stdout.write('\n🗄️ Database Performance:')
        for test, metrics in results['database_performance'].items():
            self.stdout.write(f"  {test}:")
            self.stdout.write(f"    Average: {metrics['avg_time_ms']:.2f}ms")
            self.stdout.write(f"    Min/Max: {metrics['min_time_ms']:.2f}ms / {metrics['max_time_ms']:.2f}ms")
        
        # Cache performance
        self.stdout.write('\n⚡ Cache Performance:')
        for test, metrics in results['cache_performance'].items():
            if isinstance(metrics, dict) and 'avg_time_ms' in metrics:
                self.stdout.write(f"  {test}: {metrics['avg_time_ms']:.2f}ms average")
        
        # Query analysis
        if 'query_analysis' in results and results['query_analysis']:
            self.stdout.write(f"\n🔍 Query Analysis:")
            self.stdout.write(f"  Queries executed: {results['query_analysis']['queries_executed']}")
        
        # Load testing
        if 'load_testing' in results:
            self.stdout.write('\n🔥 Load Testing Results:')
            for scenario, metrics in results['load_testing'].items():
                self.stdout.write(f"  {scenario}:")
                self.stdout.write(f"    Operations/sec: {metrics['operations_per_second']:.2f}")
                self.stdout.write(f"    Total time: {metrics['total_time_ms']:.2f}ms")
        
        self.stdout.write('\n' + '='*80)