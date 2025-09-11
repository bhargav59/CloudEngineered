"""
API Views for AI Content Generation
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    AIProvider, AIModel, ContentTemplate, ContentGeneration,
    ContentQuality, AIUsageStatistics
)
from .serializers import (
    AIProviderSerializer, AIModelSerializer, ContentTemplateSerializer,
    ContentGenerationSerializer, ContentGenerationCreateSerializer,
    ContentGenerationUpdateSerializer, AIUsageStatisticsSerializer,
    QuickToolReviewSerializer, ContentGenerationStatsSerializer,
    ContentQualitySerializer
)
from .services import ContentGenerator
from apps.tools.models import Tool
from apps.content.models import Article

logger = logging.getLogger(__name__)


@login_required
def ai_dashboard(request):
    """AI Dashboard view"""
    context = {
        'title': 'AI Content Generation',
        'total_templates': ContentTemplate.objects.filter(is_active=True).count(),
        'total_providers': AIProvider.objects.filter(is_active=True).count(),
        'total_models': AIModel.objects.filter(is_active=True).count(),
    }
    return render(request, 'ai/dashboard.html', context)


class AIProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Providers"""
    queryset = AIProvider.objects.filter(is_active=True)
    serializer_class = AIProviderSerializer
    permission_classes = [IsAuthenticated]


class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Models"""
    queryset = AIModel.objects.filter(is_active=True).select_related('provider')
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        return queryset


class ContentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Content Templates"""
    queryset = ContentTemplate.objects.filter(is_active=True).select_related('model__provider')
    serializer_class = ContentTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        template_type = self.request.query_params.get('type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        return queryset


class ContentGenerationViewSet(viewsets.ModelViewSet):
    """ViewSet for Content Generation"""
    queryset = ContentGeneration.objects.all().select_related(
        'template__model__provider', 'initiated_by', 'quality'
    ).order_by('-created_at')
    serializer_class = ContentGenerationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContentGenerationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ContentGenerationUpdateSerializer
        return ContentGenerationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user's own generations
        queryset = queryset.filter(initiated_by=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by template type
        template_type = self.request.query_params.get('template_type')
        if template_type:
            queryset = queryset.filter(template__template_type=template_type)
        
        return queryset

    def perform_create(self, serializer):
        template_id = serializer.validated_data['template_id']
        input_data = serializer.validated_data['input_data']
        
        template = ContentTemplate.objects.get(id=template_id)
        
        # Create the generation record
        generation = ContentGeneration.objects.create(
            template=template,
            initiated_by=self.request.user,
            input_data=input_data,
            status='pending'
        )
        
        # Start content generation asynchronously
        try:
            generator = ContentGenerator()
            result = generator.generate_content(
                template=template,
                input_data=input_data,
                user=self.request.user
            )
            
            # Update the generation record
            generation.status = 'completed'
            generation.generated_content = result.get('content', '')
            generation.tokens_used = result.get('tokens_used', 0)
            generation.estimated_cost = result.get('cost', 0)
            generation.processing_time = result.get('processing_time', 0)
            generation.completed_at = timezone.now()
            generation.save()
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save()

    @action(detail=False, methods=['post'])
    def generate_tool_review(self, request):
        """Generate a tool review for a specific tool"""
        tool_id = request.data.get('tool_id')
        custom_template_id = request.data.get('template_id')
        
        try:
            tool = Tool.objects.get(id=tool_id)
        except Tool.DoesNotExist:
            return Response(
                {'error': 'Tool not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or use default tool review template
        if custom_template_id:
            try:
                template = ContentTemplate.objects.get(
                    id=custom_template_id, 
                    template_type='tool_review',
                    is_active=True
                )
            except ContentTemplate.DoesNotExist:
                return Response(
                    {'error': 'Template not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            template = ContentTemplate.objects.filter(
                template_type='tool_review',
                is_active=True
            ).first()
            
            if not template:
                return Response(
                    {'error': 'No tool review template available'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Prepare input data
        input_data = {
            'tool_name': tool.name,
            'tool_description': tool.description,
            'features': getattr(tool, 'features', ''),
            'category': tool.category.name if tool.category else '',
            'website_url': tool.website_url or '',
            'github_url': tool.github_url or '',
            'pricing': tool.pricing_type if hasattr(tool, 'pricing_type') else 'Unknown'
        }
        
        # Create generation record
        generation = ContentGeneration.objects.create(
            template=template,
            initiated_by=request.user,
            input_data=input_data,
            status='processing'
        )
        
        # Generate content
        try:
            generator = ContentGenerator()
            result = generator.generate_content(
                template=template,
                input_data=input_data,
                user=request.user
            )
            
            # Update generation record
            generation.status = 'completed'
            generation.generated_content = result.get('content', '')
            generation.tokens_used = result.get('tokens_used', 0)
            generation.estimated_cost = result.get('cost', 0)
            generation.processing_time = result.get('processing_time', 0)
            generation.completed_at = timezone.now()
            generation.save()
            
            return Response({
                'generation_id': generation.id,
                'status': 'completed',
                'content': generation.generated_content,
                'tokens_used': generation.tokens_used,
                'estimated_cost': str(generation.estimated_cost)
            })
            
        except Exception as e:
            logger.error(f"Tool review generation failed: {str(e)}")
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save()
            
            return Response(
                {'error': f'Generation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_quick_review(self, request):
        """Generate a quick review from tool data"""
        serializer = QuickToolReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get default tool review template
        template = ContentTemplate.objects.filter(
            template_type='tool_review',
            is_active=True
        ).first()
        
        if not template:
            return Response(
                {'error': 'No tool review template available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create generation record
        generation = ContentGeneration.objects.create(
            template=template,
            initiated_by=request.user,
            input_data=serializer.validated_data,
            status='processing'
        )
        
        # Generate content
        try:
            generator = ContentGenerator()
            result = generator.generate_content(
                template=template,
                input_data=serializer.validated_data,
                user=request.user
            )
            
            # Update generation record
            generation.status = 'completed'
            generation.generated_content = result.get('content', '')
            generation.tokens_used = result.get('tokens_used', 0)
            generation.estimated_cost = result.get('cost', 0)
            generation.processing_time = result.get('processing_time', 0)
            generation.completed_at = timezone.now()
            generation.save()
            
            return Response({
                'generation_id': generation.id,
                'status': 'completed',
                'content': generation.generated_content,
                'tokens_used': generation.tokens_used,
                'estimated_cost': str(generation.estimated_cost)
            })
            
        except Exception as e:
            logger.error(f"Quick review generation failed: {str(e)}")
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save()
            
            return Response(
                {'error': f'Generation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get content generation statistics"""
        # Calculate statistics for the user
        user_generations = ContentGeneration.objects.filter(initiated_by=request.user)
        
        total_generations = user_generations.count()
        completed_generations = user_generations.filter(status='completed').count()
        failed_generations = user_generations.filter(status='failed').count()
        
        success_rate = (completed_generations / total_generations * 100) if total_generations > 0 else 0
        
        # Aggregate data
        aggregates = user_generations.filter(status='completed').aggregate(
            total_tokens=Sum('tokens_used'),
            total_cost=Sum('estimated_cost'),
            avg_processing_time=Avg('processing_time')
        )
        
        # Breakdown by template type
        by_template_type = {}
        template_stats = user_generations.values('template__template_type').annotate(
            count=Count('id')
        )
        for stat in template_stats:
            by_template_type[stat['template__template_type']] = stat['count']
        
        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_activity = []
        for i in range(7):
            day = seven_days_ago + timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_count = user_generations.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            recent_activity.append({
                'date': day_start.date().isoformat(),
                'count': day_count
            })
        
        stats_data = {
            'total_generations': total_generations,
            'completed_generations': completed_generations,
            'failed_generations': failed_generations,
            'success_rate': round(success_rate, 2),
            'total_tokens_used': aggregates['total_tokens'] or 0,
            'total_cost': aggregates['total_cost'] or 0,
            'average_processing_time': round(aggregates['avg_processing_time'] or 0, 2),
            'by_template_type': by_template_type,
            'recent_activity': recent_activity
        }
        
        serializer = ContentGenerationStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)


class AIUsageStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Usage Statistics"""
    queryset = AIUsageStatistics.objects.all().select_related('provider', 'model')
    serializer_class = AIUsageStatisticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by provider
        provider_id = self.request.query_params.get('provider')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)
        
        return queryset.order_by('-date')
