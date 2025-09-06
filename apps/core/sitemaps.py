"""
Sitemaps for CloudEngineered platform.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.tools.models import Tool
from apps.content.models import Article


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact']

    def location(self, item):
        return reverse(item)


class ToolSitemap(Sitemap):
    """Sitemap for tool pages."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Tool.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class ArticleSitemap(Sitemap):
    """Sitemap for article pages."""
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


# Sitemap registry
sitemaps = {
    'static': StaticViewSitemap,
    'tools': ToolSitemap,
    'articles': ArticleSitemap,
}
