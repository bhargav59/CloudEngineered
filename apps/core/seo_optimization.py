"""
Advanced SEO Optimization System
Meta tags, structured data, Open Graph, Twitter Cards.
"""
from django.utils.html import escape
from django.conf import settings
from typing import Dict, Optional
import json


# ============================================================================
# SEO META GENERATOR
# ============================================================================

class SEOMetaGenerator:
    """Generate SEO meta tags for pages."""
    
    @classmethod
    def generate_meta_tags(cls, context: Dict) -> Dict[str, str]:
        """
        Generate comprehensive meta tags.
        
        Args:
            context: Dictionary with:
                - page_type: 'home', 'tool', 'category', 'comparison', 'blog'
                - title: Page title
                - description: Page description
                - image: Image URL
                - url: Canonical URL
                - additional_data: Type-specific data
        
        Returns:
            Dictionary of meta tags
        """
        page_type = context.get('page_type', 'general')
        title = escape(context.get('title', 'CloudTools - Find the Best Cloud Tools'))
        description = escape(context.get('description', ''))
        image = context.get('image', f"{settings.SITE_URL}/static/images/og-default.jpg")
        url = context.get('url', settings.SITE_URL)
        
        # Generate base meta tags
        meta_tags = {
            'title': title,
            'description': description[:160],  # Max 160 chars
            'canonical': url,
            'robots': 'index, follow',
        }
        
        # Add Open Graph tags
        meta_tags.update(cls._generate_og_tags(title, description, image, url, page_type))
        
        # Add Twitter Card tags
        meta_tags.update(cls._generate_twitter_tags(title, description, image))
        
        # Add type-specific tags
        if page_type == 'tool':
            meta_tags.update(cls._generate_tool_meta(context))
        elif page_type == 'comparison':
            meta_tags.update(cls._generate_comparison_meta(context))
        
        return meta_tags
    
    @classmethod
    def _generate_og_tags(cls, title, description, image, url, page_type):
        """Generate Open Graph tags."""
        og_type = 'website'
        if page_type == 'tool':
            og_type = 'product'
        elif page_type == 'blog':
            og_type = 'article'
        
        return {
            'og:title': title,
            'og:description': description[:200],
            'og:image': image,
            'og:url': url,
            'og:type': og_type,
            'og:site_name': 'CloudTools',
            'og:locale': 'en_US',
        }
    
    @classmethod
    def _generate_twitter_tags(cls, title, description, image):
        """Generate Twitter Card tags."""
        return {
            'twitter:card': 'summary_large_image',
            'twitter:title': title[:70],  # Max 70 chars
            'twitter:description': description[:200],
            'twitter:image': image,
            'twitter:site': '@cloudtools',  # Replace with actual handle
        }
    
    @classmethod
    def _generate_tool_meta(cls, context):
        """Generate tool-specific meta tags."""
        tool = context.get('additional_data', {}).get('tool')
        if not tool:
            return {}
        
        keywords = []
        if tool.tags:
            keywords = [tag.strip() for tag in tool.tags.split(',')]
        keywords.extend([tool.category.name, tool.pricing_model])
        
        return {
            'keywords': ', '.join(keywords),
            'product:price:amount': tool.pricing_tiers.get('basic', {}).get('price', '0') if tool.pricing_tiers else '0',
            'product:price:currency': 'USD',
        }
    
    @classmethod
    def _generate_comparison_meta(cls, context):
        """Generate comparison-specific meta tags."""
        comparison = context.get('additional_data', {}).get('comparison')
        if not comparison:
            return {}
        
        tool_names = [tool.name for tool in comparison.tools.all()[:3]]
        keywords = tool_names + ['comparison', 'vs', 'alternative']
        
        return {
            'keywords': ', '.join(keywords),
        }


# ============================================================================
# STRUCTURED DATA GENERATOR
# ============================================================================

class StructuredDataGenerator:
    """Generate JSON-LD structured data for rich snippets."""
    
    @classmethod
    def generate_structured_data(cls, page_type: str, data: Dict) -> str:
        """
        Generate JSON-LD structured data.
        
        Args:
            page_type: Type of page
            data: Page-specific data
        
        Returns:
            JSON-LD string
        """
        if page_type == 'tool':
            return cls._generate_product_schema(data)
        elif page_type == 'comparison':
            return cls._generate_comparison_schema(data)
        elif page_type == 'blog':
            return cls._generate_article_schema(data)
        elif page_type == 'organization':
            return cls._generate_organization_schema()
        
        return cls._generate_website_schema()
    
    @classmethod
    def _generate_product_schema(cls, data: Dict) -> str:
        """Generate Product schema for tools."""
        tool = data.get('tool')
        if not tool:
            return '{}'
        
        # Calculate average rating
        avg_rating = 0
        if tool.rating_count > 0:
            avg_rating = round(tool.rating_sum / tool.rating_count, 1)
        
        schema = {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": tool.name,
            "description": tool.description,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": ", ".join(tool.supported_platforms) if tool.supported_platforms else "Web",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock"
            }
        }
        
        # Add rating if available
        if tool.rating_count > 0:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": avg_rating,
                "ratingCount": tool.rating_count,
                "bestRating": 5,
                "worstRating": 1
            }
        
        # Add pricing if available
        if tool.pricing_tiers:
            basic_price = tool.pricing_tiers.get('basic', {}).get('price', 0)
            schema["offers"]["price"] = str(basic_price)
        
        # Add images
        if tool.logo:
            schema["image"] = tool.logo
        
        # Add URLs
        if tool.website_url:
            schema["url"] = tool.website_url
        
        return json.dumps(schema, indent=2)
    
    @classmethod
    def _generate_comparison_schema(cls, data: Dict) -> str:
        """Generate ItemList schema for comparisons."""
        comparison = data.get('comparison')
        if not comparison:
            return '{}'
        
        tools_list = []
        for idx, tool in enumerate(comparison.tools.all(), start=1):
            tools_list.append({
                "@type": "ListItem",
                "position": idx,
                "item": {
                    "@type": "SoftwareApplication",
                    "name": tool.name,
                    "description": tool.description
                }
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": comparison.title,
            "description": comparison.description,
            "itemListElement": tools_list
        }
        
        return json.dumps(schema, indent=2)
    
    @classmethod
    def _generate_article_schema(cls, data: Dict) -> str:
        """Generate Article schema for blog posts."""
        article = data.get('article')
        if not article:
            return '{}'
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article.get('title'),
            "description": article.get('description'),
            "author": {
                "@type": "Person",
                "name": article.get('author', 'CloudTools Team')
            },
            "publisher": {
                "@type": "Organization",
                "name": "CloudTools",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{settings.SITE_URL}/static/images/logo.png"
                }
            },
            "datePublished": article.get('published_at', '').isoformat() if article.get('published_at') else '',
            "dateModified": article.get('updated_at', '').isoformat() if article.get('updated_at') else '',
        }
        
        return json.dumps(schema, indent=2)
    
    @classmethod
    def _generate_organization_schema(cls) -> str:
        """Generate Organization schema."""
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "CloudTools",
            "url": settings.SITE_URL,
            "logo": f"{settings.SITE_URL}/static/images/logo.png",
            "description": "Find and compare the best cloud development tools",
            "sameAs": [
                "https://twitter.com/cloudtools",
                "https://github.com/cloudtools",
                "https://linkedin.com/company/cloudtools"
            ]
        }
        
        return json.dumps(schema, indent=2)
    
    @classmethod
    def _generate_website_schema(cls) -> str:
        """Generate WebSite schema with search action."""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "CloudTools",
            "url": settings.SITE_URL,
            "potentialAction": {
                "@type": "SearchAction",
                "target": {
                    "@type": "EntryPoint",
                    "urlTemplate": f"{settings.SITE_URL}/search?q={{search_term_string}}"
                },
                "query-input": "required name=search_term_string"
            }
        }
        
        return json.dumps(schema, indent=2)


# ============================================================================
# BREADCRUMB GENERATOR
# ============================================================================

class BreadcrumbGenerator:
    """Generate structured breadcrumb navigation."""
    
    @classmethod
    def generate_breadcrumbs(cls, path_info: list) -> str:
        """
        Generate BreadcrumbList JSON-LD.
        
        Args:
            path_info: List of tuples (name, url)
        
        Returns:
            JSON-LD string
        """
        items = []
        for idx, (name, url) in enumerate(path_info, start=1):
            items.append({
                "@type": "ListItem",
                "position": idx,
                "name": name,
                "item": url
            })
        
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
        
        return json.dumps(schema, indent=2)


# ============================================================================
# SEO MIDDLEWARE
# ============================================================================

class SEOEnhancementMiddleware:
    """Middleware to add SEO enhancements to responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Add caching headers for static content
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            response['Cache-Control'] = 'public, max-age=31536000'
        
        return response


# ============================================================================
# SITEMAP HELPERS
# ============================================================================

class SitemapHelper:
    """Helper methods for sitemap generation."""
    
    @classmethod
    def get_tool_priority(cls, tool) -> float:
        """
        Calculate priority for tool in sitemap.
        
        Args:
            tool: Tool object
        
        Returns:
            Priority (0.0 - 1.0)
        """
        base_priority = 0.5
        
        # Boost for featured/trending
        if tool.is_featured:
            base_priority += 0.3
        if tool.is_trending:
            base_priority += 0.2
        
        # Boost for popularity
        if tool.github_stars > 10000:
            base_priority += 0.1
        elif tool.github_stars > 1000:
            base_priority += 0.05
        
        return min(base_priority, 1.0)
    
    @classmethod
    def get_changefreq(cls, model_type: str) -> str:
        """
        Get change frequency for sitemap.
        
        Args:
            model_type: Type of model
        
        Returns:
            Change frequency string
        """
        frequencies = {
            'home': 'daily',
            'category': 'weekly',
            'tool': 'weekly',
            'comparison': 'monthly',
            'blog': 'monthly',
        }
        
        return frequencies.get(model_type, 'monthly')
