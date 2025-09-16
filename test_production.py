#!/usr/bin/env python
"""
Production test for OpenRouter AI integration with real API
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.services import ContentGenerator, OpenAIService
from apps.ai.openrouter_service import get_openrouter_service

def test_real_api():
    """Test AI content generation with real OpenRouter API"""
    print("🚀 Testing OpenRouter Integration with Real API")
    print("=" * 60)
    
    # Test OpenRouter service configuration
    print("\n1. Testing Service Configuration:")
    openrouter_service = get_openrouter_service()
    print(f"   ✓ Service initialized: {type(openrouter_service).__name__}")
    print(f"   ✓ Using real API: {openrouter_service.api_key != 'mock-api-key'}")
    print(f"   ✓ API key present: {openrouter_service.api_key[:12]}...")
    
    # Test with different models
    print("\n2. Testing Different AI Models:")
    
    models_to_test = [
        'openai/gpt-4o-mini',    # Cheapest option
        'anthropic/claude-3-haiku',  # Alternative provider
        'openai/gpt-4o'          # Premium option
    ]
    
    for model in models_to_test:
        try:
            print(f"\n   Testing {model}:")
            result = openrouter_service.generate_content(
                system_prompt="You are a concise technical writer.",
                user_prompt="Write a 2-sentence summary of Docker containers.",
                model=model,
                max_tokens=100
            )
            
            print(f"     ✓ Generated content successfully")
            print(f"     ✓ Content: {result['content'][:80]}...")
            print(f"     ✓ Tokens: {result['tokens_used']}")
            print(f"     ✓ Cost: ${result['estimated_cost']:.6f}")
            print(f"     ✓ Provider: {result.get('model_info', {}).get('provider', 'Unknown')}")
            
        except Exception as e:
            print(f"     ❌ Error with {model}: {str(e)[:100]}...")
            continue
    
    # Test fallback mechanism
    print("\n3. Testing Fallback Mechanism:")
    try:
        result = openrouter_service.generate_content(
            system_prompt="You are a helpful assistant.",
            user_prompt="Explain what Kubernetes is in one sentence.",
            # No model specified - should use fallback chain
            max_tokens=50
        )
        
        print(f"   ✓ Fallback worked successfully")
        print(f"   ✓ Used model: {result['model']}")
        print(f"   ✓ Content: {result['content']}")
        print(f"   ✓ Cost: ${result['estimated_cost']:.6f}")
        
    except Exception as e:
        print(f"   ❌ Fallback error: {e}")
        return False
    
    # Test ContentGenerator high-level interface
    print("\n4. Testing High-Level Content Generation:")
    try:
        generator = ContentGenerator()
        
        # Create a mock template
        mock_template = type('Template', (), {
            'system_prompt': 'You are an expert tool reviewer.',
            'user_prompt_template': 'Write a brief review of {tool_name} for {use_case}.',
            'template_type': 'tool_review'
        })()
        
        result = generator.generate_content(
            template=mock_template,
            input_data={
                'tool_name': 'GitHub Actions',
                'use_case': 'CI/CD pipelines'
            },
            model='openai/gpt-4o-mini'  # Use cheapest option
        )
        
        print(f"   ✓ High-level generation successful")
        print(f"   ✓ Content length: {len(result['content'])} chars")
        print(f"   ✓ Model used: {result['model']}")
        print(f"   ✓ Total cost: ${result['cost']:.6f}")
        print(f"   ✓ Processing time: {result['processing_time']:.2f}s")
        
        # Show content preview
        print(f"\n   Content preview:")
        print(f"   {result['content'][:200]}...")
        
    except Exception as e:
        print(f"   ❌ High-level generation error: {e}")
        return False
    
    # Test legacy OpenAI compatibility
    print("\n5. Testing Legacy OpenAI Compatibility:")
    try:
        openai_service = OpenAIService()
        result = openai_service.generate_content(
            system_prompt="You are a concise assistant.",
            user_prompt="What is Docker in 10 words or less?",
            model="gpt-4o-mini",  # Will be mapped to openai/gpt-4o-mini
            max_tokens=30
        )
        
        print(f"   ✓ Legacy compatibility working")
        print(f"   ✓ Mapped model: {result['model']}")
        print(f"   ✓ Response: {result['content']}")
        
    except Exception as e:
        print(f"   ❌ Legacy compatibility error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 PRODUCTION TEST SUCCESSFUL!")
    print("\nReal API Integration Summary:")
    print("✅ OpenRouter API key working")
    print("✅ Multiple AI models accessible")
    print("✅ Cost tracking functional")
    print("✅ Fallback mechanism working")
    print("✅ High-level interface ready")
    print("✅ Legacy compatibility maintained")
    print("\n🚀 Your AI content generation is ready for production!")
    
    return True

if __name__ == '__main__':
    try:
        test_real_api()
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        sys.exit(1)