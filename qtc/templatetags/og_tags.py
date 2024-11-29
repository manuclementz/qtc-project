from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.conf import settings
import os
from PIL import Image
from urllib.parse import urljoin
import mimetypes

register = template.Library()

def get_image_info(image_path):
    """
    Get image dimensions and mime type.
    Returns tuple of (width, height, mime_type) or None if image can't be processed
    """
    try:
        if not os.path.exists(image_path):
            return None
        
        with Image.open(image_path) as img:
            width, height = img.size
            # Get mime type based on file extension
            mime_type = mimetypes.guess_type(image_path)[0] or 'image/jpeg'
            return (width, height, mime_type)
    except Exception:
        return None

def generate_cache_key(request, context):
    """Generate a unique cache key based on the current URL and context"""
    url = request.build_absolute_uri()
    # If it's a game page, include the game's last modified timestamp in the key
    if 'game' in context and hasattr(context['game'], 'updated_at'):
        return f'og_meta_tags:{url}:{context["game"].updated_at.timestamp()}'
    return f'og_meta_tags:{url}'

def generate_meta_tags(request, context):
    """Generate OpenGraph and Twitter Card meta tags based on the current page context"""
    page_type = context.get('og_type', 'website')
    meta_tags = []
    
    # Site name
    site_name = getattr(settings, 'OG_SITE_NAME', 'QTC')
    meta_tags.append(f'<meta property="og:site_name" content="{escape(site_name)}">')
    
    # Basic tags
    meta_tags.extend([
        f'<meta property="og:type" content="{page_type}">',
        f'<meta property="og:url" content="{request.build_absolute_uri()}">'
    ])
    
    # Title    
    title = site_name + ' | Quiz Thématique de Chiktabba'
    meta_tags.extend([
        f'<meta property="og:title" content="{escape(title)}">',
        f'<meta name="twitter:title" content="{escape(title)}">'
    ])
    
    # Description
    description = "Le site des grilles de 5x5 plus ou moins emblématiques."
    meta_tags.extend([
        f'<meta property="og:description" content="{escape(description)}">',
        f'<meta name="twitter:description" content="{escape(description)}">'
    ])
    
    # Twitter specific tags
    twitter_handle = getattr(settings, 'TWITTER_HANDLE', '')
    if twitter_handle:
        meta_tags.append(f'<meta name="twitter:site" content="@{escape(twitter_handle)}">')
    meta_tags.append('<meta name="twitter:card" content="summary_large_image">')
    
    return '\n'.join(meta_tags)

@register.simple_tag(takes_context=True)
def og_meta_tags(context):
    """
    Template tag that returns cached OpenGraph and Twitter Card meta tags.
    Cache duration is set by OG_META_CACHE_TIMEOUT in settings (defaults to 1 hour).
    """
    request = context['request']
    
    # Skip caching in debug mode if configured
    if getattr(settings, 'OG_META_SKIP_CACHE_IN_DEBUG', False) and settings.DEBUG:
        return mark_safe(generate_meta_tags(request, context))
    
    cache_key = generate_cache_key(request, context)
    cached_tags = cache.get(cache_key)
    
    if cached_tags is None:
        cached_tags = generate_meta_tags(request, context)
        timeout = getattr(settings, 'OG_META_CACHE_TIMEOUT', 3600)  # Default 1 hour
        cache.set(cache_key, cached_tags, timeout)
    
    return mark_safe(cached_tags)