from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Look up a key in a dictionary."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary."""
    return dictionary.get(key)

@register.filter
def stars_to_emoji(rating_str):
    """Convert star rating string to emoji stars."""
    if not rating_str:
        return ''
    
    # Count the number of ⭐ characters
    star_count = rating_str.count('⭐')
    
    # Return star emojis
    return '⭐' * star_count if star_count > 0 else rating_str