"""
AI Comparison Bot Views

Real-time tool comparison using AI models.
"""

import json
import time
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView, View
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Tool, ComparisonRequest
from .ai_comparison_service import get_comparison_service

logger = logging.getLogger(__name__)


class ComparisonBotView(TemplateView):
    """
    Main view for the AI-powered comparison bot interface.
    """
    template_name = 'tools/comparison_bot.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all published tools for selection
        tools = Tool.objects.filter(is_published=True).select_related('category').order_by('name')
        
        context['tools'] = tools
        context['categories'] = Tool.objects.filter(
            is_published=True
        ).values_list('category__name', flat=True).distinct()
        
        # Get recent comparisons for suggestions
        recent_comparisons = ComparisonRequest.objects.filter(
            status='completed'
        ).select_related('tool1', 'tool2')[:10]
        
        context['recent_comparisons'] = recent_comparisons
        context['page_title'] = 'AI Tool Comparison Bot'
        context['page_description'] = 'Compare DevOps tools in real-time using AI-powered analysis'
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ComparisonBotAPIView(View):
    """
    API endpoint for generating AI comparisons.
    """
    
    def post(self, request):
        """Generate a real-time comparison between two tools."""
        try:
            # Parse request data
            data = json.loads(request.body)
            
            tool1_id = data.get('tool1_id')
            tool2_id = data.get('tool2_id')
            user_query = data.get('query', 'Compare these tools')
            context = data.get('context', {})
            
            # Validate inputs
            if not tool1_id or not tool2_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Both tools must be selected'
                }, status=400)
            
            if tool1_id == tool2_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Please select two different tools'
                }, status=400)
            
            # Get tools
            tool1 = get_object_or_404(Tool, id=tool1_id, is_published=True)
            tool2 = get_object_or_404(Tool, id=tool2_id, is_published=True)
            
            # Create comparison request
            comparison_request = ComparisonRequest.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=request.session.session_key or 'anonymous',
                tool1=tool1,
                tool2=tool2,
                user_query=user_query,
                comparison_context=context,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            # Mark as processing
            comparison_request.mark_as_processing()
            
            # Prepare tool data for AI
            tool1_data = {
                'name': tool1.name,
                'description': tool1.description,
                'category': tool1.category.name if tool1.category else 'Uncategorized',
                'tags': tool1.tags if isinstance(tool1.tags, list) else [],
                'website': tool1.website_url,
            }
            
            tool2_data = {
                'name': tool2.name,
                'description': tool2.description,
                'category': tool2.category.name if tool2.category else 'Uncategorized',
                'tags': tool2.tags if isinstance(tool2.tags, list) else [],
                'website': tool2.website_url,
            }
            
            # Generate comparison using AI
            start_time = time.time()
            comparison_service = get_comparison_service()
            
            try:
                result = comparison_service.generate_comparison(
                    tool1_data=tool1_data,
                    tool2_data=tool2_data,
                    user_query=user_query,
                    context=context
                )
                
                processing_time = time.time() - start_time
                tokens_used = result.get('metadata', {}).get('tokens_used', 0)
                
                # Mark as completed
                comparison_request.mark_as_completed(
                    result=result,
                    tokens=tokens_used,
                    time_taken=processing_time
                )
                
                return JsonResponse({
                    'success': True,
                    'comparison_id': int(comparison_request.id),
                    'result': result,
                    'processing_time': float(round(processing_time, 2)),
                    'tool1': {'id': int(tool1.id), 'name': tool1.name},
                    'tool2': {'id': int(tool2.id), 'name': tool2.name}
                })
                
            except Exception as e:
                logger.error(f"Error generating comparison: {str(e)}")
                comparison_request.mark_as_failed(str(e))
                
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to generate comparison. Please try again.',
                    'details': str(e)
                }, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in comparison API: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred'
            }, status=500)
    
    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class QuickComparisonAPIView(View):
    """
    API endpoint for quick comparisons (shorter, faster).
    """
    
    def post(self, request):
        """Generate a quick comparison summary."""
        try:
            data = json.loads(request.body)
            
            tool1_id = data.get('tool1_id')
            tool2_id = data.get('tool2_id')
            focus_area = data.get('focus_area', None)
            
            # Get tools
            tool1 = get_object_or_404(Tool, id=tool1_id, is_published=True)
            tool2 = get_object_or_404(Tool, id=tool2_id, is_published=True)
            
            # Generate quick comparison
            comparison_service = get_comparison_service()
            result = comparison_service.generate_quick_comparison(
                tool1_name=tool1.name,
                tool2_name=tool2.name,
                focus_area=focus_area
            )
            
            return JsonResponse({
                'success': True,
                'result': result,
                'tool1': {'id': int(tool1.id), 'name': tool1.name},
                'tool2': {'id': int(tool2.id), 'name': tool2.name}
            })
            
        except Exception as e:
            logger.error(f"Error in quick comparison: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ComparisonSuggestionsAPIView(View):
    """
    API endpoint for getting suggested comparison questions.
    """
    
    def get(self, request):
        """Get suggested questions for comparing two tools."""
        tool1_id = request.GET.get('tool1_id')
        tool2_id = request.GET.get('tool2_id')
        
        if not tool1_id or not tool2_id:
            return JsonResponse({
                'success': False,
                'error': 'Both tool IDs required'
            }, status=400)
        
        try:
            tool1 = get_object_or_404(Tool, id=tool1_id, is_published=True)
            tool2 = get_object_or_404(Tool, id=tool2_id, is_published=True)
            
            comparison_service = get_comparison_service()
            suggestions = comparison_service.suggest_comparison_questions(
                tool1_name=tool1.name,
                tool2_name=tool2.name
            )
            
            return JsonResponse({
                'success': True,
                'suggestions': suggestions
            })
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ComparisonFeedbackAPIView(View):
    """
    API endpoint for submitting feedback on comparisons.
    """
    
    def post(self, request):
        """Submit feedback for a comparison."""
        try:
            data = json.loads(request.body)
            
            comparison_id = data.get('comparison_id')
            helpful = data.get('helpful', None)
            comment = data.get('comment', '')
            
            if comparison_id is None or helpful is None:
                return JsonResponse({
                    'success': False,
                    'error': 'comparison_id and helpful are required'
                }, status=400)
            
            comparison = get_object_or_404(ComparisonRequest, id=comparison_id)
            comparison.record_feedback(helpful=bool(helpful), comment=comment)
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your feedback!'
            })
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class ComparisonHistoryView(TemplateView):
    """
    View for displaying user's comparison history.
    """
    template_name = 'tools/comparison_history.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's comparison history
        comparisons = ComparisonRequest.objects.filter(
            user=self.request.user,
            status='completed'
        ).select_related('tool1', 'tool2').order_by('-created_at')[:50]
        
        context['comparisons'] = comparisons
        context['page_title'] = 'Your Comparison History'
        
        return context


class ToolSearchAPIView(View):
    """
    API endpoint for searching tools (for autocomplete).
    """
    
    def get(self, request):
        """Search for tools by name."""
        query = request.GET.get('q', '')
        
        if len(query) < 2:
            return JsonResponse({
                'success': True,
                'results': []
            })
        
        tools = Tool.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_published=True
        ).select_related('category')[:20]
        
        results = [
            {
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.name,
                'description': tool.description[:100] + '...' if len(tool.description) > 100 else tool.description
            }
            for tool in tools
        ]
        
        return JsonResponse({
            'success': True,
            'results': results
        })
