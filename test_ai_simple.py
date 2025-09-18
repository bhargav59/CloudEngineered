#!/usr/bin/env python
"""
Simple test script for AI flexibility without full Django setup.
Tests the AI service manager with mock settings.
"""

import os
import sys

# Mock Django settings for testing
class MockSettings:
    def __init__(self):
        # Check environment variables for API keys
        self.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
        
        # Mock other required settings
        self.DEBUG = True

# Setup mock settings
sys.path.append('/workspaces/CloudEngineered')

def test_ai_service_manager():
    """Test the AI service manager without Django."""
    
    print("🧪 Testing AI Service Manager (Standalone)")
    print("=" * 50)
    
    # Mock Django's settings module
    import types
    settings_module = types.ModuleType('settings')
    settings_module.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    settings_module.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') 
    settings_module.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    settings_module.DEBUG = True
    
    sys.modules['django.conf'] = types.ModuleType('django.conf')
    sys.modules['django.conf'].settings = settings_module
    
    # Test provider detection
    print("🔍 Testing AI provider detection...")
    
    has_openrouter = bool(settings_module.OPENROUTER_API_KEY)
    has_openai = bool(settings_module.OPENAI_API_KEY)
    has_anthropic = bool(settings_module.ANTHROPIC_API_KEY)
    
    print(f"   OpenRouter: {'✅ Configured' if has_openrouter else '❌ Not configured'}")
    print(f"   OpenAI: {'✅ Configured' if has_openai else '❌ Not configured'}")
    print(f"   Anthropic: {'✅ Configured' if has_anthropic else '❌ Not configured'}")
    
    if not (has_openrouter or has_openai or has_anthropic):
        print("\n❌ No AI providers configured!")
        print("   Set at least one of these environment variables:")
        print("   - OPENROUTER_API_KEY")
        print("   - OPENAI_API_KEY")
        print("   - ANTHROPIC_API_KEY")
        return False
    
    try:
        # Import and test the service manager
        print("\n🔧 Testing service manager initialization...")
        
        # Mock the apps.ai.openrouter_service import
        sys.modules['apps'] = types.ModuleType('apps')
        sys.modules['apps.ai'] = types.ModuleType('apps.ai')
        
        # Simple mock for OpenRouterService
        class MockOpenRouterService:
            def __init__(self):
                if not has_openrouter:
                    raise Exception("OpenRouter API key not configured")
                print("   📡 OpenRouter service mock initialized")
        
        sys.modules['apps.ai.openrouter_service'] = types.ModuleType('openrouter_service')
        sys.modules['apps.ai.openrouter_service'].OpenRouterService = MockOpenRouterService
        
        # Import our service manager
        from apps.ai.service_manager import AIServiceManager
        
        # Initialize the service manager
        service_manager = AIServiceManager()
        
        print("✅ AI Service Manager initialized successfully!")
        
        # Test provider information
        provider_info = service_manager.get_provider_info()
        print(f"\n📊 Provider Configuration:")
        print(f"   Priority order: {provider_info['priority']}")
        print(f"   Available providers: {provider_info['available']}")
        
        # Test availability check
        available_providers = service_manager.get_available_providers()
        active_count = sum(available_providers.values())
        
        print(f"\n🎯 {active_count} AI provider(s) ready for use")
        
        if active_count > 1:
            print("🚀 Multi-provider flexibility enabled!")
            print("   Automatic fallback will work between configured services")
        elif active_count == 1:
            print("⚡ Single provider mode - consider adding more for redundancy")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing AI service manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_setup():
    """Test the environment setup for CloudEngineered."""
    
    print("\n🌍 Testing Environment Setup")
    print("=" * 30)
    
    # Check Python environment
    print(f"📋 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check for project files
    required_files = [
        'manage.py',
        'apps/ai/service_manager.py',
        'apps/automation/ai_content_generator.py'
    ]
    
    print("\n📄 Checking project files...")
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_present = False
    
    if all_present:
        print("✅ All required project files found")
    else:
        print("⚠️  Some project files are missing")
    
    return all_present

if __name__ == "__main__":
    print("🌟 CloudEngineered AI Flexibility Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment_setup()
    
    if env_ok:
        # Test AI service manager
        ai_ok = test_ai_service_manager()
        
        if ai_ok:
            print("\n🎉 All tests passed! AI flexibility system is ready.")
            print("\n📋 Next steps:")
            print("   1. Set your preferred AI API keys as environment variables")
            print("   2. Run: python generate_trending_blogs.py")
            print("   3. Or use: python manage.py generate_trending_blogs")
        else:
            print("\n❌ AI service tests failed. Check your configuration.")
    else:
        print("\n❌ Environment setup incomplete. Check project structure.")
    
    print("\n🏁 Test complete!")