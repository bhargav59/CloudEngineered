"""
Core views for CloudEngineered platform.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, ListView
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

from apps.tools.models import Tool, Category
from apps.content.models import Article
from .models import SiteConfiguration, NewsletterSubscriber
from .forms import NewsletterSubscriptionForm
from .utils import CacheManager


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
        
        # Featured categories (for homepage hero/sections)
        context['featured_categories'] = Category.objects.filter(
            is_featured=True
        ).order_by('sort_order')[:6]
        
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
    Newsletter subscription endpoint with email verification.
    """
    def post(self, request, *args, **kwargs):
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        import json
        
        form = NewsletterSubscriptionForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            name = request.POST.get('name', '')
            preferences_str = request.POST.get('preferences', '{}')
            
            try:
                preferences = json.loads(preferences_str) if preferences_str else {}
            except json.JSONDecodeError:
                preferences = {}
            
            # Get IP and user agent
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Check if already subscribed
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'is_active': True,
                    'is_verified': False,
                    'source': 'website',
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'preferences': preferences
                }
            )
            
            if created:
                # Send verification email
                try:
                    verification_url = subscriber.get_verification_url(request)
                    
                    # Email context
                    context = {
                        'subscriber': subscriber,
                        'verification_url': verification_url,
                        'site_name': getattr(settings, 'SITE_NAME', 'CloudEngineered'),
                    }
                    
                    # Render HTML email
                    html_message = render_to_string('emails/newsletter_confirmation.html', context)
                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject='Confirm Your Newsletter Subscription',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Thank you! Please check your email to confirm your subscription.'
                    })
                except Exception as e:
                    # Log error but still return success to user
                    print(f"Error sending verification email: {e}")
                    return JsonResponse({
                        'success': True,
                        'message': 'Subscribed! (Email verification pending)'
                    })
                    
            elif not subscriber.is_active:
                # Reactivate subscription
                subscriber.resubscribe()
                subscriber.name = name or subscriber.name
                subscriber.preferences = preferences
                subscriber.save(update_fields=['name', 'preferences'])
                
                return JsonResponse({
                    'success': True,
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'You are already subscribed! Check your email for the confirmation link.'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Please enter a valid email address.',
            'errors': form.errors
        })


class NewsletterVerifyView(TemplateView):
    """
    Email verification endpoint.
    """
    template_name = 'core/newsletter_verify.html'
    
    def get(self, request, token):
        try:
            subscriber = NewsletterSubscriber.objects.get(verification_token=token)
            
            if subscriber.is_verified:
                return render(request, self.template_name, {
                    'success': True,
                    'subscriber': subscriber,
                    'already_verified': True
                })
            
            subscriber.verify_email()
            
            return render(request, self.template_name, {
                'success': True,
                'subscriber': subscriber
            })
            
        except NewsletterSubscriber.DoesNotExist:
            return render(request, self.template_name, {
                'success': False,
                'error_message': 'Invalid or expired verification link.'
            })


class NewsletterUnsubscribeView(TemplateView):
    """
    Unsubscribe endpoint.
    """
    template_name = 'core/newsletter_unsubscribe.html'
    
    def get(self, request, token):
        try:
            subscriber = NewsletterSubscriber.objects.get(verification_token=token)
            
            if not subscriber.is_active:
                return render(request, self.template_name, {
                    'success': True,
                    'subscriber': subscriber,
                    'already_unsubscribed': True
                })
            
            subscriber.unsubscribe()
            
            return render(request, self.template_name, {
                'success': True,
                'subscriber': subscriber
            })
            
        except NewsletterSubscriber.DoesNotExist:
            return render(request, self.template_name, {
                'success': False
            })


class NewsletterResubscribeView(TemplateView):
    """
    Resubscribe endpoint.
    """
    def post(self, request, token):
        try:
            subscriber = NewsletterSubscriber.objects.get(verification_token=token)
            subscriber.resubscribe()
            messages.success(request, 'Welcome back! You have been resubscribed.')
            return redirect('core:home')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Invalid subscription link.')
            return redirect('core:home')


class NewsletterFeedbackView(TemplateView):
    """
    Collect unsubscribe feedback.
    """
    def post(self, request):
        token = request.POST.get('subscriber_token')
        reason = request.POST.get('reason')
        comments = request.POST.get('comments', '')
        
        try:
            subscriber = NewsletterSubscriber.objects.get(verification_token=token)
            # Store feedback in preferences
            feedback = subscriber.preferences.get('unsubscribe_feedback', [])
            feedback.append({
                'reason': reason,
                'comments': comments,
                'date': timezone.now().isoformat()
            })
            subscriber.preferences['unsubscribe_feedback'] = feedback
            subscriber.save(update_fields=['preferences'])
            
            messages.success(request, 'Thank you for your feedback!')
        except NewsletterSubscriber.DoesNotExist:
            pass
        
        return redirect('core:home')


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


# Monitoring and Performance Views

@require_http_methods(["GET"])
def health_check(request):
    """Basic health check endpoint."""
    try:
        # Test database connectivity
        Tool.objects.count()
        
        # Test cache connectivity
        test_key = f"health_check_{timezone.now().timestamp()}"
        cache.set(test_key, "healthy", 30)
        cache_healthy = cache.get(test_key) == "healthy"
        cache.delete(test_key)
        
        status = {
            'status': 'healthy' if cache_healthy else 'degraded',
            'timestamp': timezone.now().isoformat(),
            'database': 'healthy',
            'cache': 'healthy' if cache_healthy else 'unhealthy'
        }
        
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


@require_http_methods(["GET"])
def cache_status(request):
    """Comprehensive cache status with content cache metrics."""
    cache_manager = CacheManager()
    
    try:
        from .content_cache import content_cache
        cache_stats = content_cache.get_cache_statistics()
    except Exception as e:
        cache_stats = {'error': f"Content cache unavailable: {str(e)}"}
    
    # Get legacy cache stats
    try:
        default_stats = cache_manager.get_cache_stats('default')
        ai_stats = cache_manager.get_cache_stats('ai_cache')
        session_stats = cache_manager.get_cache_stats('session_cache')
    except Exception as e:
        default_stats = ai_stats = session_stats = {'error': str(e)}
    
    status = {
        'status': 'healthy',
        'cache_backends': {
            'default': default_stats,
            'ai_cache': ai_stats,
            'session_cache': session_stats
        },
        'content_cache_stats': cache_stats,
        'timestamp': timezone.now().isoformat()
    }
    
    return JsonResponse(status)


@require_http_methods(["GET"])
def performance_metrics(request):
    """Performance metrics and database query statistics."""
    try:
        # Database metrics
        db_metrics = {
            'tools': {
                'total': Tool.objects.count(),
                'published': Tool.objects.filter(is_published=True).count(),
                'featured': Tool.objects.filter(is_featured=True).count()
            },
            'categories': {
                'total': Category.objects.count(),
                'with_tools': Category.objects.filter(tools__isnull=False).distinct().count()
            },
            'articles': {
                'total': Article.objects.count(),
                'published': Article.objects.filter(is_published=True).count()
            }
        }
        
        # Cache performance
        cache_manager = CacheManager()
        cache_metrics = {
            'default': cache_manager.get_cache_stats('default'),
            'ai_cache': cache_manager.get_cache_stats('ai_cache'),
            'session_cache': cache_manager.get_cache_stats('session_cache')
        }
        
        # Content cache performance
        try:
            from .content_cache import content_cache
            content_metrics = content_cache.get_cache_statistics()
        except Exception:
            content_metrics = {'error': 'Content cache unavailable'}
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database_metrics': db_metrics,
            'cache_metrics': cache_metrics,
            'content_cache_metrics': content_metrics
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


@require_http_methods(["POST"])
def warm_caches(request):
    """Warm up critical caches."""
    try:
        cache_manager = CacheManager()
        
        # Warm content caches
        warmed_content = cache_manager.warm_content_caches()
        
        # Warm basic test caches
        warmed_basic = cache_manager.warm_cache("performance_test", 5)
        
        return JsonResponse({
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'warmed_caches': {
                'content_caches': warmed_content,
                'test_caches': warmed_basic
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


@require_http_methods(["GET"])
def system_status(request):
    """Comprehensive system status dashboard."""
    try:
        # Database status
        tools_count = Tool.objects.count()
        articles_count = Article.objects.count()
        categories_count = Category.objects.count()
        
        # Cache health
        cache_manager = CacheManager()
        default_cache = cache_manager.get_cache_stats('default')
        ai_cache = cache_manager.get_cache_stats('ai_cache')
        session_cache = cache_manager.get_cache_stats('session_cache')
        
        cache_health = not any([
            'error' in default_cache,
            'error' in ai_cache,
            'error' in session_cache
        ])
        
        # Content cache health
        try:
            from .content_cache import content_cache
            content_cache_health = True
            content_stats = content_cache.get_cache_statistics()
        except Exception:
            content_cache_health = False
            content_stats = {'error': 'Content cache unavailable'}
        
        overall_status = 'healthy' if cache_health and content_cache_health else 'degraded'
        
        return JsonResponse({
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'components': {
                'database': {
                    'status': 'healthy',
                    'tools_count': tools_count,
                    'articles_count': articles_count,
                    'categories_count': categories_count
                },
                'cache': {
                    'status': 'healthy' if cache_health else 'unhealthy',
                    'backends': ['default', 'ai_cache', 'session_cache']
                },
                'content_cache': {
                    'status': 'healthy' if content_cache_health else 'unhealthy',
                    'stats': content_stats
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)


class PerformanceDashboardView(TemplateView):
    """Performance monitoring dashboard."""
    template_name = 'monitoring/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add initial dashboard data
        context['dashboard_title'] = 'Performance Dashboard'
        context['refresh_interval'] = 30  # seconds
        
        return context
