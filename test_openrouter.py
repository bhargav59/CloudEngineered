#!/usr/bin/env python
"""
Test script for OpenRouter AI integration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.ai.services import ContentGenerator, OpenAIService
from apps.ai.openrouter_service import get_openrouter_service
from apps.ai.models import ContentTemplate, AIModel, AIProvider

def test_mock_mode():
    """Test AI content generation in mock mode"""
    print("🧪 Testing OpenRouter Integration in Mock Mode")
    print("=" * 50)
    
    # Test OpenRouter service directly
    print("\n1. Testing OpenRouter Service:")
    openrouter_service = get_openrouter_service()
    print(f"   ✓ Service initialized: {type(openrouter_service).__name__}")
    print(f"   ✓ Mock mode: {openrouter_service.api_key == 'mock-api-key'}")
    print(f"   ✓ Available models: {len(openrouter_service.MODELS)}")
    
    # Test content generation
    print("\n2. Testing Content Generation:")
    generator = ContentGenerator()
    
    # Test with mock template-like data
    mock_template = type('Template', (), {
        'system_prompt': 'You are a technical writing assistant.',
        'user_prompt_template': 'Write a review for {tool_name} in the {category} category.',
        'template_type': 'tool_review'
    })()
    
    input_data = {
        'tool_name': 'Docker',
        'category': 'Containerization',
        'tool_description': 'A platform for developing, shipping, and running applications using containers.'
    }
    
    try:
        result = generator.generate_content(
            template=mock_template,
            input_data=input_data,
            mock=True
        )
        
        print(f"   ✓ Content generated successfully")
        print(f"   ✓ Content length: {len(result['content'])} characters")
        print(f"   ✓ Tokens used: {result['tokens_used']}")
        print(f"   ✓ Estimated cost: ${result['cost']}")
        print(f"   ✓ Processing time: {result['processing_time']}s")
        print(f"   ✓ Model used: {result['model']}")
        
        # Show first 200 characters of content
        print(f"\n   Content preview:")
        print(f"   {result['content'][:200]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test OpenRouter service model recommendation
    print("\n3. Testing Model Recommendations:")
    try:
        technical_model = openrouter_service.get_recommended_model('technical')
        general_model = openrouter_service.get_recommended_model('general')
        creative_model = openrouter_service.get_recommended_model('creative')
        
        print(f"   ✓ Technical tasks: {technical_model}")
        print(f"   ✓ General tasks: {general_model}")
        print(f"   ✓ Creative tasks: {creative_model}")
        
    except Exception as e:
        print(f"   ❌ Model recommendation error: {e}")
        return False
    
    # Test cost calculation
    print("\n4. Testing Cost Calculation:")
    try:
        cost = openrouter_service._calculate_cost('openai/gpt-4o-mini', 1000, 500)
        print(f"   ✓ Cost for 1000 input + 500 output tokens: ${cost}")
        
    except Exception as e:
        print(f"   ❌ Cost calculation error: {e}")
        return False
    
    print("\n✅ All tests passed! OpenRouter integration is working in mock mode.")
    return True

def test_openai_service_compatibility():
    """Test that OpenAIService still works with OpenRouter routing"""
    print("\n🔄 Testing OpenAI Service Compatibility")
    print("=" * 50)
    
    try:
        openai_service = OpenAIService()
        print("   ✓ OpenAIService initialized successfully")
        
        # Test content generation with the old interface
        result = openai_service.generate_content(
            system_prompt="You are a helpful assistant.",
            user_prompt="Write a short description of Docker.",
            model="gpt-4",  # This should be mapped to openai/gpt-4o
            max_tokens=200
        )
        
        print(f"   ✓ Content generated via OpenAI service")
        print(f"   ✓ Model used: {result['model']}")
        print(f"   ✓ Tokens used: {result['tokens_used']}")
        
    except Exception as e:
        print(f"   ❌ OpenAI service compatibility error: {e}")
        return False
    
    print("   ✅ OpenAI service compatibility maintained!")
    return True

if __name__ == '__main__':
    print("🚀 CloudEngineered - OpenRouter Integration Test")
    print("=" * 50)
    
    # Run tests
    test1_passed = test_mock_mode()
    test2_passed = test_openai_service_compatibility()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! OpenRouter integration is ready.")
        print("\nNext steps:")
        print("1. Add your OpenRouter API key to .env file")
        print("2. Set AI_MOCK_MODE=False to use real API")
        print("3. Start generating content with multiple AI models!")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)