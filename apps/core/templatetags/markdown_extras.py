"""
Custom template tags for markdown rendering.
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown2
import bleach

register = template.Library()

# Define allowed HTML tags and attributes for security
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
    'blockquote', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'del', 'ins',
    'sup', 'sub', 'span', 'div', 'input'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'rel'],
    'code': ['class'],
    'pre': ['class'],
    'span': ['class'],
    'div': ['class'],
    'input': ['type', 'disabled', 'checked'],
    '*': ['id']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


@register.filter(name='markdown')
@stringfilter
def markdown_filter(text):
    """
    Convert markdown text to HTML with XSS protection.
    """
    if not text:
        return ''
    
    # Use markdown2 with GitHub-flavored markdown
    html = markdown2.markdown(
        text,
        extras=[
            'fenced-code-blocks',
            'tables',
            'header-ids',
            'strike',
            'task_list',
            'code-friendly',
            'cuddled-lists',
            'footnotes',
            'link-patterns',
            'smarty-pants',
        ]
    )
    
    # Sanitize HTML to prevent XSS attacks
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True
    )
    
    return mark_safe(clean_html)
