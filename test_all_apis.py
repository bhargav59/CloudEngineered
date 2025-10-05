#!/usr/bin/env python
"""
Test all available AI API keys and configure the best working one.
Tests: xAI Grok, NVIDIA, Google Gemini, and O1 API
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from openai import OpenAI
import google.generativeai as genai
import requests

# API Keys to test - load from environment variables for security
API_KEYS = {
    'xai': os.getenv('XAI_API_KEY', ''),
    'nvidia_1': os.getenv('NVIDIA_API_KEY_1', ''),
    'nvidia_2': os.getenv('NVIDIA_API_KEY_2', ''),
    'gemini': os.getenv('GOOGLE_GEMINI_API_KEY', ''),
}

# Validate that at least one API key is provided
if not any(API_KEYS.values()):
    print("❌ Error: No API keys found in environment variables")
    print("   Please set at least one of: XAI_API_KEY, NVIDIA_API_KEY_1, NVIDIA_API_KEY_2, GOOGLE_GEMINI_API_KEY")
    sys.exit(1)

print("=" * 80)
print("  AI API Testing Suite - Finding the Best Working API")
print("=" * 80)
print()

working_apis = []

# Test 1: xAI Grok API
print("🔄 Testing xAI Grok API...")
print("-" * 80)
try:
    client = OpenAI(
        api_key=API_KEYS['xai'],
        base_url="https://api.x.ai/v1",
    )
    
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API test successful' in exactly 3 words."}
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    result = response.choices[0].message.content.strip()
    
    print(f"✅ xAI Grok API: WORKING")
    print(f"   Model: grok-beta")
    print(f"   Response: {result}")
    print(f"   Tokens used: {response.usage.total_tokens}")
    print(f"   API Key: {API_KEYS['xai'][:20]}...")
    
    working_apis.append({
        'name': 'xAI Grok',
        'key': API_KEYS['xai'],
        'base_url': 'https://api.x.ai/v1',
        'model': 'grok-beta',
        'type': 'openai_compatible',
        'priority': 1,  # Highest priority - free tier available
        'cost': 'Free tier available'
    })
    
except Exception as e:
    print(f"❌ xAI Grok API: FAILED")
    print(f"   Error: {str(e)}")

print()

# Test 2: NVIDIA API Key 1
print("🔄 Testing NVIDIA API Key 1...")
print("-" * 80)
try:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=API_KEYS['nvidia_1']
    )
    
    response = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=[
            {"role": "user", "content": "Say 'API test successful' in exactly 3 words."}
        ],
        temperature=0.5,
        max_tokens=50
    )
    
    result = response.choices[0].message.content.strip()
    
    print(f"✅ NVIDIA API Key 1: WORKING")
    print(f"   Model: llama-3.1-nemotron-70b-instruct")
    print(f"   Response: {result}")
    print(f"   Tokens used: {response.usage.total_tokens}")
    print(f"   API Key: {API_KEYS['nvidia_1'][:20]}...")
    
    working_apis.append({
        'name': 'NVIDIA NIM',
        'key': API_KEYS['nvidia_1'],
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'model': 'nvidia/llama-3.1-nemotron-70b-instruct',
        'type': 'openai_compatible',
        'priority': 2,
        'cost': 'Free for developers'
    })
    
except Exception as e:
    print(f"❌ NVIDIA API Key 1: FAILED")
    print(f"   Error: {str(e)}")

print()

# Test 3: NVIDIA API Key 2
print("🔄 Testing NVIDIA API Key 2...")
print("-" * 80)
try:
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=API_KEYS['nvidia_2']
    )
    
    response = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=[
            {"role": "user", "content": "Say 'API test successful' in exactly 3 words."}
        ],
        temperature=0.5,
        max_tokens=50
    )
    
    result = response.choices[0].message.content.strip()
    
    print(f"✅ NVIDIA API Key 2: WORKING")
    print(f"   Model: llama-3.1-nemotron-70b-instruct")
    print(f"   Response: {result}")
    print(f"   Tokens used: {response.usage.total_tokens}")
    print(f"   API Key: {API_KEYS['nvidia_2'][:20]}...")
    
    working_apis.append({
        'name': 'NVIDIA NIM (Backup)',
        'key': API_KEYS['nvidia_2'],
        'base_url': 'https://integrate.api.nvidia.com/v1',
        'model': 'nvidia/llama-3.1-nemotron-70b-instruct',
        'type': 'openai_compatible',
        'priority': 3,
        'cost': 'Free for developers'
    })
    
except Exception as e:
    print(f"❌ NVIDIA API Key 2: FAILED")
    print(f"   Error: {str(e)}")

print()

# Test 4: Google Gemini API
print("🔄 Testing Google Gemini API...")
print("-" * 80)
try:
    genai.configure(api_key=API_KEYS['gemini'])
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'API test successful' in exactly 3 words.")
    
    result = response.text.strip()
    
    print(f"✅ Google Gemini API: WORKING")
    print(f"   Model: gemini-pro")
    print(f"   Response: {result}")
    print(f"   API Key: {API_KEYS['gemini'][:20]}...")
    
    working_apis.append({
        'name': 'Google Gemini',
        'key': API_KEYS['gemini'],
        'base_url': None,  # Uses Google SDK
        'model': 'gemini-pro',
        'type': 'google_native',
        'priority': 4,
        'cost': 'Free tier: 60 requests/min'
    })
    
except Exception as e:
    print(f"❌ Google Gemini API: FAILED")
    print(f"   Error: {str(e)}")

print()
print("=" * 80)
print("  Test Results Summary")
print("=" * 80)
print()

if working_apis:
    print(f"✅ Found {len(working_apis)} working API(s)!")
    print()
    
    # Sort by priority
    working_apis.sort(key=lambda x: x['priority'])
    
    print("📊 Working APIs (ordered by priority):")
    print()
    for i, api in enumerate(working_apis, 1):
        print(f"{i}. {api['name']}")
        print(f"   Model: {api['model']}")
        print(f"   Type: {api['type']}")
        print(f"   Cost: {api['cost']}")
        print(f"   Priority: {api['priority']}")
        print()
    
    # Recommend best API
    best_api = working_apis[0]
    print("=" * 80)
    print("  🎯 RECOMMENDED CONFIGURATION")
    print("=" * 80)
    print()
    print(f"Best API: {best_api['name']}")
    print(f"Model: {best_api['model']}")
    print(f"Cost: {best_api['cost']}")
    print()
    
    print("📝 Configuration to add to .env:")
    print("-" * 80)
    
    if best_api['type'] == 'openai_compatible':
        print(f"""
# Best Working AI Configuration: {best_api['name']}
USE_OPENROUTER=False
AI_PROVIDER={best_api['name'].upper().replace(' ', '_').replace('-', '_')}
AI_API_KEY={best_api['key']}
AI_BASE_URL={best_api['base_url']}
AI_MODEL={best_api['model']}
AI_MOCK_MODE=False
""")
    elif best_api['type'] == 'google_native':
        print(f"""
# Best Working AI Configuration: {best_api['name']}
USE_OPENROUTER=False
AI_PROVIDER=GOOGLE_GEMINI
GOOGLE_GEMINI_API_KEY={best_api['key']}
AI_MODEL={best_api['model']}
AI_MOCK_MODE=False
""")
    
    print()
    print("🔧 To apply this configuration:")
    print("   1. Copy the configuration above")
    print("   2. Add it to your .env file")
    print("   3. Restart your Django server")
    print()
    
    # Save configuration to file
    config_file = '/workspaces/CloudEngineered/WORKING_API_CONFIG.txt'
    with open(config_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("  WORKING API CONFIGURATIONS\n")
        f.write("=" * 80 + "\n\n")
        
        for api in working_apis:
            f.write(f"API: {api['name']}\n")
            f.write(f"Priority: {api['priority']}\n")
            f.write(f"Model: {api['model']}\n")
            f.write(f"Cost: {api['cost']}\n")
            f.write(f"Key: {api['key']}\n")
            if api['base_url']:
                f.write(f"Base URL: {api['base_url']}\n")
            f.write("\n" + "-" * 80 + "\n\n")
    
    print(f"✅ Configuration saved to: {config_file}")
    print()
    
else:
    print("❌ No working APIs found!")
    print()
    print("Possible issues:")
    print("  • API keys may be invalid or expired")
    print("  • API services may be down")
    print("  • Network connectivity issues")
    print("  • Rate limits exceeded")
    print()
    print("💡 You can still use AI_MOCK_MODE=True for testing:")
    print("   echo 'AI_MOCK_MODE=True' >> .env")
    print()

print("=" * 80)
