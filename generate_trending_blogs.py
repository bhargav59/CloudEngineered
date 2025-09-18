#!/usr/bin/env python
"""
Quick script to generate trending blogs for CloudEngineered platform.
Run this script to create trending content automatically.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/workspaces/CloudEngineered')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.automation.tasks import generate_trending_content
from apps.automation.ai_content_generator import AIContentGenerator
from apps.tools.models import Tool, Category
from apps.content.models import Article
from django.utils import timezone
from django.conf import settings

def generate_trending_blogs():
    """Generate trending blogs for all categories with popular tools."""
    
    print("🚀 Starting trending blog generation...")
    
    try:
        # Initialize AI content generator
        generator = AIContentGenerator()
        
        # Get categories with trending tools
        categories_with_trending = Category.objects.filter(
            tools__is_published=True,
            tools__is_trending=True
        ).distinct()
        
        generated_count = 0
        
        for category in categories_with_trending:
            print(f"\n📝 Generating content for {category.name}...")
            
            # Get top trending tools in this category
            trending_tools = Tool.objects.filter(
                category=category,
                is_published=True,
                is_trending=True
            ).order_by('-github_stars', '-view_count')[:5]
            
            if trending_tools.count() >= 2:
                try:
                    # Generate trend analysis with flexible AI
                    result = generator.generate_trend_analysis(
                        category.name, 
                        list(trending_tools)
                    )
                    
                    if result.get("success"):
                        # Create article
                        article = Article.objects.create(
                            title=f"Top {category.name} Tools Trending in {timezone.now().strftime('%B %Y')}",
                            excerpt=f"Discover the most popular and trending {category.name.lower()} tools this month. Analysis and recommendations from the CloudEngineered community.",
                            content=result["content"],
                            article_type="analysis",
                            category=category,
                            ai_generated=True,
                            ai_provider=result.get("service", "auto"),
                            ai_model=result.get("model", "auto"),
                            is_published=True,  # Auto-publish trending content
                            meta_title=f"Top {category.name} Tools Trending {timezone.now().strftime('%B %Y')} | CloudEngineered",
                            meta_description=f"Latest trending {category.name.lower()} tools analysis. Market overview, recommendations, and insights from CloudEngineered experts.",
                        )
                        
                        print(f"✅ Created article: {article.title}")
                        print(f"   📄 Content length: {len(article.content)} characters")
                        print(f"   🔗 URL: /content/articles/{article.slug}/")
                        generated_count += 1
                        
                except Exception as e:
                    print(f"❌ Error generating content for {category.name}: {e}")
                    continue
            else:
                print(f"⚠️  Not enough trending tools in {category.name} (need at least 2)")
        
        print(f"\n🎉 Successfully generated {generated_count} trending blog articles!")
        
        # Also run the existing trending content task
        print("\n🔄 Running additional trending content generation...")
        task_result = generate_trending_content()
        
        if task_result.get("success"):
            print("✅ Additional trending content generated successfully!")
        else:
            print(f"⚠️  Additional content generation had issues: {task_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Fatal error during blog generation: {e}")
        return False
    
    return True

def show_recent_articles():
    """Show recently generated articles."""
    print("\n📰 Recent Articles Generated:")
    print("=" * 50)
    
    recent_articles = Article.objects.filter(
        ai_generated=True
    ).order_by('-created_at')[:10]
    
    for i, article in enumerate(recent_articles, 1):
        print(f"{i:2d}. {article.title}")
        print(f"    📅 {article.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"    📂 {article.category.name if article.category else 'No Category'}")
        print(f"    🤖 {article.ai_provider} ({article.ai_model})")
        print(f"    📊 {article.view_count} views")
        print()

if __name__ == "__main__":
    print("🌟 CloudEngineered Trending Blog Generator")
    print("=" * 50)
    
    # Check if we have any AI API keys configured
    
    has_openrouter = hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY
    has_openai = hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY  
    has_anthropic = hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY
    
    if not (has_openrouter or has_openai or has_anthropic):
        print("❌ No AI API keys configured!")
        print("   Please set one of: OPENROUTER_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        sys.exit(1)
    
    print(f"✅ OpenRouter API: {'Configured' if has_openrouter else 'Not configured'}")
    print(f"✅ OpenAI API: {'Configured' if has_openai else 'Not configured'}")
    print(f"✅ Anthropic API: {'Configured' if has_anthropic else 'Not configured'}")
    
    # Show which service will be used
    if has_openrouter:
        print("🎯 Primary service: OpenRouter (flexible model access)")
    elif has_anthropic:
        print("🎯 Primary service: Anthropic Claude")
    elif has_openai:
        print("🎯 Primary service: OpenAI GPT")
    
    print("🔄 Automatic fallback enabled between configured services")
    
    # Generate trending blogs
    success = generate_trending_blogs()
    
    if success:
        show_recent_articles()
    
    print("\n🏁 Blog generation complete!")