"""
Management command to test caching system
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.core.cache_utils import (
    cache_manager, ToolsCacheManager, AICacheManager, 
    SearchCacheManager, warm_popular_caches, check_cache_health
)
from apps.tools.models import Tool, Category
from apps.ai.models import ContentTemplate, AIModel
import time


class Command(BaseCommand):
    help = 'Test caching system performance and functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            choices=['basic', 'performance', 'invalidation', 'warming', 'health'],
            default='basic',
            help='Type of cache test to run'
        )
        parser.add_argument(
            '--iterations',
            type=int,
            default=100,
            help='Number of iterations for performance tests'
        )

    def handle(self, *args, **options):
        test_type = options['test_type']
        iterations = options['iterations']
        
        self.stdout.write(f"Testing cache system: {test_type}")
        
        if test_type == 'basic':
            self.test_basic_caching()
        elif test_type == 'performance':
            self.test_performance(iterations)
        elif test_type == 'invalidation':
            self.test_cache_invalidation()
        elif test_type == 'warming':
            self.test_cache_warming()
        elif test_type == 'health':
            self.test_cache_health()
    
    def test_basic_caching(self):
        """Test basic cache operations"""
        self.stdout.write("=== Basic Cache Operations Test ===")
        
        # Test cache manager
        test_data = {
            'name': 'Test Tool',
            'description': 'A test tool for caching',
            'category': 'Testing'
        }
        
        # Set cache
        cache_manager.set('test', 'basic_test', test_data, timeout=60)
        self.stdout.write("✅ Cache set successful")
        
        # Get cache
        cached_data = cache_manager.get('test', 'basic_test')
        if cached_data == test_data:
            self.stdout.write("✅ Cache get successful")
        else:
            self.stdout.write("❌ Cache get failed")
        
        # Test different cache backends
        cache_manager.set('ai_test', 'ai_basic', test_data, cache_backend='ai')
        ai_cached = cache_manager.get('ai_test', 'ai_basic', cache_backend='ai')
        if ai_cached == test_data:
            self.stdout.write("✅ AI cache backend working")
        else:
            self.stdout.write("❌ AI cache backend failed")
        
        # Clean up
        cache_manager.delete('test', 'basic_test')
        cache_manager.delete('ai_test', 'ai_basic', cache_backend='ai')
        self.stdout.write("✅ Cache cleanup successful")
    
    def test_performance(self, iterations):
        """Test cache performance vs database queries"""
        self.stdout.write(f"=== Performance Test ({iterations} iterations) ===")
        
        # Ensure we have test data
        try:
            tool = Tool.objects.first()
            if not tool:
                self.stdout.write("❌ No tools found for performance testing")
                return
        except Exception:
            self.stdout.write("❌ Database not accessible for performance testing")
            return
        
        # Test database query performance
        start_time = time.time()
        for i in range(iterations):
            tools = Tool.objects.filter(is_published=True)[:10]
            list(tools)  # Force evaluation
        db_time = time.time() - start_time
        
        # Test cache performance
        # First, warm the cache
        tools_data = list(Tool.objects.filter(is_published=True)[:10].values())
        ToolsCacheManager.set_featured_tools(tools_data)
        
        start_time = time.time()
        for i in range(iterations):
            cached_tools = ToolsCacheManager.get_featured_tools()
        cache_time = time.time() - start_time
        
        self.stdout.write(f"Database queries: {db_time:.4f}s ({iterations} iterations)")
        self.stdout.write(f"Cache queries: {cache_time:.4f}s ({iterations} iterations)")
        
        if cache_time < db_time:
            speedup = db_time / cache_time
            self.stdout.write(f"✅ Cache is {speedup:.2f}x faster than database")
        else:
            self.stdout.write("❌ Cache is slower than database (unexpected)")
    
    def test_cache_invalidation(self):
        """Test cache invalidation functionality"""
        self.stdout.write("=== Cache Invalidation Test ===")
        
        # Test pattern invalidation
        test_keys = ['test:item1', 'test:item2', 'other:item1']
        for key in test_keys:
            cache_manager.set('invalidation', key, 'test_value', timeout=300)
        
        # Verify all keys are cached
        all_cached = all(
            cache_manager.get('invalidation', key) == 'test_value' 
            for key in test_keys
        )
        if all_cached:
            self.stdout.write("✅ All test keys cached successfully")
        else:
            self.stdout.write("❌ Failed to cache test keys")
        
        # Test pattern invalidation
        cache_manager.invalidate_pattern('test:')
        
        # Check results
        test_keys_cached = [
            cache_manager.get('invalidation', key) 
            for key in ['test:item1', 'test:item2']
        ]
        other_key_cached = cache_manager.get('invalidation', 'other:item1')
        
        if all(val is None for val in test_keys_cached) and other_key_cached == 'test_value':
            self.stdout.write("✅ Pattern invalidation working correctly")
        else:
            self.stdout.write("❌ Pattern invalidation failed")
        
        # Clean up
        cache_manager.delete('invalidation', 'other:item1')
    
    def test_cache_warming(self):
        """Test cache warming functionality"""
        self.stdout.write("=== Cache Warming Test ===")
        
        # Clear relevant caches first
        cache_manager.delete('tools', 'featured_tools')
        AICacheManager.set_content_templates(None)
        
        # Test cache warming
        try:
            warm_popular_caches()
            self.stdout.write("✅ Cache warming completed without errors")
            
            # Verify warmed caches
            featured_tools = ToolsCacheManager.get_featured_tools()
            ai_templates = AICacheManager.get_content_templates()
            ai_models = AICacheManager.get_ai_models()
            
            if featured_tools is not None:
                self.stdout.write(f"✅ Featured tools cached: {len(featured_tools) if isinstance(featured_tools, list) else 'data present'}")
            else:
                self.stdout.write("⚠️ Featured tools not cached (may be empty)")
            
            if ai_templates is not None:
                self.stdout.write(f"✅ AI templates cached: {len(ai_templates) if isinstance(ai_templates, list) else 'data present'}")
            else:
                self.stdout.write("⚠️ AI templates not cached (may be empty)")
            
            if ai_models is not None:
                self.stdout.write(f"✅ AI models cached: {len(ai_models) if isinstance(ai_models, list) else 'data present'}")
            else:
                self.stdout.write("⚠️ AI models not cached (may be empty)")
            
        except Exception as e:
            self.stdout.write(f"❌ Cache warming failed: {e}")
    
    def test_cache_health(self):
        """Test cache health check"""
        self.stdout.write("=== Cache Health Check ===")
        
        health_result = check_cache_health()
        
        status = health_result.get('status', 'unknown')
        message = health_result.get('message', 'No message')
        
        if status == 'healthy':
            self.stdout.write(f"✅ {message}")
        elif status == 'unhealthy':
            self.stdout.write(f"❌ {message}")
        else:
            self.stdout.write(f"⚠️ {message}")
        
        # Test all cache backends
        backends = ['default', 'ai', 'session']
        for backend in backends:
            try:
                test_key = f"health_check_{backend}"
                cache_manager.set('health', test_key, 'working', timeout=60, cache_backend=backend)
                result = cache_manager.get('health', test_key, cache_backend=backend)
                
                if result == 'working':
                    self.stdout.write(f"✅ {backend} cache backend healthy")
                    cache_manager.delete('health', test_key, cache_backend=backend)
                else:
                    self.stdout.write(f"❌ {backend} cache backend unhealthy")
            except Exception as e:
                self.stdout.write(f"❌ {backend} cache backend error: {e}")
        
        # Test Redis-specific features
        try:
            cache_manager.invalidate_pattern('health_check_*')
            self.stdout.write("✅ Redis pattern invalidation working")
        except Exception as e:
            self.stdout.write(f"⚠️ Redis pattern invalidation may not be available: {e}")
        
        self.stdout.write("\n=== Cache Statistics ===")
        try:
            # Get cache info from Redis
            from django_redis import get_redis_connection
            redis_conn = get_redis_connection("default")
            info = redis_conn.info()
            
            self.stdout.write(f"Redis version: {info.get('redis_version', 'Unknown')}")
            self.stdout.write(f"Connected clients: {info.get('connected_clients', 'Unknown')}")
            self.stdout.write(f"Used memory: {info.get('used_memory_human', 'Unknown')}")
            self.stdout.write(f"Total keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
            
        except Exception as e:
            self.stdout.write(f"⚠️ Could not get Redis statistics: {e}")
        
        self.stdout.write("\n✅ Cache system test completed!")