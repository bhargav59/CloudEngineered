"""
Management command to test AI integration with tools
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tools.models import Tool, Category
from apps.ai.models import ContentTemplate
from apps.ai.services import ContentGenerator
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Test AI integration with tools'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tool-id',
            type=int,
            help='Specific tool ID to generate content for'
        )
        parser.add_argument(
            '--content-type',
            choices=['review', 'tutorial', 'guide', 'comparison'],
            default='review',
            help='Type of content to generate'
        )
        parser.add_argument(
            '--mock',
            action='store_true',
            help='Use mock mode for testing'
        )

    def handle(self, *args, **options):
        self.stdout.write("Testing AI Integration with Tools...")
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='ai_test_user',
            defaults={'email': 'ai_test@example.com', 'is_staff': True}
        )
        if created:
            self.stdout.write(f"Created test user: {user.username}")
        
        # Get tool to test with
        tool_id = options.get('tool_id')
        if tool_id:
            try:
                tool = Tool.objects.get(id=tool_id)
            except Tool.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Tool with ID {tool_id} not found")
                )
                return
        else:
            # Get or create a test tool
            category, _ = Category.objects.get_or_create(
                name='Development Tools',
                defaults={'slug': 'development-tools', 'description': 'Tools for developers'}
            )
            
            tool, created = Tool.objects.get_or_create(
                name='Docker',
                defaults={
                    'slug': 'docker',
                    'description': 'Docker is a platform for developing, shipping, and running applications using containerization technology.',
                    'category': category,
                    'website_url': 'https://www.docker.com',
                    'github_url': 'https://github.com/docker/docker'
                }
            )
            if created:
                self.stdout.write(f"Created test tool: {tool.name}")
        
        self.stdout.write(f"Testing with tool: {tool.name} (ID: {tool.id})")
        
        # Get content template
        content_type = options.get('content_type', 'review')
        template_type_map = {
            'review': 'tool_review',
            'tutorial': 'tutorial',
            'guide': 'how_to_guide',
            'comparison': 'comparison'
        }
        
        template_type = template_type_map.get(content_type, 'tool_review')
        template = ContentTemplate.objects.filter(
            template_type=template_type,
            is_active=True
        ).first()
        
        if not template:
            self.stdout.write(
                self.style.ERROR(f"No {content_type} template found")
            )
            return
        
        self.stdout.write(f"Using template: {template.name} ({template.template_type})")
        
        # Prepare input data
        input_data = {
            'tool_name': tool.name,
            'tool_description': tool.description,
            'category': tool.category.name if tool.category else 'General',
            'website_url': tool.website_url or '',
            'github_url': tool.github_url or '',
            'pricing': 'Free/Open Source',
            'features': tool.description,
            'target_audience': 'developers',
            'use_cases': 'containerization, application deployment, microservices',
            'alternatives': 'Podman, containerd, LXC'
        }
        
        self.stdout.write("Input data:")
        self.stdout.write(json.dumps(input_data, indent=2))
        
        # Generate content
        try:
            generator = ContentGenerator()
            
            if options.get('mock'):
                self.stdout.write("Using mock mode...")
                result = generator.generate_content(
                    template=template,
                    input_data=input_data,
                    user=user,
                    mock=True
                )
            else:
                self.stdout.write("Generating real content...")
                result = generator.generate_content(
                    template=template,
                    input_data=input_data,
                    user=user,
                    mock=False
                )
            
            self.stdout.write(self.style.SUCCESS("Content generation successful!"))
            self.stdout.write(f"Tokens used: {result.get('tokens_used', 'N/A')}")
            self.stdout.write(f"Estimated cost: ${result.get('cost', 'N/A')}")
            self.stdout.write(f"Processing time: {result.get('processing_time', 'N/A')}s")
            
            content = result.get('content', '')
            if content:
                self.stdout.write("\nGenerated Content:")
                self.stdout.write("-" * 50)
                # Show first 500 characters
                preview = content[:500] + "..." if len(content) > 500 else content
                self.stdout.write(preview)
                self.stdout.write("-" * 50)
                self.stdout.write(f"Total content length: {len(content)} characters")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Content generation failed: {str(e)}")
            )
            return
        
        self.stdout.write(self.style.SUCCESS("AI Integration test completed successfully!"))
        
        # Show integration statistics
        self.stdout.write("\nIntegration Statistics:")
        self.stdout.write(f"- Tool: {tool.name}")
        self.stdout.write(f"- Category: {tool.category.name if tool.category else 'None'}")
        self.stdout.write(f"- Template Type: {template_type}")
        self.stdout.write(f"- Content Type: {content_type}")
        self.stdout.write(f"- Mock Mode: {'Yes' if options.get('mock') else 'No'}")
        
        if not options.get('mock'):
            # Show real generation record
            from apps.ai.models import ContentGeneration
            recent_generation = ContentGeneration.objects.filter(
                initiated_by=user,
                input_data__icontains=tool.name
            ).order_by('-created_at').first()
            
            if recent_generation:
                self.stdout.write(f"- Generation ID: {recent_generation.id}")
                self.stdout.write(f"- Status: {recent_generation.status}")
                self.stdout.write(f"- Created: {recent_generation.created_at}")
