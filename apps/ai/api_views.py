"""
API Views for AI Content Generation
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q
import logging

from .models import ContentTemplate, ContentGeneration, AIModel, AIProvider
from .services import ContentGenerator, AIServiceError
from .serializers import (
    ContentTemplateSerializer, ContentGenerationSerializer,
    AIModelSerializer, ContentGenerationCreateSerializer
)

logger = logging.getLogger(__name__)


class ContentTemplateListView(APIView):
    """List available content templates"""
    
    def get(self, request):
        templates = ContentTemplate.objects.filter(is_active=True)
        
        # Filter by template type if specified
        template_type = request.query_params.get('type')
        if template_type:
            templates = templates.filter(template_type=template_type)
        
        serializer = ContentTemplateSerializer(templates, many=True)
        return Response(serializer.data)


class ContentGenerationView(APIView):
    """Handle content generation requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Generate new content"""
        serializer = ContentGenerationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template_id = serializer.validated_data['template_id']
        input_data = serializer.validated_data['input_data']
        
        try:
            generator = ContentGenerator()
            generation = generator.generate_from_template(
                template_id=template_id,
                input_data=input_data,
                user_id=request.user.id
            )
            
            response_serializer = ContentGenerationSerializer(generation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except AIServiceError as e:
            logger.error(f"AI service error: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error in content generation: {str(e)}")
            return Response(
                {'error': 'Content generation failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """List user's content generations"""
        generations = ContentGeneration.objects.filter(
            initiated_by=request.user
        ).order_by('-created_at')
        
        # Filter by status if specified
        status_filter = request.query_params.get('status')
        if status_filter:
            generations = generations.filter(status=status_filter)
        
        # Pagination
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * page_size
        end = start + page_size
        
        serializer = ContentGenerationSerializer(generations[start:end], many=True)
        return Response({
            'results': serializer.data,
            'count': generations.count(),
            'page': page,
            'page_size': page_size,
            'has_next': end < generations.count()
        })


class ContentGenerationDetailView(APIView):
    """Handle individual content generation operations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, generation_id):
        """Get content generation details"""
        generation = get_object_or_404(
            ContentGeneration,
            id=generation_id,
            initiated_by=request.user
        )
        
        serializer = ContentGenerationSerializer(generation)
        return Response(serializer.data)
    
    def delete(self, request, generation_id):
        """Delete content generation"""
        generation = get_object_or_404(
            ContentGeneration,
            id=generation_id,
            initiated_by=request.user
        )
        
        generation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def ai_models_list(request):
    """List available AI models"""
    cache_key = 'ai_models_list'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        models = AIModel.objects.filter(
            is_active=True,
            provider__is_active=True
        ).select_related('provider')
        
        serializer = AIModelSerializer(models, many=True)
        cached_data = serializer.data
        cache.set(cache_key, cached_data, 300)  # Cache for 5 minutes
    
    return Response(cached_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_tool_review(request):
    """Generate a quick tool review with minimal input"""
    tool_name = request.data.get('tool_name')
    tool_description = request.data.get('tool_description')
    
    if not tool_name or not tool_description:
        return Response(
            {'error': 'tool_name and tool_description are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Get the tool review template
        template = ContentTemplate.objects.get(
            template_type='tool_review',
            is_active=True
        )
        
        input_data = {
            'tool_name': tool_name,
            'tool_description': tool_description,
            'features': request.data.get('features', 'Not specified'),
            'website_url': request.data.get('website_url', 'Not available'),
            'github_url': request.data.get('github_url', 'Not available'),
            'category': request.data.get('category', 'General')
        }
        
        generator = ContentGenerator()
        generation = generator.generate_from_template(
            template_id=template.id,
            input_data=input_data,
            user_id=request.user.id
        )
        
        serializer = ContentGenerationSerializer(generation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except ContentTemplate.DoesNotExist:
        return Response(
            {'error': 'Tool review template not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except AIServiceError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def generation_status(request, generation_id):
    """Get real-time status of content generation"""
    generation = get_object_or_404(
        ContentGeneration,
        id=generation_id,
        initiated_by=request.user
    )
    
    return Response({
        'id': generation.id,
        'status': generation.status,
        'progress': {
            'pending': generation.status == 'pending',
            'processing': generation.status == 'processing',
            'completed': generation.status == 'completed',
            'failed': generation.status == 'failed'
        },
        'tokens_used': generation.tokens_used,
        'estimated_cost': generation.estimated_cost,
        'error_message': generation.error_message,
        'created_at': generation.created_at,
        'completed_at': generation.completed_at
    })


@api_view(['GET'])
def ai_stats(request):
    """Get AI usage statistics"""
    cache_key = 'ai_stats_overview'
    cached_stats = cache.get(cache_key)
    
    if cached_stats is None:
        total_generations = ContentGeneration.objects.count()
        completed_generations = ContentGeneration.objects.filter(status='completed').count()
        failed_generations = ContentGeneration.objects.filter(status='failed').count()
        
        # Calculate success rate
        success_rate = (completed_generations / total_generations * 100) if total_generations > 0 else 0
        
        # Get active providers and models
        active_providers = AIProvider.objects.filter(is_active=True).count()
        active_models = AIModel.objects.filter(is_active=True, provider__is_active=True).count()
        active_templates = ContentTemplate.objects.filter(is_active=True).count()
        
        cached_stats = {
            'total_generations': total_generations,
            'completed_generations': completed_generations,
            'failed_generations': failed_generations,
            'success_rate': round(success_rate, 1),
            'active_providers': active_providers,
            'active_models': active_models,
            'active_templates': active_templates
        }
        
        cache.set(cache_key, cached_stats, 300)  # Cache for 5 minutes
    
    return Response(cached_stats)
