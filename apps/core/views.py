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
            tool_count=Count('tools')
        ).filter(tool_count__gt=0).order_by('-tool_count')[:6]
        
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
    """
    Global search view for tools and content.
    """
    template_name = 'core/search.html'
    context_object_name = 'results'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return []
        
        # Search in tools
        tool_results = Tool.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(features__icontains=query),
            is_published=True
        ).select_related('category').order_by('-view_count')
        
        # Search in articles
        article_results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query),
            is_published=True
        ).select_related('author').order_by('-published_at')
        
        # Combine results
        results = []
        for tool in tool_results:
            results.append({
                'type': 'tool',
                'object': tool,
                'title': tool.name,
                'description': tool.description,
                'url': tool.get_absolute_url(),
                'image': tool.logo,
            })
        
        for article in article_results:
            results.append({
                'type': 'article',
                'object': article,
                'title': article.title,
                'description': article.excerpt,
                'url': article.get_absolute_url(),
                'image': article.featured_image,
            })
        
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = len(self.get_queryset())
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
