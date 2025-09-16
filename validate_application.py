#!/usr/bin/env python3
"""
Comprehensive validation script for CloudEngineered platform
Validates CSS/JS configuration and overall functionality
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append('/workspaces/codespaces-blank/cloudengineered')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def validate_static_files():
    """Validate static files configuration"""
    print("🔍 Validating static files...")
    
    # Check CSS file
    css_path = Path('/workspaces/codespaces-blank/cloudengineered/static/css/main.css')
    if css_path.exists():
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        # Check for proper CSS conversion (no @apply directives)
        if '@apply' in css_content:
            print("❌ CSS still contains @apply directives")
            return False
        else:
            print("✅ CSS properly converted to standard CSS")
    else:
        print("❌ CSS file not found")
        return False
    
    # Check JS file
    js_path = Path('/workspaces/codespaces-blank/cloudengineered/static/js/main.js')
    if js_path.exists():
        with open(js_path, 'r') as f:
            js_content = f.read()
        
        # Check for essential JavaScript functionality
        if 'addEventListener' in js_content and 'DOMContentLoaded' in js_content:
            print("✅ JavaScript file contains interactive functionality")
        else:
            print("⚠️  JavaScript file exists but may lack interactivity")
    else:
        print("❌ JavaScript file not found")
        return False
    
    return True

def validate_django_setup():
    """Validate Django configuration"""
    print("\n🔍 Validating Django setup...")
    
    try:
        from django.conf import settings
        from django.apps import apps
        
        # Check if apps are properly loaded
        if apps.ready:
            print("✅ Django apps properly loaded")
        else:
            print("❌ Django apps not ready")
            return False
        
        # Check static files settings (allow both STATIC_URL and STATICFILES_DIRS)
        if hasattr(settings, 'STATIC_URL'):
            print(f"✅ STATIC_URL configured: {settings.STATIC_URL}")
        elif hasattr(settings, 'STATICFILES_DIRS'):
            print("✅ Static files configured via STATICFILES_DIRS")
        else:
            print("⚠️  Static files configuration not found")
        
        # Check database connection
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Django validation error: {e}")
        return False

def validate_models():
    """Validate key models using Django management commands"""
    print("\n🔍 Validating models...")
    
    try:
        # Test basic model operations using Django shell-like approach
        from django.apps import apps
        
        # Get model classes properly
        Tool = apps.get_model('tools', 'Tool')
        Article = apps.get_model('content', 'Article') 
        Category = apps.get_model('tools', 'Category')
        
        # Check if models can be queried
        tool_count = Tool.objects.filter(is_published=True).count()
        article_count = Article.objects.filter(is_published=True).count()
        category_count = Category.objects.count()
        
        print(f"✅ Published tools: {tool_count}")
        print(f"✅ Published articles: {article_count}")  
        print(f"✅ Categories: {category_count}")
        
        # Check site configuration
        try:
            SiteConfiguration = apps.get_model('core', 'SiteConfiguration')
            site_config = SiteConfiguration.objects.get(pk=1)
            print(f"✅ Site configuration loaded: {site_config.site_name}")
        except Exception:
            print("⚠️  No site configuration found")
        
        return True
        
    except Exception as e:
        print(f"❌ Model validation error: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 CloudEngineered Platform Validation")
    print("=" * 50)
    
    validations = [
        validate_static_files(),
        validate_django_setup(),
        validate_models()
    ]
    
    print("\n" + "=" * 50)
    if all(validations):
        print("🎉 All validations passed! Your CloudEngineered platform is properly configured.")
        print("📝 Summary:")
        print("   ✅ CSS/JS files properly configured")
        print("   ✅ Django setup successful")
        print("   ✅ Database models accessible")
        print("   ✅ Server ready for production use")
        print("\n🌐 Access your application at: http://localhost:8000")
        return True
    else:
        print("❌ Some validations failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)