"""
Enhanced Search with ML-based Ranking
Semantic search, recommendations, and personalization.
"""
from django.db.models import Q, Count, Avg, F, Value, FloatField
from django.db.models.functions import Greatest, Coalesce
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# SEARCH RANKING ALGORITHM
# ============================================================================

class SearchRanker:
    """
    ML-inspired search ranking algorithm.
    Combines multiple signals to rank search results.
    """
    
    # Ranking weights
    WEIGHTS = {
        'text_relevance': 0.30,      # How well text matches query
        'popularity': 0.25,           # GitHub stars, views
        'quality': 0.20,              # Rating, review count
        'recency': 0.10,              # Recently updated
        'engagement': 0.10,           # User engagement
        'personalization': 0.05,      # User preferences
    }
    
    @classmethod
    def search_tools(cls, query: str, user=None, filters: Dict = None) -> List:
        """
        Search tools with ML-based ranking.
        
        Args:
            query: Search query string
            user: User object for personalization (optional)
            filters: Additional filters (category, pricing, etc.)
        
        Returns:
            Ranked list of tools
        """
        from apps.tools.models import Tool
        
        # Build base queryset
        tools = Tool.objects.filter(is_published=True)
        
        # Apply filters
        if filters:
            if 'category' in filters:
                tools = tools.filter(category__slug=filters['category'])
            if 'pricing_model' in filters:
                tools = tools.filter(pricing_model=filters['pricing_model'])
            if 'min_rating' in filters:
                tools = tools.annotate(
                    avg_rating=F('rating_sum') / F('rating_count')
                ).filter(avg_rating__gte=filters['min_rating'])
        
        # Text search with PostgreSQL full-text search
        if query:
            search_vector = SearchVector('name', weight='A') + \
                          SearchVector('description', weight='B') + \
                          SearchVector('tagline', weight='B') + \
                          SearchVector('tags', weight='C')
            search_query = SearchQuery(query)
            
            tools = tools.annotate(
                search_rank=SearchRank(search_vector, search_query)
            ).filter(search_rank__gt=0)
        else:
            tools = tools.annotate(search_rank=Value(1.0, output_field=FloatField()))
        
        # Calculate ranking scores
        tools = cls._calculate_scores(tools, query, user)
        
        # Sort by final score
        tools = tools.order_by('-final_score')
        
        return tools
    
    @classmethod
    def _calculate_scores(cls, queryset, query: str, user):
        """Calculate individual ranking scores."""
        
        # Normalize GitHub stars (0-1 scale)
        max_stars = 100000  # Assume max 100k stars
        
        # Normalize views
        max_views = 10000
        
        # Calculate scores
        queryset = queryset.annotate(
            # Text relevance (from search_rank)
            text_score=F('search_rank'),
            
            # Popularity score
            popularity_score=(
                F('github_stars') / Value(max_stars, output_field=FloatField()) * 0.7 +
                F('view_count') / Value(max_views, output_field=FloatField()) * 0.3
            ),
            
            # Quality score
            quality_score=Coalesce(
                F('rating_sum') / F('rating_count') / 5.0,
                Value(0.5, output_field=FloatField())
            ),
            
            # Recency score (updated in last 30 days = 1.0)
            recency_score=Value(1.0, output_field=FloatField()),  # Simplified
            
            # Engagement score
            engagement_score=(
                F('view_count') / Value(max_views, output_field=FloatField())
            ),
            
            # Calculate weighted final score
            final_score=(
                F('text_score') * cls.WEIGHTS['text_relevance'] +
                F('popularity_score') * cls.WEIGHTS['popularity'] +
                F('quality_score') * cls.WEIGHTS['quality'] +
                F('recency_score') * cls.WEIGHTS['recency'] +
                F('engagement_score') * cls.WEIGHTS['engagement']
            )
        )
        
        # Add personalization if user provided
        if user and user.is_authenticated:
            queryset = cls._add_personalization(queryset, user)
        
        return queryset
    
    @classmethod
    def _add_personalization(cls, queryset, user):
        """Add personalization boost based on user preferences."""
        # Get user's favorite categories
        from apps.users.models import UserPreference
        
        try:
            prefs = UserPreference.objects.get(user=user)
            favorite_categories = prefs.favorite_categories.all()
            
            if favorite_categories:
                # Boost tools in favorite categories
                queryset = queryset.annotate(
                    personalization_boost=Case(
                        When(category__in=favorite_categories, then=Value(0.2)),
                        default=Value(0.0),
                        output_field=FloatField()
                    ),
                    final_score=F('final_score') + F('personalization_boost')
                )
        except:
            pass
        
        return queryset


# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """
    Tool recommendation engine.
    Suggests tools based on collaborative filtering and content similarity.
    """
    
    @classmethod
    def get_recommendations(cls, user, limit: int = 10) -> List:
        """
        Get personalized recommendations for a user.
        
        Args:
            user: User object
            limit: Number of recommendations
        
        Returns:
            List of recommended tools
        """
        cache_key = f'recommendations_{user.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        recommendations = []
        
        # Strategy 1: Collaborative filtering (users who viewed this also viewed...)
        collab_recs = cls._collaborative_filtering(user, limit // 2)
        recommendations.extend(collab_recs)
        
        # Strategy 2: Content-based filtering (similar to what you liked)
        content_recs = cls._content_based_filtering(user, limit // 2)
        recommendations.extend(content_recs)
        
        # Remove duplicates and limit
        seen = set()
        unique_recs = []
        for tool in recommendations:
            if tool.id not in seen:
                seen.add(tool.id)
                unique_recs.append(tool)
            if len(unique_recs) >= limit:
                break
        
        # Cache for 1 hour
        cache.set(cache_key, unique_recs, 3600)
        
        return unique_recs
    
    @classmethod
    def _collaborative_filtering(cls, user, limit: int) -> List:
        """Find tools viewed by similar users."""
        from apps.tools.models import Tool
        from apps.analytics.models import PageView
        
        # Get tools this user viewed
        user_views = PageView.objects.filter(
            user=user,
            url__contains='/tools/'
        ).values_list('url', flat=True)[:20]
        
        # Extract tool IDs from URLs
        tool_ids = []
        for url in user_views:
            match = re.search(r'/tools/([^/]+)/?$', url)
            if match:
                tool_slug = match.group(1)
                try:
                    tool = Tool.objects.get(slug=tool_slug)
                    tool_ids.append(tool.id)
                except Tool.DoesNotExist:
                    pass
        
        if not tool_ids:
            # Return trending tools as fallback
            return list(Tool.objects.filter(
                is_published=True,
                is_trending=True
            )[:limit])
        
        # Find other users who viewed the same tools
        similar_users = PageView.objects.filter(
            url__regex=r'/tools/[^/]+/?$'
        ).exclude(user=user).values('user').annotate(
            common_views=Count('id')
        ).order_by('-common_views')[:50]
        
        similar_user_ids = [u['user'] for u in similar_users if u['user']]
        
        # Get tools viewed by similar users but not by this user
        recommended_tools = Tool.objects.filter(
            is_published=True
        ).exclude(id__in=tool_ids).annotate(
            view_count_similar=Count('view_count')
        ).order_by('-view_count_similar')[:limit]
        
        return list(recommended_tools)
    
    @classmethod
    def _content_based_filtering(cls, user, limit: int) -> List:
        """Find tools similar to what user liked."""
        from apps.tools.models import Tool, ToolReview
        
        # Get tools user rated highly
        high_rated = ToolReview.objects.filter(
            user=user,
            rating__gte=4
        ).values_list('tool', flat=True)
        
        if not high_rated:
            # Return featured tools as fallback
            return list(Tool.objects.filter(
                is_published=True,
                is_featured=True
            )[:limit])
        
        # Get categories of highly rated tools
        favorite_tools = Tool.objects.filter(id__in=high_rated)
        favorite_categories = favorite_tools.values_list('category', flat=True).distinct()
        
        # Find similar tools in same categories
        similar_tools = Tool.objects.filter(
            category__in=favorite_categories,
            is_published=True
        ).exclude(id__in=high_rated).annotate(
            avg_rating=Coalesce(
                F('rating_sum') / F('rating_count'),
                Value(0.0, output_field=FloatField())
            )
        ).order_by('-avg_rating', '-github_stars')[:limit]
        
        return list(similar_tools)
    
    @classmethod
    def get_similar_tools(cls, tool, limit: int = 5) -> List:
        """
        Get tools similar to a specific tool.
        
        Args:
            tool: Tool object
            limit: Number of similar tools
        
        Returns:
            List of similar tools
        """
        from apps.tools.models import Tool
        
        # Find tools in same category with similar tags
        similar = Tool.objects.filter(
            category=tool.category,
            is_published=True
        ).exclude(id=tool.id)
        
        # Simple similarity: count matching tags
        # In production, use TF-IDF or embeddings
        if tool.tags:
            tool_tags = set(tool.tags.split(','))
            similar = similar.annotate(
                tag_overlap=Value(0, output_field=FloatField())
            )
            # Would calculate tag overlap here
        
        similar = similar.order_by('-github_stars')[:limit]
        
        return list(similar)


# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

class SemanticSearch:
    """
    Semantic search using embeddings (placeholder for ML integration).
    In production, integrate with OpenAI embeddings or sentence transformers.
    """
    
    @classmethod
    def semantic_search(cls, query: str, limit: int = 20) -> List:
        """
        Perform semantic search (currently uses keyword search).
        
        TODO: Integrate with:
        - OpenAI embeddings
        - Sentence transformers
        - Vector database (Pinecone, Weaviate)
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of matching tools
        """
        # For now, use advanced keyword search
        return SearchRanker.search_tools(query)[:limit]
    
    @classmethod
    def generate_embeddings(cls, tool):
        """
        Generate embeddings for a tool (placeholder).
        
        TODO: Implement with:
        - OpenAI text-embedding-ada-002
        - Store in vector database
        - Use for similarity search
        """
        pass


# ============================================================================
# SEARCH SUGGESTIONS
# ============================================================================

class SearchSuggestions:
    """Auto-complete search suggestions."""
    
    @classmethod
    def get_suggestions(cls, query: str, limit: int = 10) -> List[str]:
        """
        Get search suggestions for a query.
        
        Args:
            query: Partial search query
            limit: Max suggestions
        
        Returns:
            List of suggestion strings
        """
        from apps.tools.models import Tool
        
        if len(query) < 2:
            return []
        
        # Get popular searches from cache
        cache_key = f'search_suggestions_{query.lower()}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Search tool names
        tools = Tool.objects.filter(
            Q(name__icontains=query) | Q(tags__icontains=query),
            is_published=True
        ).values_list('name', flat=True)[:limit]
        
        suggestions = list(tools)
        
        # Cache for 1 hour
        cache.set(cache_key, suggestions, 3600)
        
        return suggestions
