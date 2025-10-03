"""
Core template context processors for CloudEngineered platform.
"""

from datetime import datetime
from .models import SiteConfiguration


def site_context(request):
    """
    Add site configuration to template context.
    """
    try:
        config = SiteConfiguration.get_instance()
        return {
            'site_config': config,
            'site_name': config.site_name,
            'site_description': config.site_description,
            'current_year': datetime.now().year,
        }
    except Exception:
        return {
            'site_config': None,
            'site_name': 'CloudEngineered',
            'site_description': 'Cloud Engineering Tools Review Platform',
            'current_year': datetime.now().year,
        }
