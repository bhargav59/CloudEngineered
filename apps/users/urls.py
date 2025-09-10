from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    
    # Profile management
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    
    # Bookmarks
    path('bookmarks/', views.user_bookmarks_view, name='bookmarks'),
    path('bookmarks/add/', views.add_bookmark, name='add_bookmark'),
    
    # Preferences and settings
    path('preferences/', views.user_preferences_view, name='preferences'),
    path('subscription/', views.subscription_view, name='subscription'),
    
    # Activity
    path('activity/', views.UserActivityListView.as_view(), name='activity'),
]
