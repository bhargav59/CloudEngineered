"""
AI Integration for Tools App
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.ai.models import ContentTemplate, ContentGeneration
from apps.ai.services import ContentGenerator
from .models import Tool
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_tool_content(request, tool_id):
    """Generate AI content for a specific tool"""
    
    tool = get_object_or_404(Tool, id=tool_id)
    content_type = request.data.get('content_type', 'review')
    template_id = request.data.get('template_id')
    
    # Map content types to template types
    template_type_map = {
        'review': 'tool_review',
        'tutorial': 'tutorial',
        'guide': 'how_to_guide',
        'comparison': 'comparison'
    }
    
    template_type = template_type_map.get(content_type, 'tool_review')
    
    # Get template
    if template_id:
        try:
            template = ContentTemplate.objects.get(
                id=template_id,
                is_active=True
            )
        except ContentTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        template = ContentTemplate.objects.filter(
            template_type=template_type,
            is_active=True
        ).first()
        
        if not template:
            return Response(
                {'error': f'No {content_type} template available'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Prepare input data based on tool information
    input_data = {
        'tool_name': tool.name,
        'tool_description': tool.description,
        'category': tool.category.name if tool.category else 'General',
        'website_url': tool.website_url or '',
        'github_url': tool.github_url or '',
        'pricing': getattr(tool, 'pricing_type', 'Unknown'),
        'features': tool.description,  # Using description as features for now
        'target_audience': request.data.get('target_audience', 'developers'),
        'use_cases': request.data.get('use_cases', ''),
        'alternatives': request.data.get('alternatives', ''),
        'pros_cons': request.data.get('pros_cons', '')
    }
    
    # Add any custom input data from request
    custom_data = request.data.get('custom_data', {})
    if isinstance(custom_data, dict):
        input_data.update(custom_data)
    
    # Create content generation record
    generation = ContentGeneration.objects.create(
        template=template,
        initiated_by=request.user,
        input_data=input_data,
        status='processing'
    )
    
    try:
        # Generate content
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
        generation.save()
        
        return Response({
            'generation_id': generation.id,
            'tool_id': tool.id,
            'tool_name': tool.name,
            'content_type': content_type,
            'status': 'completed',
            'content': generation.generated_content,
            'tokens_used': generation.tokens_used,
            'estimated_cost': str(generation.estimated_cost),
            'processing_time': generation.processing_time
        })
        
    except Exception as e:
        logger.error(f"Tool content generation failed for tool {tool.id}: {str(e)}")
        generation.status = 'failed'
        generation.error_message = str(e)
        generation.save()
        
        return Response(
            {'error': f'Content generation failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_generate_reviews(request):
    """Generate reviews for multiple tools"""
    
    tool_ids = request.data.get('tool_ids', [])
    template_id = request.data.get('template_id')
    
    if not tool_ids:
        return Response(
            {'error': 'No tool IDs provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get template
    if template_id:
        try:
            template = ContentTemplate.objects.get(
                id=template_id,
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
    
    # Get tools
    tools = Tool.objects.filter(id__in=tool_ids)
    if not tools.exists():
        return Response(
            {'error': 'No valid tools found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    results = []
    generator = ContentGenerator()
    
    for tool in tools:
        input_data = {
            'tool_name': tool.name,
            'tool_description': tool.description,
            'category': tool.category.name if tool.category else 'General',
            'website_url': tool.website_url or '',
            'github_url': tool.github_url or '',
            'pricing': getattr(tool, 'pricing_type', 'Unknown'),
            'features': tool.description
        }
        
        # Create generation record
        generation = ContentGeneration.objects.create(
            template=template,
            initiated_by=request.user,
            input_data=input_data,
            status='processing'
        )
        
        try:
            # Generate content
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
            generation.save()
            
            results.append({
                'tool_id': tool.id,
                'tool_name': tool.name,
                'generation_id': generation.id,
                'status': 'completed',
                'tokens_used': generation.tokens_used,
                'estimated_cost': str(generation.estimated_cost)
            })
            
        except Exception as e:
            logger.error(f"Bulk review generation failed for tool {tool.id}: {str(e)}")
            generation.status = 'failed'
            generation.error_message = str(e)
            generation.save()
            
            results.append({
                'tool_id': tool.id,
                'tool_name': tool.name,
                'generation_id': generation.id,
                'status': 'failed',
                'error': str(e)
            })
    
    # Calculate summary statistics
    successful = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    total_tokens = sum(int(r.get('tokens_used', 0)) for r in successful)
    total_cost = sum(float(r.get('estimated_cost', 0)) for r in successful)
    
    return Response({
        'summary': {
            'total_tools': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_tokens_used': total_tokens,
            'total_estimated_cost': str(total_cost)
        },
        'results': results
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tool_ai_content_history(request, tool_id):
    """Get AI content generation history for a tool"""
    
    tool = get_object_or_404(Tool, id=tool_id)
    
    # Get all generations that mention this tool
    generations = ContentGeneration.objects.filter(
        input_data__icontains=tool.name
    ).select_related('template', 'initiated_by').order_by('-created_at')
    
    # Filter by user if requested
    if request.query_params.get('my_content_only') == 'true':
        generations = generations.filter(initiated_by=request.user)
    
    # Filter by content type
    content_type = request.query_params.get('content_type')
    if content_type:
        template_type_map = {
            'review': 'tool_review',
            'tutorial': 'tutorial',
            'guide': 'how_to_guide',
            'comparison': 'comparison'
        }
        template_type = template_type_map.get(content_type)
        if template_type:
            generations = generations.filter(template__template_type=template_type)
    
    results = []
    for generation in generations:
        results.append({
            'generation_id': generation.id,
            'template_name': generation.template.name,
            'template_type': generation.template.template_type,
            'content_type': generation.template.get_template_type_display(),
            'status': generation.status,
            'generated_by': generation.initiated_by.username,
            'tokens_used': generation.tokens_used,
            'estimated_cost': str(generation.estimated_cost) if generation.estimated_cost else '0',
            'created_at': generation.created_at,
            'completed_at': generation.completed_at,
            'has_content': bool(generation.generated_content),
            'content_preview': generation.generated_content[:200] + '...' if len(generation.generated_content) > 200 else generation.generated_content
        })
    
    return Response({
        'tool_id': tool.id,
        'tool_name': tool.name,
        'total_generations': len(results),
        'generations': results
    })
