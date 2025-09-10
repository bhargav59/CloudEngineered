"""
Search API endpoints for autocomplete and suggestions.
"""

from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import SearchSuggestion, PopularSearch, SearchQuery
from ..tools.models import Tool, Category


class SearchSuggestionsAPI(View):
    """API endpoint for search autocomplete suggestions"""
    
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def get(self, request):
        query = request.GET.get('q', '').strip()
        limit = min(int(request.GET.get('limit', 10)), 20)  # Max 20 suggestions
        
        if not query or len(query) < 2:
            return JsonResponse({'suggestions': []})
        
        suggestions = []
        
        try:
            # Get search suggestions from database
            db_suggestions = SearchSuggestion.objects.filter(
                suggestion__icontains=query,
                is_active=True
            ).order_by('-priority', '-search_count')[:limit//2]
            
            for suggestion in db_suggestions:
                suggestions.append({
                    'text': suggestion.suggestion,
                    'type': 'suggestion',
                    'category': suggestion.category,
                    'count': suggestion.search_count
                })
            
            # Get popular searches that match
            popular_searches = PopularSearch.objects.filter(
                query__icontains=query
            ).order_by('-search_count')[:limit//2]
            
            for popular in popular_searches:
                if not any(s['text'] == popular.query for s in suggestions):
                    suggestions.append({
                        'text': popular.query,
                        'type': 'popular',
                        'count': popular.search_count
                    })
            
            # If we don't have enough suggestions, add tool/category names
            if len(suggestions) < limit:
                remaining = limit - len(suggestions)
                
                # Tool names that match
                tools = Tool.objects.filter(
                    name__icontains=query
                ).values('name')[:remaining//2]
                
                for tool in tools:
                    if not any(s['text'].lower() == tool['name'].lower() for s in suggestions):
                        suggestions.append({
                            'text': tool['name'],
                            'type': 'tool',
                            'category': 'Tools'
                        })
                
                # Category names that match
                if len(suggestions) < limit:
                    categories = Category.objects.filter(
                        name__icontains=query
                    ).values('name')[:remaining//2]
                    
                    for category in categories:
                        if not any(s['text'].lower() == category['name'].lower() for s in suggestions):
                            suggestions.append({
                                'text': category['name'],
                                'type': 'category',
                                'category': 'Categories'
                            })
            
            # Sort by relevance (exact matches first, then by popularity)
            suggestions.sort(key=lambda x: (
                0 if x['text'].lower().startswith(query.lower()) else 1,
                -x.get('count', 0)
            ))
            
            return JsonResponse({
                'suggestions': suggestions[:limit],
                'query': query
            })
            
        except Exception as e:
            return JsonResponse({
                'suggestions': [],
                'error': str(e)
            }, status=500)


class SearchFiltersAPI(View):
    """API endpoint for dynamic search filters"""
    
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def get(self, request):
        try:
            # Get categories with tool counts
            categories = Category.objects.annotate(
                tool_count=Count('tools')
            ).filter(tool_count__gt=0).order_by('name')
            
            # Build filter data
            filters = {
                'categories': [
                    {
                        'slug': cat.slug,
                        'name': cat.name,
                        'count': cat.tool_count,
                        'icon': getattr(cat, 'icon', '📁')
                    }
                    for cat in categories
                ],
                'content_types': [
                    {'key': 'tools', 'name': 'Tools', 'icon': '🔧'},
                    {'key': 'articles', 'name': 'Articles', 'icon': '📄'},
                ],
                'sort_options': [
                    {'key': '', 'name': 'Relevance'},
                    {'key': 'name', 'name': 'Name A-Z'},
                    {'key': '-name', 'name': 'Name Z-A'},
                    {'key': '-created_at', 'name': 'Newest First'},
                    {'key': 'created_at', 'name': 'Oldest First'},
                ]
            }
            
            return JsonResponse(filters)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)


class SearchAnalyticsAPI(View):
    """API endpoint for search analytics (admin only)"""
    
    def get(self, request):
        if not request.user.is_staff:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        try:
            # Get popular searches
            popular = PopularSearch.objects.filter(
                search_count__gte=2
            ).order_by('-search_count')[:10]
            
            # Get recent searches with zero results
            zero_results = SearchQuery.objects.filter(
                results_count=0
            ).values('query').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            
            analytics = {
                'popular_searches': [
                    {
                        'query': p.query,
                        'count': p.search_count,
                        'unique_users': p.unique_users,
                        'is_trending': p.is_trending
                    }
                    for p in popular
                ],
                'zero_result_queries': [
                    {
                        'query': z['query'],
                        'count': z['count']
                    }
                    for z in zero_results
                ],
                'total_searches': SearchQuery.objects.count(),
                'unique_queries': SearchQuery.objects.values('query').distinct().count(),
            }
            
            return JsonResponse(analytics)
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
