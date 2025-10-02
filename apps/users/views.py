"""
User views for CloudEngineered platform.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import DetailView, UpdateView, ListView, CreateView
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django import forms

from .models import User, UserProfile, UserActivity, UserBookmark, UserPreferences, UserSubscription
from apps.tools.models import Tool, ToolReview
from apps.content.models import Article


class UserRegistrationForm(UserCreationForm):
    """Custom registration form."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com'
        })
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Choose a username'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            UserPreferences.objects.create(user=user)
        return user


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in
            login(request, user)
            messages.success(request, f'Welcome to CloudEngineered, {user.username}! Your account has been created successfully.')
            return redirect('users:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


class UserDashboardView(LoginRequiredMixin, DetailView):
    """User dashboard main page."""
    template_name = 'users/dashboard.html'
    context_object_name = 'user'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        context['profile'] = profile
        
        # Recent activity
        context['recent_activities'] = UserActivity.objects.filter(
            user=user
        ).order_by('-created_at')[:10]
        
        # Bookmarks
        context['recent_bookmarks'] = UserBookmark.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Statistics
        context['stats'] = {
            'tools_reviewed': ToolReview.objects.filter(user=user).count(),
            'articles_read': profile.articles_read,
            'bookmarks_count': UserBookmark.objects.filter(user=user).count(),
            'comments_made': profile.comments_made,
        }
        
        # Recommended tools based on user interests
        if profile.favorite_categories:
            context['recommended_tools'] = Tool.objects.filter(
                category__name__in=profile.favorite_categories,
                is_published=True
            ).order_by('-created_at')[:6]
        else:
            context['recommended_tools'] = Tool.objects.filter(
                is_published=True
            ).order_by('-view_count')[:6]
        
        # Recent articles
        context['recent_articles'] = Article.objects.filter(
            is_published=True
        ).order_by('-created_at')[:5]
        
        return context


class UserProfileView(DetailView):
    """Public user profile view."""
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        
        # Get user profile
        profile = getattr(user, 'profile', None)
        context['profile'] = profile
        
        # Check privacy settings
        can_view_activity = True
        can_view_bookmarks = False
        
        if profile:
            preferences = getattr(user, 'preferences', None)
            if preferences:
                if preferences.profile_visibility == 'private':
                    can_view_activity = False
                elif preferences.profile_visibility == 'authenticated' and not self.request.user.is_authenticated:
                    can_view_activity = False
                
                can_view_activity = can_view_activity and preferences.show_activity
                can_view_bookmarks = preferences.show_bookmarks and self.request.user == user
        
        context['can_view_activity'] = can_view_activity
        context['can_view_bookmarks'] = can_view_bookmarks
        
        if can_view_activity:
            # Recent reviews
            context['recent_reviews'] = ToolReview.objects.filter(
                user=user,
                is_published=True
            ).order_by('-created_at')[:5]
            
            # Recent activity
            context['recent_activities'] = UserActivity.objects.filter(
                user=user
            ).order_by('-created_at')[:10]
        
        if can_view_bookmarks:
            context['bookmarks'] = UserBookmark.objects.filter(
                user=user
            ).order_by('-created_at')[:10]
        
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile view."""
    model = User
    template_name = 'users/profile_edit.html'
    fields = [
        'first_name', 'last_name', 'bio', 'location', 'website', 'avatar',
        'company', 'job_title', 'experience_level', 'github_username',
        'linkedin_url', 'twitter_username'
    ]
    
    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return self.object.get_absolute_url()
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)


@login_required
def user_bookmarks_view(request):
    """User bookmarks management view."""
    bookmarks = UserBookmark.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by content type
    content_type = request.GET.get('type')
    if content_type in ['tool', 'article', 'comparison']:
        bookmarks = bookmarks.filter(content_type=content_type)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        bookmarks = bookmarks.filter(
            Q(notes__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(bookmarks, 20)
    page = request.GET.get('page')
    bookmarks = paginator.get_page(page)
    
    context = {
        'bookmarks': bookmarks,
        'content_type': content_type,
        'search_query': search_query,
    }
    return render(request, 'users/bookmarks.html', context)


@login_required
def add_bookmark(request):
    """AJAX view to add/remove bookmarks."""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        object_id = request.POST.get('object_id')
        
        if content_type and object_id:
            bookmark, created = UserBookmark.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            
            if not created:
                bookmark.delete()
                bookmarked = False
            else:
                bookmarked = True
                
                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='bookmark_tool' if content_type == 'tool' else 'bookmark_content',
                    object_type=content_type,
                    object_id=object_id
                )
            
            return JsonResponse({
                'success': True,
                'bookmarked': bookmarked
            })
    
    return JsonResponse({'success': False})


@login_required
def user_preferences_view(request):
    """User preferences and settings view."""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences
        preferences.dashboard_layout = request.POST.get('dashboard_layout', preferences.dashboard_layout)
        preferences.items_per_page = int(request.POST.get('items_per_page', preferences.items_per_page))
        preferences.content_difficulty = request.POST.get('content_difficulty', preferences.content_difficulty)
        preferences.email_frequency = request.POST.get('email_frequency', preferences.email_frequency)
        
        # Boolean fields
        preferences.notify_new_tools = bool(request.POST.get('notify_new_tools'))
        preferences.notify_tool_updates = bool(request.POST.get('notify_tool_updates'))
        preferences.notify_new_articles = bool(request.POST.get('notify_new_articles'))
        preferences.notify_comments = bool(request.POST.get('notify_comments'))
        preferences.show_activity = bool(request.POST.get('show_activity'))
        preferences.show_bookmarks = bool(request.POST.get('show_bookmarks'))
        
        preferences.profile_visibility = request.POST.get('profile_visibility', preferences.profile_visibility)
        
        preferences.save()
        messages.success(request, 'Your preferences have been updated!')
        return redirect('users:preferences')
    
    context = {
        'preferences': preferences,
    }
    return render(request, 'users/preferences.html', context)


@login_required
def subscription_view(request):
    """User subscription management view."""
    subscription, created = UserSubscription.objects.get_or_create(user=request.user)
    
    context = {
        'subscription': subscription,
        'available_plans': UserSubscription.SUBSCRIPTION_PLANS,
    }
    return render(request, 'users/subscription.html', context)


class UserActivityListView(LoginRequiredMixin, ListView):
    """User activity history view."""
    model = UserActivity
    template_name = 'users/activity.html'
    context_object_name = 'activities'
    paginate_by = 50
    
    def get_queryset(self):
        return UserActivity.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Activity stats
        activities = UserActivity.objects.filter(user=self.request.user)
        context['activity_stats'] = {
            'total': activities.count(),
            'this_week': activities.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'this_month': activities.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        }
        
        return context


# Utility function to track user activity
def track_user_activity(user, activity_type, object_type, object_id, metadata=None):
    """Helper function to track user activities."""
    if user.is_authenticated:
        UserActivity.objects.create(
            user=user,
            activity_type=activity_type,
            object_type=object_type,
            object_id=object_id,
            metadata=metadata or {}
        )
