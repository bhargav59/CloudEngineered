"""
Core signals for CloudEngineered platform.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteConfiguration


@receiver(post_save, sender=SiteConfiguration)
def clear_site_config_cache(sender, instance, **kwargs):
    """
    Clear cache when site configuration is updated.
    """
    cache.delete('site_configuration')
    cache.clear()  # Clear all cache for simplicity
