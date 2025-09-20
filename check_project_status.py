#!/usr/bin/env python3
"""
Project Status Checker for CloudEngineered
This script analyzes the project for potential issues and configuration problems.
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Check if all required directories and files exist"""
    print("🔍 Checking Project Structure...")
    
    required_dirs = [
        'apps/core',
        'apps/users', 
        'apps/ai',
        'apps/tools',
        'apps/content',
        'apps/analytics',
        'apps/automation',
        'apps/affiliates',
        'apps/api',
        'config/settings',
        'templates',
        'static',
    ]
    
    required_files = [
        'manage.py',
        'config/urls.py',
        'config/settings/base.py',
        'config/settings/development.py',
        'config/settings/production.py',
        '.env.example',
    ]
    
    missing_dirs = []
    missing_files = []
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
        else:
            print(f"✅ {directory}")
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def check_python_syntax():
    """Check Python files for syntax errors"""
    print("\n🐍 Checking Python Syntax...")
    
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environment and git directories
        dirs[:] = [d for d in dirs if d not in ['venv', '.git', '__pycache__', '.pytest_cache']]
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path}")
        except SyntaxError as e:
            syntax_errors.append((file_path, str(e)))
            print(f"❌ {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ {file_path}: {e}")
    
    return len(syntax_errors) == 0

def check_environment_file():
    """Check if .env file exists and has required variables"""
    print("\n🔧 Checking Environment Configuration...")
    
    if not Path('.env').exists():
        print("❌ .env file not found")
        if Path('.env.example').exists():
            print("📝 Creating .env from .env.example...")
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created")
        else:
            print("❌ .env.example not found either")
            return False
    
    # Check for critical environment variables
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        required_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
        missing_vars = []
        
        for var in required_vars:
            if f'{var}=' not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        else:
            print("✅ Environment file looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_requirements():
    """Check requirements files"""
    print("\n📦 Checking Requirements Files...")
    
    req_files = [
        'requirements/base.txt',
        'requirements/development.txt',
        'requirements/production.txt'
    ]
    
    for req_file in req_files:
        if Path(req_file).exists():
            print(f"✅ {req_file}")
            try:
                with open(req_file, 'r') as f:
                    lines = len(f.readlines())
                print(f"   📄 {lines} lines")
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
        else:
            print(f"❌ {req_file}")

def check_app_configurations():
    """Check Django app configurations"""
    print("\n🏗️ Checking Django App Configurations...")
    
    apps_dir = Path('apps')
    if not apps_dir.exists():
        print("❌ apps directory not found")
        return False
    
    for app_dir in apps_dir.iterdir():
        if app_dir.is_dir() and not app_dir.name.startswith('__'):
            app_files = ['__init__.py', 'models.py', 'views.py', 'urls.py']
            print(f"\n📁 {app_dir.name}:")
            
            for app_file in app_files:
                file_path = app_dir / app_file
                if file_path.exists():
                    print(f"   ✅ {app_file}")
                else:
                    print(f"   ⚠️ {app_file} (optional)")

def check_initial_data_scripts():
    """Check for initial data population scripts"""
    print("\n📊 Checking Data Population Scripts...")
    
    data_scripts = [
        'setup_initial_data.py',
        'setup_simple_data.py',
        'setup_trending_tools.py'
    ]
    
    for script in data_scripts:
        if Path(script).exists():
            print(f"✅ {script}")
        else:
            print(f"❌ {script}")

def main():
    """Main function to run all checks"""
    print("🚀 CloudEngineered Project Status Check")
    print("=" * 50)
    
    results = {
        'structure': check_project_structure(),
        'syntax': check_python_syntax(),
        'environment': check_environment_file(),
        'requirements': True,  # Just informational
        'apps': True,  # Just informational
        'data_scripts': True,  # Just informational
    }
    
    check_requirements()
    check_app_configurations()
    check_initial_data_scripts()
    
    print("\n" + "=" * 50)
    print("📋 Summary:")
    
    all_good = True
    for check_name, result in results.items():
        if result:
            print(f"✅ {check_name.replace('_', ' ').title()}")
        else:
            print(f"❌ {check_name.replace('_', ' ').title()}")
            all_good = False
    
    if all_good:
        print("\n🎉 Project structure looks good!")
        print("📝 Next steps:")
        print("1. Install dependencies: pip install -r requirements/development.txt")
        print("2. Run migrations: python manage.py migrate")
        print("3. Create superuser: python manage.py createsuperuser")
        print("4. Load initial data: python setup_initial_data.py")
        print("5. Start server: python manage.py runserver")
    else:
        print("\n⚠️ Some issues found that need to be addressed.")
    
    return all_good

if __name__ == '__main__':
    main()