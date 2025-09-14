"""
Caching utilities for CloudEngineered platform
Provides centralized cache management with smart invalidation
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
from django.core.cache import cache, caches
from django.conf import settings
from django.utils.encoding import force_bytes
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


class CacheManager:
    """Centralized cache management with multiple cache backends"""
    
    def __init__(self):
        self.default_cache = cache
        self.ai_cache = caches['ai_cache']
        self.session_cache = caches['session_cache']
        self.timeouts = getattr(settings, 'CACHE_TIMEOUTS', {})
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (int, str)):
                key_parts.append(str(arg))
            elif isinstance(arg, dict):
                # Sort dict for consistent keys
                sorted_items = sorted(arg.items())
                key_parts.append(hashlib.md5(
                    force_bytes(json.dumps(sorted_items, sort_keys=True))
                ).hexdigest()[:8])
            else:
                key_parts.append(str(arg))
        
        # Add keyword arguments
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(hashlib.md5(
                force_bytes(json.dumps(sorted_kwargs, sort_keys=True))
            ).hexdigest()[:8])
        
        cache_key = ':'.join(key_parts)
        return cache_key[:250]  # Django cache key limit
    
    def get(self, cache_type: str, key: str, default=None, cache_backend: str = 'default'):
        """Get value from cache with fallback"""
        try:
            cache_instance = getattr(self, f'{cache_backend}_cache', self.default_cache)
            full_key = self.get_cache_key(cache_type, key)
            return cache_instance.get(full_key, default)
        except Exception as e:
            logger.warning(f"Cache get failed for {cache_type}:{key}: {e}")
            return default
    
    def set(self, cache_type: str, key: str, value: Any, 
            timeout: Optional[int] = None, cache_backend: str = 'default'):
        """Set value in cache with automatic timeout"""
        try:
            cache_instance = getattr(self, f'{cache_backend}_cache', self.default_cache)
            full_key = self.get_cache_key(cache_type, key)
            
            if timeout is None:
                timeout = self.timeouts.get(cache_type, 300)
            
            cache_instance.set(full_key, value, timeout)
            logger.debug(f"Cached {cache_type}:{key} for {timeout}s")
        except Exception as e:
            logger.warning(f"Cache set failed for {cache_type}:{key}: {e}")
    
    def delete(self, cache_type: str, key: str, cache_backend: str = 'default'):
        """Delete value from cache"""
        try:
            cache_instance = getattr(self, f'{cache_backend}_cache', self.default_cache)
            full_key = self.get_cache_key(cache_type, key)
            cache_instance.delete(full_key)
            logger.debug(f"Deleted cache {cache_type}:{key}")
        except Exception as e:
            logger.warning(f"Cache delete failed for {cache_type}:{key}: {e}")
    
    def invalidate_pattern(self, pattern: str, cache_backend: str = 'default'):
        """Invalidate cache keys matching pattern (Redis only)"""
        try:
            cache_instance = getattr(self, f'{cache_backend}_cache', self.default_cache)
            if hasattr(cache_instance, 'delete_pattern'):
                cache_instance.delete_pattern(f"*{pattern}*")
                logger.debug(f"Invalidated cache pattern: {pattern}")
        except Exception as e:
            logger.warning(f"Cache pattern invalidation failed for {pattern}: {e}")
    
    def get_or_set(self, cache_type: str, key: str, func: Callable, 
                   timeout: Optional[int] = None, cache_backend: str = 'default'):
        """Get from cache or execute function and cache result"""
        value = self.get(cache_type, key, cache_backend=cache_backend)
        if value is None:
            value = func()
            if value is not None:
                self.set(cache_type, key, value, timeout, cache_backend)
        return value


# Global cache manager instance
cache_manager = CacheManager()


def cache_result(cache_type: str, timeout: Optional[int] = None, 
                cache_backend: str = 'default', key_func: Optional[Callable] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            result = cache_manager.get(cache_type, cache_key, cache_backend=cache_backend)
            if result is None:
                # Execute function and cache result
                result = func(*args, **kwargs)
                if result is not None:
                    cache_manager.set(cache_type, cache_key, result, timeout, cache_backend)
            
            return result
        return wrapper
    return decorator


class ToolsCacheManager:
    """Specialized cache manager for tools and categories"""
    
    @staticmethod
    def get_tools_by_category(category_slug: str):
        """Get tools for a category with caching"""
        cache_key = f"tools_by_category:{category_slug}"
        return cache_manager.get('tools', cache_key)
    
    @staticmethod
    def set_tools_by_category(category_slug: str, tools_data):
        """Cache tools for a category"""
        cache_key = f"tools_by_category:{category_slug}"
        cache_manager.set('tools', cache_key, tools_data)
    
    @staticmethod
    def get_featured_tools():
        """Get featured tools with caching"""
        return cache_manager.get('tools', 'featured_tools')
    
    @staticmethod
    def set_featured_tools(tools_data):
        """Cache featured tools"""
        cache_manager.set('tools', 'featured_tools', tools_data)
    
    @staticmethod
    def get_tool_detail(tool_slug: str):
        """Get tool detail with caching"""
        cache_key = f"tool_detail:{tool_slug}"
        return cache_manager.get('tools', cache_key)
    
    @staticmethod
    def set_tool_detail(tool_slug: str, tool_data):
        """Cache tool detail"""
        cache_key = f"tool_detail:{tool_slug}"
        cache_manager.set('tools', cache_key, tool_data)
    
    @staticmethod
    def invalidate_tool_cache(tool_slug: str):
        """Invalidate all cache for a specific tool"""
        cache_manager.delete('tools', f'tool_detail:{tool_slug}')
        cache_manager.invalidate_pattern(f'tools_by_category')
        cache_manager.delete('tools', 'featured_tools')


class AICacheManager:
    """Specialized cache manager for AI content"""
    
    @staticmethod
    def get_content_templates():
        """Get content templates with caching"""
        return cache_manager.get('ai_templates', 'all_templates', cache_backend='ai')
    
    @staticmethod
    def set_content_templates(templates_data):
        """Cache content templates"""
        cache_manager.set('ai_templates', 'all_templates', templates_data, 
                         timeout=7200, cache_backend='ai')
    
    @staticmethod
    def get_ai_models():
        """Get AI models with caching"""
        return cache_manager.get('ai_templates', 'ai_models', cache_backend='ai')
    
    @staticmethod
    def set_ai_models(models_data):
        """Cache AI models"""
        cache_manager.set('ai_templates', 'ai_models', models_data, 
                         timeout=7200, cache_backend='ai')
    
    @staticmethod
    def get_generation(generation_id: int):
        """Get AI generation with caching"""
        cache_key = f"generation:{generation_id}"
        return cache_manager.get('ai_generations', cache_key, cache_backend='ai')
    
    @staticmethod
    def set_generation(generation_id: int, generation_data):
        """Cache AI generation"""
        cache_key = f"generation:{generation_id}"
        cache_manager.set('ai_generations', cache_key, generation_data, 
                         timeout=3600, cache_backend='ai')
    
    @staticmethod
    def invalidate_generation(generation_id: int):
        """Invalidate generation cache"""
        cache_key = f"generation:{generation_id}"
        cache_manager.delete('ai_generations', cache_key, cache_backend='ai')


class SearchCacheManager:
    """Cache manager for search results"""
    
    @staticmethod
    def get_search_results(query: str, filters: Dict = None):
        """Get search results with caching"""
        cache_key = f"search:{query}"
        if filters:
            filter_hash = hashlib.md5(
                force_bytes(json.dumps(filters, sort_keys=True))
            ).hexdigest()[:8]
            cache_key = f"search:{query}:{filter_hash}"
        
        return cache_manager.get('search_results', cache_key)
    
    @staticmethod
    def set_search_results(query: str, results_data, filters: Dict = None):
        """Cache search results"""
        cache_key = f"search:{query}"
        if filters:
            filter_hash = hashlib.md5(
                force_bytes(json.dumps(filters, sort_keys=True))
            ).hexdigest()[:8]
            cache_key = f"search:{query}:{filter_hash}"
        
        cache_manager.set('search_results', cache_key, results_data, timeout=600)


# Cache invalidation signals
@receiver(post_save, sender='tools.Tool')
@receiver(post_delete, sender='tools.Tool')
def invalidate_tool_cache(sender, instance, **kwargs):
    """Invalidate tool-related cache when tool is modified"""
    ToolsCacheManager.invalidate_tool_cache(instance.slug)
    logger.debug(f"Invalidated cache for tool: {instance.slug}")


@receiver(post_save, sender='tools.Category')
@receiver(post_delete, sender='tools.Category')
def invalidate_category_cache(sender, instance, **kwargs):
    """Invalidate category-related cache when category is modified"""
    cache_manager.invalidate_pattern('tools_by_category')
    cache_manager.delete('tools', 'featured_tools')
    logger.debug(f"Invalidated cache for category: {instance.slug}")


@receiver(post_save, sender='ai.ContentTemplate')
@receiver(post_delete, sender='ai.ContentTemplate')
def invalidate_ai_template_cache(sender, instance, **kwargs):
    """Invalidate AI template cache when template is modified"""
    AICacheManager.set_content_templates(None)  # Force refresh
    logger.debug(f"Invalidated AI template cache")


@receiver(post_save, sender='ai.ContentGeneration')
def invalidate_ai_generation_cache(sender, instance, **kwargs):
    """Invalidate AI generation cache when generation is modified"""
    AICacheManager.invalidate_generation(instance.id)
    logger.debug(f"Invalidated AI generation cache: {instance.id}")


# Cache warming functions
def warm_popular_caches():
    """Warm up frequently accessed caches"""
    from apps.tools.models import Category, Tool
    from apps.ai.models import ContentTemplate, AIModel
    
    try:
        # Warm tools cache
        featured_tools = Tool.objects.filter(is_featured=True).select_related('category')[:10]
        ToolsCacheManager.set_featured_tools(list(featured_tools.values()))
        
        # Warm categories cache
        for category in Category.objects.filter(is_featured=True):
            tools = Tool.objects.filter(category=category, is_published=True)[:20]
            ToolsCacheManager.set_tools_by_category(category.slug, list(tools.values()))
        
        # Warm AI templates cache
        templates = ContentTemplate.objects.filter(is_active=True).select_related('model')
        AICacheManager.set_content_templates(list(templates.values()))
        
        # Warm AI models cache
        models = AIModel.objects.filter(is_active=True).select_related('provider')
        AICacheManager.set_ai_models(list(models.values()))
        
        logger.info("Cache warming completed successfully")
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")


# Cache health check
def check_cache_health():
    """Check if cache is working properly"""
    try:
        test_key = "cache_health_check"
        test_value = "working"
        
        # Test default cache
        cache_manager.set('health', test_key, test_value, timeout=60)
        result = cache_manager.get('health', test_key)
        
        if result == test_value:
            cache_manager.delete('health', test_key)
            return {"status": "healthy", "message": "Cache is working properly"}
        else:
            return {"status": "unhealthy", "message": "Cache read/write test failed"}
            
    except Exception as e:
        return {"status": "error", "message": f"Cache health check failed: {e}"}