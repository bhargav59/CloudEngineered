#!/usr/bin/env python
"""
Test script for the flexible AI service manager.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/workspaces/CloudEngineered')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.automation.ai_content_generator import AIContentGenerator, AIServiceManager
from apps.tools.models import Tool, Category

def test_ai_service_manager():
    """Test the AI service manager configuration and fallback behavior."""
    
    print("🧪 Testing AI Service Manager Configuration")
    print("=" * 50)
    
    # Test service manager initialization
    try:
        manager = AIServiceManager()
        print(f"✅ AIServiceManager initialized successfully")
        print(f"📊 Available services: {', '.join(manager.available_services)}")
        print(f"🎯 Primary service: {manager.primary_service}")
        
        # Check which services are configured
        from django.conf import settings
        print(f"\n🔧 Configuration Status:")
        print(f"   OpenRouter API: {'✅ Configured' if hasattr(settings, 'OPENROUTER_API_KEY') and settings.OPENROUTER_API_KEY else '❌ Not configured'}")
        print(f"   OpenAI API: {'✅ Configured' if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY else '❌ Not configured'}")
        print(f"   Anthropic API: {'✅ Configured' if hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY else '❌ Not configured'}")
        
    except Exception as e:
        print(f"❌ Error initializing AIServiceManager: {e}")
        return False
    
    # Test content generator
    try:
        generator = AIContentGenerator()
        print(f"\n✅ AIContentGenerator initialized successfully")
        print(f"🎯 Primary service in use: {generator.ai_manager.primary_service}")
        
    except Exception as e:
        print(f"❌ Error initializing AIContentGenerator: {e}")
        return False
    
    return True

def test_prompt_generation():
    """Test prompt generation without making API calls."""
    
    print("\n🧪 Testing Prompt Generation")
    print("=" * 50)
    
    try:
        generator = AIContentGenerator()
        
        # Create a mock tool for testing
        try:
            category = Category.objects.first()
            if not category:
                category = Category.objects.create(
                    name="Test Category",
                    description="Test category for AI testing"
                )
            
            tool = Tool.objects.first()
            if not tool:
                tool = Tool.objects.create(
                    name="Test Tool",
                    description="A test tool for AI content generation testing",
                    category=category,
                    website_url="https://example.com",
                    is_published=True
                )
            
            print(f"📝 Using tool: {tool.name}")
            
            # Test prompt generation
            review_prompt = generator._build_tool_review_prompt(tool)
            print(f"✅ Tool review prompt generated ({len(review_prompt)} chars)")
            
            trend_prompt = generator._build_trend_analysis_prompt("DevOps", [tool])
            print(f"✅ Trend analysis prompt generated ({len(trend_prompt)} chars)")
            
            how_to_prompt = generator._build_how_to_prompt(tool, "deployment automation")
            print(f"✅ How-to guide prompt generated ({len(how_to_prompt)} chars)")
            
            comparison_prompt = generator._build_comparison_prompt([tool], ["pricing", "features"])
            print(f"✅ Comparison prompt generated ({len(comparison_prompt)} chars)")
            
        except Exception as e:
            print(f"❌ Error in prompt generation: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up prompt test: {e}")
        return False
    
    return True

def show_usage_examples():
    """Show usage examples for the new AI system."""
    
    print("\n📚 Usage Examples")
    print("=" * 50)
    
    print("""
# Basic Usage (uses configured primary service):
generator = AIContentGenerator()
result = generator.generate_tool_review(tool)

# Force specific service:
result = generator.generate_tool_review(tool, service="openai")
result = generator.generate_tool_review(tool, service="anthropic") 
result = generator.generate_tool_review(tool, service="openrouter")

# Generate with specific model (OpenRouter):
result = generator.generate_tool_review(tool, service="openrouter", model="anthropic/claude-3-sonnet")

# Environment Variables:
export OPENROUTER_API_KEY="your-openrouter-key"  # Primary (default)
export OPENAI_API_KEY="your-openai-key"         # Automatic fallback
export ANTHROPIC_API_KEY="your-anthropic-key"   # Automatic fallback

# Trending blog generation with flexible AI:
python manage.py generate_trending_blogs --publish
python generate_trending_blogs.py
    """)

if __name__ == "__main__":
    print("🌟 CloudEngineered Flexible AI Service Test")
    print("=" * 50)
    
    # Run tests
    success1 = test_ai_service_manager()
    success2 = test_prompt_generation()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Your flexible AI system is ready!")
        show_usage_examples()
    else:
        print("\n❌ Some tests failed. Check configuration and try again.")
    
    print("\n🏁 Test complete!")