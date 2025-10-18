"""
Forms for the tools app.
"""
from django import forms
from .models import ToolReview


class ToolReviewForm(forms.ModelForm):
    """Form for creating tool reviews."""
    
    class Meta:
        model = ToolReview
        fields = ['title', 'content', 'rating', 'usage_duration', 'use_case', 'team_size']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Summary of your review'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Share your experience with this tool...',
                'rows': 6
            }),
            'rating': forms.RadioSelect(attrs={
                'class': 'star-rating'
            }),
            'usage_duration': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'use_case': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., CI/CD pipelines, container orchestration'
            }),
            'team_size': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., 5-10 developers'
            }),
        }
        labels = {
            'title': 'Review Title',
            'content': 'Your Review',
            'rating': 'Rating',
            'usage_duration': 'How long have you used this tool?',
            'use_case': 'What did you use it for?',
            'team_size': 'Team Size (optional)',
        }
