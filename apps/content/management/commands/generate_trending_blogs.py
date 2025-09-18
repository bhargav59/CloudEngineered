"""
Management command to generate trending blog content.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.automation.ai_content_generator import AIContentGenerator
from apps.automation.tasks import generate_trending_content
from apps.tools.models import Tool, Category
from apps.content.models import Article


class Command(BaseCommand):
    help = 'Generate trending blog articles using AI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            help='Generate content for specific category only',
        )
        parser.add_argument(
            '--service',
            type=str,
            choices=['openrouter', 'openai', 'anthropic', 'auto'],
            default='auto',
            help='AI service to use (auto uses best available)',
        )
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model to use (for OpenRouter service)',
        )
        parser.add_argument(
            '--publish',
            action='store_true',
            help='Auto-publish generated articles',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating articles',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🌟 CloudEngineered Trending Blog Generator')
        )
        
        # Initialize AI generator
        try:
            generator = AIContentGenerator()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to initialize AI generator: {e}')
            )
            return

        # Get categories to process
        if options['category']:
            categories = Category.objects.filter(name__icontains=options['category'])
            if not categories.exists():
                self.stdout.write(
                    self.style.ERROR(f'❌ Category "{options["category"]}" not found')
                )
                return
        else:
            categories = Category.objects.filter(
                tools__is_published=True,
                tools__is_trending=True
            ).distinct()

        generated_count = 0
        
        for category in categories:
            self.stdout.write(f'\n📝 Processing {category.name}...')
            
            # Get trending tools
            trending_tools = Tool.objects.filter(
                category=category,
                is_published=True,
                is_trending=True
            ).order_by('-github_stars', '-view_count')[:5]
            
            if trending_tools.count() < 2:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Skipping {category.name}: need at least 2 trending tools'
                    )
                )
                continue
            
            if options['dry_run']:
                self.stdout.write(
                    f'🔍 Would generate article for {category.name} '
                    f'with {trending_tools.count()} tools'
                )
                continue
            
            try:
                # Generate content with flexible AI service
                result = generator.generate_trend_analysis(
                    category.name,
                    list(trending_tools),
                    service=options['service'] if options['service'] != 'auto' else None,
                    model=options['model']
                )
                
                if result.get("success"):
                    # Create article
                    article = Article.objects.create(
                        title=f"Top {category.name} Tools Trending in {timezone.now().strftime('%B %Y')}",
                        excerpt=f"Discover the most popular and trending {category.name.lower()} tools this month.",
                        content=result["content"],
                        article_type="analysis",
                        category=category,
                        ai_generated=True,
                        ai_provider=result.get("service", "auto"),
                        ai_model=result.get("model", "auto"),
                        is_published=options['publish'],
                        meta_title=f"Top {category.name} Tools Trending {timezone.now().strftime('%B %Y')}",
                        meta_description=f"Latest trending {category.name.lower()} tools analysis and recommendations.",
                    )
                    
                    status = "✅ Published" if options['publish'] else "📝 Draft"
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'{status} "{article.title}" ({len(article.content)} chars)'
                        )
                    )
                    generated_count += 1
                    
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Failed to generate content for {category.name}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error processing {category.name}: {e}')
                )
                continue

        # Summary
        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Generated {generated_count} trending blog articles!')
            )
            
            # Run additional trending content task
            self.stdout.write('\n🔄 Running additional trending content generation...')
            task_result = generate_trending_content()
            
            if task_result.get("success"):
                self.stdout.write(
                    self.style.SUCCESS('✅ Additional trending content generated!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Additional content generation issues: {task_result.get("error", "Unknown")}'
                    )
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n🔍 Dry run complete: would generate {len(categories)} articles')
            )
            
        # Show recent articles
        self.stdout.write('\n📰 Recent AI-Generated Articles:')
        recent_articles = Article.objects.filter(
            ai_generated=True
        ).order_by('-created_at')[:5]
        
        for article in recent_articles:
            status = "🌐" if article.is_published else "📝"
            self.stdout.write(
                f'  {status} {article.title} ({article.created_at.strftime("%Y-%m-%d")})'
            )