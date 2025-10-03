"""
User Dashboard Views
Analytics, subscriptions, bookmarks, and activity tracking.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.tools.models import Tool, ToolReview, ToolComparison
from apps.monetization.models import PremiumSubscription, Commission
from apps.analytics.models import PageView


@login_required
def dashboard_home(request):
    """
    Main dashboard view with overview stats.
    """
    user = request.user
    
    # Get user's subscription status
    subscription = None
    try:
        subscription = PremiumSubscription.objects.get(
            user=user,
            status='active'
        )
    except PremiumSubscription.DoesNotExist:
        pass
    
    # Get user's activity stats
    reviews_count = ToolReview.objects.filter(user=user).count()
    bookmarks_count = 0
    if hasattr(user, 'bookmarks'):
        bookmarks_count = user.bookmarks.count()
    
    # Get recent comparisons
    recent_comparisons = ToolComparison.objects.filter(
        created_by=user
    ).order_by('-created_at')[:5]
    
    # Get page views (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    page_views = PageView.objects.filter(
        user=user,
        timestamp__gte=thirty_days_ago
    ).count()
    
    # Get commission earnings (if affiliate)
    total_earnings = Commission.objects.filter(
        affiliate_program__affiliate_network__user=user,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'subscription': subscription,
        'reviews_count': reviews_count,
        'bookmarks_count': bookmarks_count,
        'recent_comparisons': recent_comparisons,
        'page_views': page_views,
        'total_earnings': total_earnings,
    }
    
    return render(request, 'users/dashboard/home.html', context)


@login_required
def dashboard_analytics(request):
    """
    Analytics dashboard with detailed stats.
    """
    user = request.user
    
    # Time range selection
    range_days = int(request.GET.get('range', 30))
    start_date = timezone.now() - timedelta(days=range_days)
    
    # Page views over time
    page_views = PageView.objects.filter(
        user=user,
        timestamp__gte=start_date
    ).values('timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')
    
    # Most viewed tools
    tool_views = PageView.objects.filter(
        user=user,
        timestamp__gte=start_date,
        url__contains='/tools/'
    ).values('url').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Activity breakdown
    activity = {
        'reviews': ToolReview.objects.filter(
            user=user,
            created_at__gte=start_date
        ).count(),
        'comparisons': ToolComparison.objects.filter(
            created_by=user,
            created_at__gte=start_date
        ).count(),
        'page_views': PageView.objects.filter(
            user=user,
            timestamp__gte=start_date
        ).count(),
    }
    
    context = {
        'range_days': range_days,
        'page_views': list(page_views),
        'tool_views': tool_views,
        'activity': activity,
    }
    
    return render(request, 'users/dashboard/analytics.html', context)


@login_required
def dashboard_subscriptions(request):
    """
    Subscription management dashboard.
    """
    user = request.user
    
    # Get current subscription
    subscription = None
    try:
        subscription = PremiumSubscription.objects.get(
            user=user,
            status='active'
        )
    except PremiumSubscription.DoesNotExist:
        pass
    
    # Get subscription history
    subscription_history = PremiumSubscription.objects.filter(
        user=user
    ).order_by('-created_at')
    
    # Get available tiers
    from apps.monetization.models import PremiumTier
    available_tiers = PremiumTier.objects.filter(
        is_active=True
    ).order_by('sort_order')
    
    context = {
        'subscription': subscription,
        'subscription_history': subscription_history,
        'available_tiers': available_tiers,
    }
    
    return render(request, 'users/dashboard/subscriptions.html', context)


@login_required
def dashboard_bookmarks(request):
    """
    User's bookmarked tools.
    """
    user = request.user
    
    bookmarks = []
    if hasattr(user, 'bookmarks'):
        bookmarks = user.bookmarks.filter(
            is_published=True
        ).order_by('-created_at')
    
    context = {
        'bookmarks': bookmarks,
    }
    
    return render(request, 'users/dashboard/bookmarks.html', context)


@login_required
def dashboard_reviews(request):
    """
    User's tool reviews.
    """
    user = request.user
    
    reviews = ToolReview.objects.filter(
        user=user
    ).select_related('tool').order_by('-created_at')
    
    # Calculate stats
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    helpful_count = reviews.aggregate(total=Sum('helpful_count'))['total'] or 0
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
        'helpful_count': helpful_count,
    }
    
    return render(request, 'users/dashboard/reviews.html', context)


@login_required
def dashboard_comparisons(request):
    """
    User's tool comparisons.
    """
    user = request.user
    
    comparisons = ToolComparison.objects.filter(
        created_by=user
    ).prefetch_related('tools').order_by('-created_at')
    
    context = {
        'comparisons': comparisons,
    }
    
    return render(request, 'users/dashboard/comparisons.html', context)


@login_required
def dashboard_affiliate(request):
    """
    Affiliate earnings dashboard.
    """
    user = request.user
    
    # Get user's affiliate programs
    from apps.monetization.models import AffiliateNetwork, AffiliateProgram
    
    networks = AffiliateNetwork.objects.filter(user=user)
    programs = AffiliateProgram.objects.filter(
        affiliate_network__in=networks
    )
    
    # Calculate earnings
    total_earnings = Commission.objects.filter(
        affiliate_program__in=programs,
        status='paid'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_earnings = Commission.objects.filter(
        affiliate_program__in=programs,
        status='pending'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Recent commissions
    recent_commissions = Commission.objects.filter(
        affiliate_program__in=programs
    ).select_related('affiliate_program', 'tool').order_by('-created_at')[:20]
    
    # Monthly breakdown
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_earnings = Commission.objects.filter(
        affiliate_program__in=programs,
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        total=Sum('amount')
    ).order_by('created_at__date')
    
    context = {
        'networks': networks,
        'programs': programs,
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'recent_commissions': recent_commissions,
        'monthly_earnings': list(monthly_earnings),
    }
    
    return render(request, 'users/dashboard/affiliate.html', context)


@login_required
def dashboard_settings(request):
    """
    User settings and preferences.
    """
    user = request.user
    
    if request.method == 'POST':
        # Handle settings update
        # Email notifications
        user.profile.email_notifications = request.POST.get('email_notifications') == 'on'
        user.profile.newsletter_subscribed = request.POST.get('newsletter') == 'on'
        
        # Preferences
        if request.POST.get('favorite_categories'):
            from apps.tools.models import Category
            category_ids = request.POST.getlist('favorite_categories')
            categories = Category.objects.filter(id__in=category_ids)
            user.profile.favorite_categories.set(categories)
        
        user.profile.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('users:dashboard_settings')
    
    # Get all categories for selection
    from apps.tools.models import Category
    all_categories = Category.objects.all()
    
    context = {
        'all_categories': all_categories,
    }
    
    return render(request, 'users/dashboard/settings.html', context)


@login_required
def toggle_bookmark(request, tool_slug):
    """
    Toggle bookmark for a tool.
    """
    tool = get_object_or_404(Tool, slug=tool_slug, is_published=True)
    
    if hasattr(request.user, 'bookmarks'):
        if request.user.bookmarks.filter(id=tool.id).exists():
            request.user.bookmarks.remove(tool)
            messages.success(request, f'Removed {tool.name} from bookmarks')
        else:
            request.user.bookmarks.add(tool)
            messages.success(request, f'Added {tool.name} to bookmarks')
    
    # Redirect back to referring page
    return redirect(request.META.get('HTTP_REFERER', 'tools:tool_detail', args=[tool_slug]))


@login_required
def delete_review(request, review_id):
    """
    Delete a user's review.
    """
    review = get_object_or_404(ToolReview, id=review_id, user=request.user)
    tool_name = review.tool.name
    review.delete()
    
    messages.success(request, f'Your review of {tool_name} has been deleted')
    return redirect('users:dashboard_reviews')


@login_required
def cancel_subscription(request):
    """
    Cancel user's subscription.
    """
    if request.method == 'POST':
        try:
            subscription = PremiumSubscription.objects.get(
                user=request.user,
                status='active'
            )
            subscription.status = 'cancelled'
            subscription.cancelled_at = timezone.now()
            subscription.save()
            
            messages.success(request, 'Your subscription has been cancelled')
        except PremiumSubscription.DoesNotExist:
            messages.error(request, 'No active subscription found')
    
    return redirect('users:dashboard_subscriptions')
