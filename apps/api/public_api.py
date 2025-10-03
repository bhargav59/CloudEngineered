"""
Public API for CloudTools Platform
RESTful API with rate limiting and authentication.
"""
from rest_framework import serializers, viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from apps.tools.models import Tool, ToolComparison, ToolReview, Category
from apps.ai.models import AIModel
from apps.monetization.models import PremiumTier


# ============================================================================
# SERIALIZERS
# ============================================================================

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer."""
    tool_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'tool_count']
    
    def get_tool_count(self, obj):
        return obj.tools.filter(is_published=True).count()


class ToolListSerializer(serializers.ModelSerializer):
    """Lightweight tool serializer for lists."""
    category = serializers.StringRelatedField()
    
    class Meta:
        model = Tool
        fields = [
            'id', 'name', 'slug', 'tagline', 'description',
            'category', 'logo', 'website_url', 'pricing_model',
            'github_stars', 'github_forks', 'rating_sum', 'rating_count',
            'view_count', 'is_featured', 'is_trending'
        ]


class ToolDetailSerializer(serializers.ModelSerializer):
    """Detailed tool serializer."""
    category = CategorySerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Tool
        fields = [
            'id', 'name', 'slug', 'tagline', 'description', 'detailed_description',
            'category', 'tags', 'logo', 'screenshot', 'screenshots',
            'website_url', 'github_url', 'documentation_url',
            'pricing_model', 'pricing_tiers', 'free_tier_available',
            'deployment_types', 'supported_platforms', 'languages',
            'features', 'integrations', 'use_cases', 'tech_stack',
            'pros', 'cons',
            'github_stars', 'github_forks', 'github_watchers',
            'github_contributors', 'github_latest_release',
            'performance_score', 'performance_metrics',
            'community_size', 'documentation_quality',
            'security_features', 'compliance_certifications',
            'rating_sum', 'rating_count', 'average_rating',
            'view_count', 'is_featured', 'is_trending',
            'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        if obj.rating_count > 0:
            return round(obj.rating_sum / obj.rating_count, 1)
        return 0


class ToolComparisonSerializer(serializers.ModelSerializer):
    """Tool comparison serializer."""
    tools = ToolListSerializer(many=True, read_only=True)
    
    class Meta:
        model = ToolComparison
        fields = [
            'id', 'title', 'slug', 'description', 'tools',
            'introduction', 'conclusion', 'recommendation',
            'feature_matrix', 'tool_analysis',
            'view_count', 'is_published', 'created_at', 'updated_at'
        ]


class ToolReviewSerializer(serializers.ModelSerializer):
    """Tool review serializer."""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = ToolReview
        fields = [
            'id', 'tool', 'user', 'title', 'content', 'rating',
            'usage_duration', 'use_case', 'is_verified',
            'helpful_count', 'created_at'
        ]
        read_only_fields = ['user', 'helpful_count', 'is_verified']


class PremiumTierSerializer(serializers.ModelSerializer):
    """Premium tier serializer."""
    
    class Meta:
        model = PremiumTier
        fields = [
            'id', 'name', 'slug', 'description',
            'price_monthly', 'price_yearly', 'discount_percentage',
            'features', 'is_featured', 'sort_order'
        ]


class AIModelSerializer(serializers.ModelSerializer):
    """AI Model serializer."""
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'provider', 'display_name',
            'max_tokens', 'is_active'
        ]


# ============================================================================
# PAGINATION
# ============================================================================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================================================
# THROTTLING
# ============================================================================

class BurstRateThrottle(UserRateThrottle):
    """Burst rate throttle: 60 requests per minute."""
    rate = '60/min'


class SustainedRateThrottle(UserRateThrottle):
    """Sustained rate throttle: 1000 requests per hour."""
    rate = '1000/hour'


class AnonBurstRateThrottle(AnonRateThrottle):
    """Anonymous burst rate: 20 requests per minute."""
    rate = '20/min'


class AnonSustainedRateThrottle(AnonRateThrottle):
    """Anonymous sustained rate: 100 requests per hour."""
    rate = '100/hour'


# ============================================================================
# VIEWSETS
# ============================================================================

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories.
    
    list: Get all categories
    retrieve: Get a specific category by ID or slug
    tools: Get tools in a category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstRateThrottle, AnonSustainedRateThrottle]
    lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination
    
    @action(detail=True, methods=['get'])
    def tools(self, request, slug=None):
        """Get tools in a category."""
        category = self.get_object()
        tools = Tool.objects.filter(
            category=category,
            is_published=True
        ).order_by('-github_stars')
        
        page = self.paginate_queryset(tools)
        if page is not None:
            serializer = ToolListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ToolListSerializer(tools, many=True)
        return Response(serializer.data)


class ToolViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tools.
    
    list: Get all published tools
    retrieve: Get a specific tool by ID or slug
    search: Search tools by name/description
    trending: Get trending tools
    featured: Get featured tools
    reviews: Get reviews for a tool
    similar: Get similar tools
    """
    queryset = Tool.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstRateThrottle, AnonSustainedRateThrottle]
    lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'pricing_model', 'is_featured', 'is_trending']
    search_fields = ['name', 'description', 'tagline', 'tags']
    ordering_fields = ['github_stars', 'view_count', 'rating_sum', 'created_at']
    ordering = ['-github_stars']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ToolListSerializer
        return ToolDetailSerializer
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending tools."""
        tools = self.get_queryset().filter(is_trending=True)[:20]
        serializer = ToolListSerializer(tools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured tools."""
        tools = self.get_queryset().filter(is_featured=True)[:20]
        serializer = ToolListSerializer(tools, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, slug=None):
        """Get reviews for a tool."""
        tool = self.get_object()
        reviews = ToolReview.objects.filter(tool=tool).order_by('-created_at')
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ToolReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ToolReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def similar(self, request, slug=None):
        """Get similar tools based on category and tags."""
        tool = self.get_object()
        
        # Find similar tools by category and overlapping tags
        similar_tools = Tool.objects.filter(
            category=tool.category,
            is_published=True
        ).exclude(id=tool.id)[:10]
        
        serializer = ToolListSerializer(similar_tools, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, slug=None):
        """Create a review for a tool."""
        tool = self.get_object()
        
        serializer = ToolReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tool=tool, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ComparisonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tool comparisons.
    
    list: Get all published comparisons
    retrieve: Get a specific comparison
    create_comparison: Create a new comparison request
    """
    queryset = ToolComparison.objects.filter(is_published=True)
    serializer_class = ToolComparisonSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstRateThrottle, AnonSustainedRateThrottle]
    lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination
    
    @action(detail=False, methods=['post'])
    def create_comparison(self, request):
        """
        Create a new comparison request.
        
        POST /api/comparisons/create_comparison/
        {
            "tool_ids": [1, 2, 3],
            "user_query": "Which is best for startups?"
        }
        """
        tool_ids = request.data.get('tool_ids', [])
        user_query = request.data.get('user_query', '')
        
        if len(tool_ids) < 2:
            return Response(
                {'error': 'At least 2 tools required for comparison'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tools = Tool.objects.filter(id__in=tool_ids, is_published=True)
        if tools.count() != len(tool_ids):
            return Response(
                {'error': 'One or more tools not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create comparison request (would trigger async processing)
        from apps.tools.models import ComparisonRequest
        
        comparison_request = ComparisonRequest.objects.create(
            tool1=tools[0],
            tool2=tools[1],
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or 'api',
            user_query=user_query,
            status='pending'
        )
        
        # Trigger async comparison generation
        from apps.automation.tasks import generate_tool_comparison
        generate_tool_comparison.delay(tool_ids, user_query)
        
        return Response({
            'request_id': comparison_request.id,
            'status': 'pending',
            'message': 'Comparison is being generated. Check back soon!'
        }, status=status.HTTP_202_ACCEPTED)


class PricingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for premium pricing tiers.
    
    list: Get all available pricing tiers
    """
    queryset = PremiumTier.objects.filter(is_active=True).order_by('sort_order')
    serializer_class = PremiumTierSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstRateThrottle, AnonSustainedRateThrottle]


class AIModelsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for AI models.
    
    list: Get all available AI models
    """
    queryset = AIModel.objects.filter(is_active=True)  # Changed from is_available to is_active
    serializer_class = AIModelSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonBurstRateThrottle, AnonSustainedRateThrottle]


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API root endpoint with links to all resources.
    """
    return Response({
        'message': 'Welcome to CloudTools API',
        'version': '1.0',
        'endpoints': {
            'categories': '/api/categories/',
            'tools': '/api/tools/',
            'comparisons': '/api/comparisons/',
            'pricing': '/api/pricing/',
            'ai_models': '/api/ai-models/',
        },
        'documentation': '/api/docs/',
        'authentication': {
            'token_auth': '/api/auth/token/',
            'refresh': '/api/auth/refresh/',
        },
        'rate_limits': {
            'authenticated': '1000 requests/hour',
            'anonymous': '100 requests/hour',
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint."""
    from django.db import connection
    from django.utils import timezone
    
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {
                'database': 'ok',
                'api': 'ok',
            }
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Get stats for the authenticated user."""
    user = request.user
    
    # Get user's activity stats
    bookmarks_count = user.bookmarks.count() if hasattr(user, 'bookmarks') else 0
    reviews_count = user.tool_reviews.count()
    
    return Response({
        'username': user.username,
        'email': user.email,
        'bookmarks': bookmarks_count,
        'reviews': reviews_count,
        'member_since': user.date_joined.isoformat(),
    })
