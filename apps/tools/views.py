from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Category, Tool, ToolComparison, ToolReview
from apps.content.models import Article


class CategoryListView(ListView):
    """Display all tool categories."""
    model = Category
    template_name = 'tools/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(
            is_active=True
        ).annotate(
            tool_count=Count('tools', filter=Q(tools__is_published=True))
        ).order_by('sort_order', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_categories'] = self.get_queryset().filter(is_featured=True)[:6]
        context['page_title'] = 'Tool Categories'
        context['page_description'] = 'Browse tools by category - from CI/CD to monitoring and security.'
        return context


class ToolListView(ListView):
    """Display tools in a specific category."""
    model = Tool
    template_name = 'tools/tool_list.html'
    context_object_name = 'tools'
    paginate_by = 20
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category'])
        queryset = Tool.objects.filter(
            category=self.category,
            is_published=True
        ).select_related('category').prefetch_related('reviews')
        
        # Add search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Add sorting
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', 'name')
        elif sort_by == 'popularity':
            queryset = queryset.order_by('-view_count', 'name')
        elif sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('name')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', 'name')
        context['page_title'] = f'{self.category.name} Tools'
        context['page_description'] = f'Discover and compare {self.category.name.lower()} tools.'
        return context


class ToolDetailView(DetailView):
    """Display detailed information about a specific tool."""
    model = Tool
    template_name = 'tools/tool_detail.html'
    context_object_name = 'tool'
    
    def get_object(self):
        category = get_object_or_404(Category, slug=self.kwargs['category'])
        tool = get_object_or_404(
            Tool, 
            category=category,
            slug=self.kwargs['slug'],
            is_published=True
        )
        # Increment view count
        tool.increment_view_count()
        return tool
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tool = self.object
        
        # Get related tools
        context['related_tools'] = Tool.objects.filter(
            category=tool.category,
            is_published=True
        ).exclude(id=tool.id)[:4]
        
        # Get reviews
        context['reviews'] = tool.reviews.filter(is_published=True).order_by('-created_at')[:5]
        context['review_count'] = tool.reviews.filter(is_published=True).count()
        
        # Get related articles
        context['related_articles'] = Article.objects.filter(
            Q(related_tools=tool) | Q(category=tool.category),
            is_published=True,
            published_at__isnull=False
        ).distinct().order_by('-published_at')[:3]
        
        context['page_title'] = f'{tool.name} - {tool.category.name} Tool'
        context['page_description'] = tool.description[:160]
        return context


class ComparisonListView(ListView):
    """Display tool comparisons."""
    model = ToolComparison
    template_name = 'tools/comparison_list.html'
    context_object_name = 'comparisons'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = ToolComparison.objects.filter(
            is_published=True
        ).prefetch_related('tools')
        
        # Filter by tool category if specified
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(tools__category=category).distinct()
            except Category.DoesNotExist:
                pass
        
        return queryset.order_by('-updated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        context['selected_category'] = self.request.GET.get('category')
        context['page_title'] = 'Tool Comparisons'
        context['page_description'] = 'Compare tools side-by-side to make informed decisions.'
        return context


# Function-based views for backward compatibility
def category_list(request):
    """List all tool categories."""
    view = CategoryListView.as_view()
    return view(request)

def tool_list(request, category):
    """List tools in a category."""
    view = ToolListView.as_view()
    return view(request, category=category)

def tool_detail(request, category, slug):
    """Show tool detail."""
    view = ToolDetailView.as_view()
    return view(request, category=category, slug=slug)

def comparison_list(request):
    """List tool comparisons."""
    view = ComparisonListView.as_view()
    return view(request)
