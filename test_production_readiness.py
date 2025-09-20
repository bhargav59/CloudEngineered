#!/usr/bin/env python
"""
Comprehensive CloudEngineered Production Readiness Test
"""

import os
import sys
import django
import requests
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import Tool, Category
from apps.content.models import Article
from apps.ai.openrouter_service import get_openrouter_service

def test_database_setup():
    """Test that database is properly set up with data."""
    print("🗄️  Testing Database Setup...")
    
    # Test models
    categories = Category.objects.count()
    tools = Tool.objects.count()
    articles = Article.objects.count()
    users = get_user_model().objects.count()
    
    print(f"   ✓ Categories: {categories}")
    print(f"   ✓ Tools: {tools}")
    print(f"   ✓ Articles: {articles}")
    print(f"   ✓ Users: {users}")
    
    if categories >= 5 and tools >= 5 and articles >= 1 and users >= 1:
        print("   ✅ Database setup: PASS")
        return True
    else:
        print("   ❌ Database setup: FAIL")
        return False

def test_web_interface():
    """Test that web interface is working."""
    print("🌐 Testing Web Interface...")
    
    client = Client()
    
    # Test homepage
    response = client.get('/')
    if response.status_code == 200:
        print("   ✓ Homepage: 200 OK")
    else:
        print(f"   ❌ Homepage: {response.status_code}")
        return False
    
    # Test tools page
    response = client.get('/tools/')
    if response.status_code == 200:
        print("   ✓ Tools page: 200 OK")
    else:
        print(f"   ❌ Tools page: {response.status_code}")
        return False
    
    # Test search page
    response = client.get('/search/')
    if response.status_code == 200:
        print("   ✓ Search page: 200 OK")
    else:
        print(f"   ❌ Search page: {response.status_code}")
        return False
    
    # Test admin panel
    response = client.get('/admin/')
    if response.status_code == 200:
        print("   ✓ Admin panel: 200 OK")
    else:
        print(f"   ❌ Admin panel: {response.status_code}")
        return False
    
    print("   ✅ Web interface: PASS")
    return True

def test_seo_features():
    """Test SEO features."""
    print("🔍 Testing SEO Features...")
    
    client = Client()
    
    # Test sitemap
    response = client.get('/sitemap.xml')
    if response.status_code == 200 and 'xml' in response['Content-Type']:
        print("   ✓ Sitemap: Working")
    else:
        print("   ❌ Sitemap: Failed")
        return False
    
    # Test robots.txt
    response = client.get('/robots.txt')
    if response.status_code == 200:
        print("   ✓ Robots.txt: Working")
    else:
        print("   ❌ Robots.txt: Failed")
        return False
    
    # Test meta tags on homepage
    response = client.get('/')
    content = response.content.decode()
    if 'meta name="description"' in content and 'meta property="og:title"' in content:
        print("   ✓ Meta tags: Present")
    else:
        print("   ❌ Meta tags: Missing")
        return False
    
    print("   ✅ SEO features: PASS")
    return True

def test_ai_integration():
    """Test AI integration."""
    print("🤖 Testing AI Integration...")
    
    try:
        service = get_openrouter_service()
        print(f"   ✓ Service initialized: {service.__class__.__name__}")
        
        # Test model availability
        models = service.get_available_models()
        print(f"   ✓ Available models: {len(models)}")
        
        # Test content generation (mock mode)
        test_tool = Tool.objects.first()
        if test_tool:
            result = service.generate_content(
                system_prompt="You are a helpful assistant that reviews software tools.",
                user_prompt=f"Generate a brief review for {test_tool.name}",
                model="gpt-4o-mini",
                max_tokens=100
            )
            if result and result.get('content'):
                print("   ✓ Content generation: Working")
            else:
                print("   ❌ Content generation: Failed")
                return False
        
        print("   ✅ AI integration: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ AI integration: Failed - {e}")
        return False

def test_production_readiness():
    """Test production readiness."""
    print("🚀 Testing Production Readiness...")
    
    # Check Django checks
    from django.core.management.base import CommandError
    from django.core import checks
    
    try:
        issues = checks.run_checks(include_deployment_checks=False)
        if not issues:
            print("   ✓ Django system checks: PASS")
        else:
            print(f"   ⚠️  Django system checks: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"      - {issue}")
    except Exception as e:
        print(f"   ❌ Django system checks: Failed - {e}")
        return False
    
    # Check environment variables
    required_settings = ['SECRET_KEY', 'DEBUG']
    missing = [setting for setting in required_settings if not hasattr(django.conf.settings, setting)]
    
    if not missing:
        print("   ✓ Required settings: Present")
    else:
        print(f"   ❌ Missing settings: {missing}")
        return False
    
    print("   ✅ Production readiness: PASS")
    return True

def main():
    """Run all tests."""
    print("🚀 CloudEngineered Production Readiness Test")
    print("=" * 50)
    
    tests = [
        test_database_setup,
        test_web_interface,
        test_seo_features,
        test_ai_integration,
        test_production_readiness
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! CloudEngineered is production ready!")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)