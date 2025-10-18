"""
Management command to validate and fix slugs across all models.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
import re

from apps.content.models import Article
from apps.tools.models import Tool, ToolComparison, Category


class Command(BaseCommand):
    help = 'Validates and fixes slugs that contain invalid URL characters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually fix the slugs (default is dry-run)',
        )

    def handle(self, *args, **options):
        fix_mode = options['fix']
        
        if fix_mode:
            self.stdout.write(self.style.WARNING('🔧 FIX MODE: Will update invalid slugs'))
        else:
            self.stdout.write(self.style.WARNING('👀 DRY-RUN MODE: No changes will be made'))
            self.stdout.write(self.style.WARNING('   Use --fix to actually update slugs\n'))
        
        total_fixed = 0
        
        # Check Articles
        self.stdout.write('\n📰 Checking Articles...')
        total_fixed += self.check_model(Article, fix_mode)
        
        # Check Tools
        self.stdout.write('\n🔧 Checking Tools...')
        total_fixed += self.check_model(Tool, fix_mode)
        
        # Check Tool Comparisons
        self.stdout.write('\n⚖️  Checking Tool Comparisons...')
        total_fixed += self.check_model(ToolComparison, fix_mode)
        
        # Check Categories
        self.stdout.write('\n📁 Checking Categories...')
        total_fixed += self.check_model(Category, fix_mode)
        
        # Summary
        self.stdout.write('\n' + '='*60)
        if fix_mode:
            self.stdout.write(self.style.SUCCESS(f'✅ Fixed {total_fixed} invalid slugs'))
        else:
            self.stdout.write(self.style.WARNING(f'Found {total_fixed} invalid slugs (dry-run)'))
            if total_fixed > 0:
                self.stdout.write(self.style.WARNING('Run with --fix to update them'))
        self.stdout.write('='*60 + '\n')

    def check_model(self, model, fix_mode):
        """Check all instances of a model for invalid slugs."""
        fixed_count = 0
        
        for obj in model.objects.all():
            if not hasattr(obj, 'slug'):
                continue
            
            # Check if slug contains invalid characters
            # Valid pattern: [-a-zA-Z0-9_]
            if not re.match(r'^[-a-zA-Z0-9_]+$', obj.slug):
                old_slug = obj.slug
                
                # Fix the slug
                new_slug = re.sub(r'[^-a-zA-Z0-9_]', '-', obj.slug)
                
                # Remove multiple consecutive hyphens
                new_slug = re.sub(r'-+', '-', new_slug)
                
                # Remove leading/trailing hyphens
                new_slug = new_slug.strip('-')
                
                self.stdout.write(
                    f'  ❌ {model.__name__}: {old_slug}\n'
                    f'     → {new_slug}'
                )
                
                if fix_mode:
                    obj.slug = new_slug
                    obj.save(update_fields=['slug'])
                    self.stdout.write(self.style.SUCCESS('     ✅ Fixed!'))
                
                fixed_count += 1
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS(f'   ✅ All {model.__name__} slugs are valid'))
        
        return fixed_count
