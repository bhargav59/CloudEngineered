"""
AI-powered views for content generation and management.
"""

import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

try:
    from apps.automation.ai_content_generator import AIContentGenerator
except ImportError:
    AIContentGenerator = None

try:
    from apps.automation.tasks import (
        generate_ai_tool_review, 
        generate_ai_tool_comparison,
        generate_trend_analysis,
        scan_github_for_new_tools
    )
except ImportError:
    # Create mock functions when tasks are not available
    def generate_ai_tool_review(*args, **kwargs):
        return {"success": False, "error": "Task system unavailable"}
    
    def generate_ai_tool_comparison(*args, **kwargs):
        return {"success": False, "error": "Task system unavailable"}
    
    def generate_trend_analysis(*args, **kwargs):
        return {"success": False, "error": "Task system unavailable"}
    
    def scan_github_for_new_tools(*args, **kwargs):
        return {"success": False, "error": "Task system unavailable"}

from apps.tools.models import Tool, Category, ToolComparison
from apps.content.models import Article


@method_decorator(staff_member_required, name='dispatch')
class AIDashboardView(TemplateView):
    """AI Dashboard for managing automated content generation."""
    
    template_name = 'admin/ai_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # AI Statistics
        context['ai_stats'] = {
            'total_ai_articles': Article.objects.filter(ai_generated=True).count(),
            'ai_articles_this_month': Article.objects.filter(
                ai_generated=True,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
            'tools_without_reviews': Tool.objects.exclude(
                id__in=Article.objects.filter(
                    article_type='tool_review',
                    metadata__tool_id__isnull=False
                ).values_list('metadata__tool_id', flat=True)
            ).count(),
            'pending_comparisons': self._get_pending_comparisons_count()
        }
        
        # Recent AI content
        context['recent_ai_content'] = Article.objects.filter(
            ai_generated=True
        ).order_by('-created_at')[:10]
        
        # Tools needing reviews
        context['tools_needing_reviews'] = Tool.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).exclude(
            id__in=Article.objects.filter(
                article_type='tool_review',
                metadata__tool_id__isnull=False
            ).values_list('metadata__tool_id', flat=True)
        )[:20]
        
        # Categories for trend analysis
        context['categories'] = Category.objects.annotate(
            tool_count=Count('tools'),
            recent_tools=Count('tools', filter=Q(
                tools__created_at__gte=timezone.now() - timedelta(days=90)
            ))
        ).order_by('-tool_count')
        
        return context
    
    def _get_pending_comparisons_count(self):
        """Get count of tool pairs that could be compared."""
        categories_with_multiple_tools = Category.objects.annotate(
            tool_count=Count('tools')
        ).filter(tool_count__gte=2)
        
        # Estimate potential comparisons (simplified)
        total_combinations = 0
        for category in categories_with_multiple_tools:
            tool_count = category.tool_count
            if tool_count >= 2:
                # nC2 = n! / (2! * (n-2)!) = n * (n-1) / 2
                combinations = tool_count * (tool_count - 1) // 2
                total_combinations += min(combinations, 10)  # Max 10 per category
        
        # Subtract existing comparisons
        existing_comparisons = ToolComparison.objects.count()
        return max(0, total_combinations - existing_comparisons)


@staff_member_required
@require_http_methods(["POST"])
def generate_tool_review_ajax(request):
    """AJAX endpoint for generating tool reviews."""
    try:
        tool_id = request.POST.get('tool_id')
        provider = request.POST.get('provider', 'openai')
        
        if not tool_id:
            return JsonResponse({'success': False, 'error': 'Tool ID required'})
        
        tool = get_object_or_404(Tool, id=tool_id)
        
        # Queue the task
        task = generate_ai_tool_review.delay(tool_id, provider=provider)
        
        return JsonResponse({
            'success': True,
            'message': f'Review generation started for {tool.name}',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_http_methods(["POST"])
def generate_comparison_ajax(request):
    """AJAX endpoint for generating tool comparisons."""
    try:
        tool_ids = request.POST.getlist('tool_ids')
        provider = request.POST.get('provider', 'openai')
        
        if len(tool_ids) < 2:
            return JsonResponse({'success': False, 'error': 'At least 2 tools required'})
        
        # Convert to integers
        tool_ids = [int(tid) for tid in tool_ids]
        
        # Verify tools exist
        tools = Tool.objects.filter(id__in=tool_ids)
        if len(tools) != len(tool_ids):
            return JsonResponse({'success': False, 'error': 'Some tools not found'})
        
        # Queue the task
        task = generate_ai_tool_comparison.delay(tool_ids, provider=provider)
        
        tool_names = [tool.name for tool in tools]
        return JsonResponse({
            'success': True,
            'message': f'Comparison generation started for {", ".join(tool_names)}',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_http_methods(["POST"])
def generate_trend_analysis_ajax(request):
    """AJAX endpoint for generating trend analysis."""
    try:
        category_id = request.POST.get('category_id')
        provider = request.POST.get('provider', 'openai')
        
        if not category_id:
            return JsonResponse({'success': False, 'error': 'Category ID required'})
        
        category = get_object_or_404(Category, id=category_id)
        
        # Queue the task
        task = generate_trend_analysis.delay(category_id, provider=provider)
        
        return JsonResponse({
            'success': True,
            'message': f'Trend analysis generation started for {category.name}',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_http_methods(["POST"])
def scan_github_ajax(request):
    """AJAX endpoint for scanning GitHub for new tools."""
    try:
        # Queue the task
        task = scan_github_for_new_tools.delay()
        
        return JsonResponse({
            'success': True,
            'message': 'GitHub scan started for new tools',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def ai_content_preview(request):
    """Preview AI-generated content before publishing."""
    if request.method == 'POST':
        try:
            generator = AIContentGenerator()
            content_type = request.POST.get('content_type')
            
            if content_type == 'tool_review':
                tool_id = request.POST.get('tool_id')
                tool = get_object_or_404(Tool, id=tool_id)
                
                # Generate preview content
                result = generator.generate_tool_review(tool, provider='openai')
                
                return JsonResponse({
                    'success': True,
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {})
                })
                
            elif content_type == 'trend_analysis':
                category_id = request.POST.get('category_id')
                category = get_object_or_404(Category, id=category_id)
                
                # Generate preview content
                result = generator.generate_trend_analysis(category, provider='openai')
                
                return JsonResponse({
                    'success': True,
                    'content': result.get('content', ''),
                    'metadata': result.get('metadata', {})
                })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@staff_member_required
def bulk_ai_operations(request):
    """Handle bulk AI operations."""
    if request.method == 'POST':
        try:
            operation = request.POST.get('operation')
            
            if operation == 'generate_reviews_for_new_tools':
                # Generate reviews for tools added in the last 30 days
                new_tools = Tool.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).exclude(
                    id__in=Article.objects.filter(
                        article_type='tool_review',
                        metadata__tool_id__isnull=False
                    ).values_list('metadata__tool_id', flat=True)
                )[:10]  # Limit to 10 to avoid overwhelming the system
                
                task_ids = []
                for tool in new_tools:
                    task = generate_ai_tool_review.delay(tool.id)
                    task_ids.append(task.id)
                
                messages.success(
                    request, 
                    f'Started generating reviews for {len(new_tools)} tools'
                )
                
            elif operation == 'generate_category_comparisons':
                # Generate comparisons for popular categories
                categories_with_tools = Category.objects.annotate(
                    tool_count=Count('tools')
                ).filter(tool_count__gte=3).order_by('-tool_count')[:3]
                
                comparison_count = 0
                for category in categories_with_tools:
                    tools = list(category.tools.order_by('-github_stars')[:3])
                    if len(tools) >= 2:
                        tool_ids = [tool.id for tool in tools]
                        generate_ai_tool_comparison.delay(tool_ids)
                        comparison_count += 1
                
                messages.success(
                    request,
                    f'Started generating {comparison_count} comparisons'
                )
                
            elif operation == 'generate_all_trend_analyses':
                # Generate trend analyses for all categories with tools
                categories_with_tools = Category.objects.annotate(
                    tool_count=Count('tools')
                ).filter(tool_count__gte=3)
                
                for category in categories_with_tools:
                    generate_trend_analysis.delay(category.id)
                
                messages.success(
                    request,
                    f'Started generating trend analyses for {categories_with_tools.count()} categories'
                )
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('admin:ai_dashboard')


@staff_member_required
def ai_content_analytics(request):
    """Analytics view for AI-generated content performance."""
    
    # AI content statistics
    ai_articles = Article.objects.filter(ai_generated=True)
    
    analytics_data = {
        'total_ai_articles': ai_articles.count(),
        'ai_articles_by_type': ai_articles.values('article_type').annotate(
            count=Count('id')
        ).order_by('-count'),
        'ai_articles_by_provider': ai_articles.values('ai_provider').annotate(
            count=Count('id')
        ).order_by('-count'),
        'ai_articles_by_month': ai_articles.extra(
            select={'month': "strftime('%%Y-%%m', created_at)"}
        ).values('month').annotate(count=Count('id')).order_by('month'),
        'top_ai_categories': Article.objects.filter(
            ai_generated=True
        ).values(
            'categories__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
    }
    
    return render(request, 'admin/ai_analytics.html', {
        'analytics_data': analytics_data
    })
