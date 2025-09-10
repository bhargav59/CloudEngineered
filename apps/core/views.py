"""
Core views for CloudEngineered platform.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings

from apps.tools.models import Tool, Category
from apps.content.models import Article
from .models import SiteConfiguration, NewsletterSubscriber
from .forms import NewsletterSubscriptionForm


class HomeView(TemplateView):
    """
    Homepage view with featured tools and latest content.
    """
    template_name = 'core/home.html'
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured tools
        context['featured_tools'] = Tool.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category').order_by('-created_at')[:6]
        
        # Latest articles
        context['latest_articles'] = Article.objects.filter(
            is_published=True
        ).select_related('author').order_by('-published_at')[:4]
        
        # Popular categories
        context['popular_categories'] = Category.objects.annotate(
            tools_count=Count('tools')
        ).filter(tools_count__gt=0).order_by('-tools_count')[:6]
        
        # Stats for homepage
        context['stats'] = {
            'total_tools': Tool.objects.filter(is_published=True).count(),
            'total_articles': Article.objects.filter(is_published=True).count(),
            'total_categories': Category.objects.filter(tools__is_published=True).distinct().count(),
        }
        
        # Newsletter form
        context['newsletter_form'] = NewsletterSubscriptionForm()
        
        return context


class SearchView(ListView):
    """Advanced global search with filtering and faceted search"""
    template_name = 'core/search.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        content_type = self.request.GET.get('type', '')
        category_slug = self.request.GET.get('category', '')
        sort_by = self.request.GET.get('sort', '')

        if not query and not category_slug and not content_type:
            return []

        results = []

        # Search in tools (if not filtered to articles only)
        if content_type != 'articles':
            tool_query = Tool.objects.select_related('category', 'created_by')
            
            if query:
                tool_query = tool_query.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(features__icontains=query) |
                    Q(category__name__icontains=query)
                )
            
            if category_slug:
                tool_query = tool_query.filter(category__slug=category_slug)
            
            # Apply sorting
            if sort_by:
                if sort_by in ['name', '-name', 'created_at', '-created_at']:
                    tool_query = tool_query.order_by(sort_by)
            else:
                # Default relevance sorting (query matches in name first, then description)
                if query:
                    tool_query = tool_query.extra(
                        select={
                            'relevance': "CASE "
                                       "WHEN name ILIKE %s THEN 3 "
                                       "WHEN description ILIKE %s THEN 2 "
                                       "WHEN features ILIKE %s THEN 1 "
                                       "ELSE 0 END"
                        },
                        select_params=[f'%{query}%', f'%{query}%', f'%{query}%']
                    ).order_by('-relevance', '-created_at')

            for tool in tool_query:
                results.append({
                    'type': 'tool',
                    'object': tool,
                    'title': tool.name,
                    'description': tool.description,
                    'url': tool.get_absolute_url(),
                    'image': tool.image.url if tool.image else None,
                    'category': tool.category.name if tool.category else None,
                    'created_at': tool.created_at,
                })

        # Search in articles (if not filtered to tools only)
        if content_type != 'tools':
            article_query = Article.objects.select_related('author')
            
            if query:
                article_query = article_query.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(excerpt__icontains=query) |
                    Q(tags__icontains=query)
                )
            
            # Apply sorting
            if sort_by:
                if sort_by in ['title', '-title', 'created_at', '-created_at']:
                    # Map 'name' sorting to 'title' for articles
                    article_sort = sort_by.replace('name', 'title')
                    article_query = article_query.order_by(article_sort)
            else:
                # Default relevance sorting
                if query:
                    article_query = article_query.extra(
                        select={
                            'relevance': "CASE "
                                       "WHEN title ILIKE %s THEN 3 "
                                       "WHEN excerpt ILIKE %s THEN 2 "
                                       "WHEN content ILIKE %s THEN 1 "
                                       "ELSE 0 END"
                        },
                        select_params=[f'%{query}%', f'%{query}%', f'%{query}%']
                    ).order_by('-relevance', '-created_at')

            for article in article_query:
                results.append({
                    'type': 'article',
                    'object': article,
                    'title': article.title,
                    'description': article.excerpt or (article.content[:200] + '...' if len(article.content) > 200 else article.content),
                    'url': article.get_absolute_url(),
                    'image': article.featured_image.url if hasattr(article, 'featured_image') and article.featured_image else None,
                    'created_at': article.created_at,
                })

        # If no specific sorting was applied and we have mixed results, sort by relevance
        if not sort_by and query and results:
            results.sort(key=lambda x: (
                3 if query.lower() in x['title'].lower() else
                2 if query.lower() in x['description'].lower() else 1
            ), reverse=True)

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        # Search parameters
        context['query'] = query
        context['filters'] = {
            'type': self.request.GET.get('type', ''),
            'category': self.request.GET.get('category', ''),
            'sort': self.request.GET.get('sort', ''),
        }
        
        # Get total results count
        context['total_results'] = len(self.get_queryset()) if hasattr(self, 'object_list') else 0
        
        # Get categories for filters
        try:
            from ..tools.models import Category
            context['categories'] = Category.objects.filter(
                tools__isnull=False
            ).distinct().order_by('name')
        except ImportError:
            context['categories'] = []
        
        # Popular searches (simulate for now - in production this would come from analytics)
        if not query:
            context['popular_searches'] = [
                {'query': 'kubernetes', 'count': 45},
                {'query': 'docker', 'count': 38},
                {'query': 'monitoring', 'count': 32},
                {'query': 'ci/cd', 'count': 28},
                {'query': 'security', 'count': 25},
            ]
        
        return context


class NewsletterSubscribeView(TemplateView):
    """
    Newsletter subscription endpoint.
    """
    def post(self, request, *args, **kwargs):
        form = NewsletterSubscriptionForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if already subscribed
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )
            
            if created:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
                return JsonResponse({'success': True, 'message': 'Subscribed successfully!'})
            elif not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'Welcome back! Your subscription has been reactivated.')
                return JsonResponse({'success': True, 'message': 'Subscription reactivated!'})
            else:
                return JsonResponse({'success': False, 'message': 'You are already subscribed!'})
        
        return JsonResponse({'success': False, 'errors': form.errors})


class AboutView(TemplateView):
    """
    About page view.
    """
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Site statistics
        context['stats'] = {
            'total_tools': Tool.objects.filter(is_published=True).count(),
            'total_reviews': Article.objects.filter(is_published=True, article_type='review').count(),
            'total_comparisons': Article.objects.filter(is_published=True, article_type='comparison').count(),
            'newsletter_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        }
        
        return context


class ContactView(TemplateView):
    """
    Contact page view.
    """
    template_name = 'core/contact.html'


class PrivacyPolicyView(TemplateView):
    """
    Privacy policy page.
    """
    template_name = 'core/privacy.html'


class TermsOfServiceView(TemplateView):
    """
    Terms of service page.
    """
    template_name = 'core/terms.html'


def handler404(request, exception):
    """
    Custom 404 error handler.
    """
    return render(request, 'core/404.html', status=404)


def handler500(request):
    """
    Custom 500 error handler.
    """
    return render(request, 'core/500.html', status=500)
