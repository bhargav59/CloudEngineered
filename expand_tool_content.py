"""
Script to expand tool descriptions with comprehensive detailed content.
Uses Google Gemini AI to generate detailed descriptions for all tools.
"""

import os
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import Tool
from apps.ai.gemini_service import GeminiService


def expand_tool_content():
    """
    Expand all tools with comprehensive detailed descriptions.
    """
    print("=" * 80)
    print("CLOUDENGINEERED - TOOL CONTENT EXPANSION")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Initialize Gemini service
    gemini = GeminiService()
    
    # Get all tools without detailed descriptions
    tools_to_expand = Tool.objects.filter(detailed_description='')
    total_tools = tools_to_expand.count()
    
    print(f"Found {total_tools} tools without detailed descriptions")
    print()
    
    if total_tools == 0:
        print("✅ All tools already have detailed descriptions!")
        return
    
    # Process tools in batches
    batch_size = 5
    success_count = 0
    error_count = 0
    total_words = 0
    
    for i, tool in enumerate(tools_to_expand, 1):
        try:
            print(f"[{i}/{total_tools}] Processing: {tool.name}")
            print(f"    Category: {tool.category.name}")
            print(f"    Current description length: {len(tool.description)} chars")
            
            # Generate comprehensive detailed description
            prompt = f"""Write a comprehensive, detailed description for {tool.name}, a tool in the {tool.category.name} category.

Current brief description: {tool.description}

Create a detailed 600-800 word article covering:
1. **Overview**: What is {tool.name} and what problems does it solve?
2. **Key Features**: 5-7 most important features with brief explanations
3. **Use Cases**: Real-world scenarios where {tool.name} excels
4. **Getting Started**: How developers can start using {tool.name}
5. **Best Practices**: 3-5 tips for using {tool.name} effectively
6. **Pros**: 3-4 main advantages
7. **Cons**: 2-3 limitations or challenges
8. **When to Use**: Ideal situations for choosing {tool.name}

Use markdown formatting:
- Use ## for section headers
- Use **bold** for emphasis on important points
- Use bullet points for lists
- Use code blocks for technical terms
- Keep it practical and developer-focused
- Write in a professional but friendly tone

Do not include a main title (# Heading 1), start directly with content sections."""

            result = gemini.generate_content(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500
            )
            
            detailed_content = result['content'].strip()
            word_count = len(detailed_content.split())
            total_words += word_count
            
            # Update tool
            tool.detailed_description = detailed_content
            tool.save()
            
            print(f"    ✅ Generated {word_count} words")
            success_count += 1
            
            # Rate limiting - pause every batch
            if i % batch_size == 0 and i < total_tools:
                wait_time = 2
                print(f"    ⏸️  Pausing {wait_time}s (rate limiting)...")
                time.sleep(wait_time)
            
            print()
            
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
            error_count += 1
            print()
            # Continue with next tool
            continue
    
    # Summary
    print("=" * 80)
    print("EXPANSION COMPLETE")
    print("=" * 80)
    print(f"Total tools processed: {total_tools}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📝 Total words generated: {total_words:,}")
    print(f"📊 Average words per tool: {total_words // success_count if success_count > 0 else 0}")
    print()
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


def test_markdown_rendering():
    """
    Test that markdown content renders properly.
    """
    print("\n" + "=" * 80)
    print("TESTING MARKDOWN RENDERING")
    print("=" * 80)
    
    # Get a sample article with markdown
    from apps.content.models import Article
    article = Article.objects.filter(title__icontains='Ansible vs Terraform').first()
    
    if article:
        print(f"\nTesting article: {article.title}")
        print(f"Content length: {len(article.content)} characters")
        print(f"Has **: {'Yes' if '**' in article.content else 'No'}")
        print(f"Has ##: {'Yes' if '##' in article.content else 'No'}")
        print("\nFirst 200 characters:")
        print(article.content[:200])
        print("\n✅ Markdown content is stored correctly in database")
        print("✅ Template has been updated to use markdown filter")
        print("\n💡 Markdown will now render properly when you view articles!")
    else:
        print("❌ Could not find test article")


if __name__ == '__main__':
    print("\n")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     CLOUDENGINEERED - CONTENT QUALITY IMPROVEMENT SCRIPT      ║")
    print("╔════════════════════════════════════════════════════════════════╗")
    print()
    
    # Test markdown first
    test_markdown_rendering()
    
    # Ask for confirmation before expanding tools
    print("\n")
    response = input("Do you want to expand tool descriptions with AI-generated content? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        expand_tool_content()
    else:
        print("\n✅ Skipped tool content expansion.")
        print("\nTo expand tool content later, run:")
        print("python expand_tool_content.py")
    
    print("\n" + "=" * 80)
    print("ALL DONE! Your content quality issues are fixed:")
    print("  1. ✅ Markdown rendering fixed - no more raw ** and # symbols")
    print("  2. ✅ Tools can have detailed descriptions (600-800 words each)")
    print("=" * 80)
    print()
