"""
Management command to generate content using AI templates
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.ai.models import ContentTemplate
from apps.ai.services import ContentGenerator

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate content using AI templates'

    def add_arguments(self, parser):
        parser.add_argument('template_id', type=int, help='ID of the content template to use')
        parser.add_argument('--tool-name', type=str, help='Name of the tool to review')
        parser.add_argument('--tool-description', type=str, help='Description of the tool')
        parser.add_argument('--features', type=str, help='Comma-separated list of features')
        parser.add_argument('--category', type=str, help='Tool category')
        parser.add_argument('--website-url', type=str, help='Tool website URL')
        parser.add_argument('--github-url', type=str, help='Tool GitHub URL')
        parser.add_argument('--user-id', type=int, help='ID of the user generating content')
        parser.add_argument('--output-file', type=str, help='File to save generated content')

    def handle(self, *args, **options):
        template_id = options['template_id']
        
        try:
            template = ContentTemplate.objects.get(id=template_id, is_active=True)
        except ContentTemplate.DoesNotExist:
            raise CommandError(f'Template with ID {template_id} not found or inactive')

        self.stdout.write(f'Using template: {template.name} ({template.get_template_type_display()})')
        
        # Collect input data based on template type
        input_data = self.collect_input_data(template, options)
        
        if not input_data:
            raise CommandError('No input data provided. Use appropriate --tool-* arguments.')

        self.stdout.write('Generating content...')
        
        try:
            generator = ContentGenerator()
            generation = generator.generate_from_template(
                template_id=template_id,
                input_data=input_data,
                user_id=options.get('user_id')
            )
            
            self.stdout.write(self.style.SUCCESS(f'✅ Content generated successfully!'))
            self.stdout.write(f'Generation ID: {generation.id}')
            self.stdout.write(f'Status: {generation.status}')
            self.stdout.write(f'Tokens used: {generation.tokens_used}')
            self.stdout.write(f'Estimated cost: ${generation.estimated_cost}')
            
            # Output the generated content
            self.stdout.write(self.style.WARNING('\n📝 Generated Content:'))
            self.stdout.write('=' * 80)
            self.stdout.write(generation.generated_content)
            self.stdout.write('=' * 80)
            
            # Save to file if requested
            if options.get('output_file'):
                with open(options['output_file'], 'w', encoding='utf-8') as f:
                    f.write(generation.generated_content)
                self.stdout.write(f'Content saved to: {options["output_file"]}')
            
            # Show quality assessment if available
            if hasattr(generation, 'quality'):
                quality = generation.quality
                self.stdout.write(self.style.WARNING('\n📊 Quality Assessment:'))
                self.stdout.write(f'Word count: {quality.word_count}')
                self.stdout.write(f'Readability score: {quality.readability_score:.1f}')
                self.stdout.write(f'Has headings: {quality.has_headings}')
                self.stdout.write(f'Has links: {quality.has_links}')
                self.stdout.write(f'Requires review: {quality.requires_human_review}')
            
        except Exception as e:
            raise CommandError(f'Content generation failed: {str(e)}')

    def collect_input_data(self, template, options):
        """Collect input data based on template type and provided options"""
        input_data = {}
        
        # Common fields
        if options.get('tool_name'):
            input_data['tool_name'] = options['tool_name']
        if options.get('tool_description'):
            input_data['tool_description'] = options['tool_description']
        if options.get('features'):
            input_data['features'] = options['features']
        if options.get('category'):
            input_data['category'] = options['category']
        if options.get('website_url'):
            input_data['website_url'] = options['website_url']
        if options.get('github_url'):
            input_data['github_url'] = options['github_url']
        
        # Template-specific fields
        if template.template_type == 'comparison':
            # For comparison templates, you'd need tool1_* and tool2_* fields
            pass
        elif template.template_type == 'guide':
            # For guide templates, you'd need guide_title, main_tool, etc.
            if options.get('tool_name'):
                input_data['guide_title'] = f"How to use {options['tool_name']}"
                input_data['main_tool'] = options['tool_name']
                input_data['target_audience'] = "DevOps Engineers and Cloud Architects"
                input_data['difficulty_level'] = "Intermediate"
                input_data['prerequisites'] = "Basic command line knowledge"
        
        return input_data
