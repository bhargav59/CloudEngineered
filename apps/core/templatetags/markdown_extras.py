"""
Custom template tags for markdown rendering.
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown2

register = template.Library()


@register.filter(name='markdown')
@stringfilter
def markdown_filter(text):
    """
    Convert markdown text to HTML.
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
    return mark_safe(html)
