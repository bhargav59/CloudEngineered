from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count
from django.utils import timezone
from .models import Article, ContentTag
from apps.tools.models import Category


class ArticleListView(ListView):
    """Display all published articles."""
    model = Article
    template_name = 'content/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Article.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        ).select_related('author', 'category')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                pass
        
        # Filter by article type
        article_type = self.request.GET.get('type')
        if article_type and article_type in [choice[0] for choice in Article.ARTICLE_TYPES]:
            queryset = queryset.filter(article_type=article_type)
        
        # Filter by tag
        tag_slug = self.request.GET.get('tag')
        if tag_slug:
            try:
                tag = ContentTag.objects.get(slug=tag_slug)
                queryset = queryset.filter(tags=tag)
            except ContentTag.DoesNotExist:
                pass
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options
        context['categories'] = Category.objects.all().order_by('name')
        context['article_types'] = Article.ARTICLE_TYPES
        context['popular_tags'] = ContentTag.objects.filter(
            usage_count__gt=0
        ).order_by('-usage_count')[:10]
        
        # Current filters
        context['selected_category'] = self.request.GET.get('category')
        context['selected_type'] = self.request.GET.get('type')
        context['selected_tag'] = self.request.GET.get('tag')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Featured articles
        context['featured_articles'] = Article.objects.filter(
            is_published=True,
            is_featured=True,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:3]
        
        context['page_title'] = 'Articles & Reviews'
        context['page_description'] = 'Latest articles, tool reviews, and guides for cloud engineering professionals.'
        return context


class ArticleDetailView(DetailView):
    """Display a specific article."""
    model = Article
    template_name = 'content/article_detail.html'
    context_object_name = 'article'
    
    def get_object(self):
        article = get_object_or_404(
            Article,
            slug=self.kwargs['slug'],
            is_published=True,
            published_at__lte=timezone.now()
        )
        # Increment view count
        article.increment_views()
        return article
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        
        # Get related articles
        related_articles = Article.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        ).exclude(id=article.id)
        
        # Try to find related by category first
        if article.category:
            related_articles = related_articles.filter(category=article.category)
        
        # If not enough articles and article has tags (JSONField is a list)
        if related_articles.count() < 3 and article.tags:
            # article.tags is a list, not a queryset
            related_articles = Article.objects.filter(
                is_published=True,
                published_at__lte=timezone.now()
            ).exclude(id=article.id)
        
        context['related_articles'] = related_articles.order_by('-published_at')[:4]
        
        # Get related tools if this is a tool review
        # related_tools is a JSONField (list of tool IDs), not a relationship
        if article.article_type in ['review', 'comparison'] and article.related_tools:
            from apps.tools.models import Tool
            context['related_tools'] = Tool.objects.filter(
                id__in=article.related_tools,
                is_published=True
            )[:3]
        
        # Navigation
        context['previous_article'] = Article.objects.filter(
            published_at__lt=article.published_at,
            is_published=True
        ).order_by('-published_at').first()
        
        context['next_article'] = Article.objects.filter(
            published_at__gt=article.published_at,
            is_published=True
        ).order_by('published_at').first()
        
        context['page_title'] = article.title
        context['page_description'] = article.excerpt or article.meta_description
        return context


# Function-based views for backward compatibility
def article_list(request):
    """List all articles."""
    view = ArticleListView.as_view()
    return view(request)

def article_detail(request, slug):
    """Show article detail."""
    view = ArticleDetailView.as_view()
    return view(request, slug=slug)
