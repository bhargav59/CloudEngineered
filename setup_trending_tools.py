#!/usr/bin/env python
"""
Setup script to mark some tools as trending for blog generation.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/workspaces/CloudEngineered')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import Tool, Category
from django.utils import timezone
import random

def setup_trending_tools():
    """Mark some popular tools as trending for blog generation."""
    
    print("🔥 Setting up trending tools for blog generation...")
    
    # Get all published tools
    tools = Tool.objects.filter(is_published=True)
    
    if not tools.exists():
        print("❌ No published tools found. Please add some tools first.")
        return False
    
    # Mark top tools in each category as trending
    categories = Category.objects.filter(tools__is_published=True).distinct()
    trending_count = 0
    
    for category in categories:
        category_tools = Tool.objects.filter(
            category=category,
            is_published=True
        ).order_by('-github_stars', '-view_count')
        
        # Mark top 3-5 tools as trending
        trending_tools = category_tools[:random.randint(3, 5)]
        
        for tool in trending_tools:
            tool.is_trending = True
            tool.save()
            trending_count += 1
            print(f"🔥 Marked {tool.name} as trending in {category.name}")
    
    print(f"\n✅ Successfully marked {trending_count} tools as trending across {categories.count()} categories!")
    return True

def show_trending_status():
    """Show current trending tools status."""
    print("\n📊 Current Trending Tools Status:")
    print("=" * 50)
    
    categories = Category.objects.filter(tools__is_trending=True).distinct()
    
    for category in categories:
        trending_tools = Tool.objects.filter(
            category=category,
            is_trending=True,
            is_published=True
        )
        
        print(f"\n📂 {category.name} ({trending_tools.count()} trending)")
        for tool in trending_tools:
            stars = f"⭐ {tool.github_stars}" if tool.github_stars else "⭐ --"
            views = f"👀 {tool.view_count}" if tool.view_count else "👀 --"
            print(f"   🔥 {tool.name} ({stars}, {views})")

if __name__ == "__main__":
    print("🌟 CloudEngineered Trending Tools Setup")
    print("=" * 50)
    
    # Setup trending tools
    success = setup_trending_tools()
    
    if success:
        show_trending_status()
        print("\n🚀 Ready to generate trending blogs!")
        print("   Run: python manage.py generate_trending_blogs")
        print("   Or:  python generate_trending_blogs.py")
    
    print("\n🏁 Setup complete!")