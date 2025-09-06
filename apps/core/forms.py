"""
Core forms for CloudEngineered platform.
"""

from django import forms
from django.core.validators import validate_email
from .models import NewsletterSubscriber


class NewsletterSubscriptionForm(forms.ModelForm):
    """
    Newsletter subscription form.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-input',
        }),
        help_text='We will never share your email with anyone.'
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            validate_email(email)
        return email


class ContactForm(forms.Form):
    """
    Contact form for user inquiries.
    """
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('tool_request', 'Tool Review Request'),
        ('partnership', 'Partnership Opportunity'),
        ('technical', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your full name',
            'class': 'form-input',
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com',
            'class': 'form-input',
        })
    )
    
    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Your message...',
            'class': 'form-textarea',
            'rows': 5,
        })
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        return message


class SearchForm(forms.Form):
    """
    Global search form.
    """
    q = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tools, articles, and guides...',
            'class': 'search-input',
        }),
        label='Search'
    )
    
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.HiddenInput()
    )
    
    def clean_q(self):
        query = self.cleaned_data.get('q')
        if query and len(query) < 2:
            raise forms.ValidationError('Search query must be at least 2 characters long.')
        return query
