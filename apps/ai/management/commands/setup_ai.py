"""
Management command to set up initial AI providers, models, and templates
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.ai.models import AIProvider, AIModel, ContentTemplate


class Command(BaseCommand):
    help = 'Set up initial AI providers, models, and content templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of existing data',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('Setting up AI providers and models...'))
        
        with transaction.atomic():
            # Create AI Providers
            self.create_providers(force)
            
            # Create AI Models
            self.create_models(force)
            
            # Create Content Templates
            self.create_templates(force)
        
        self.stdout.write(self.style.SUCCESS('✅ AI setup completed successfully!'))

    def create_providers(self, force):
        """Create AI service providers"""
        providers_data = [
            {
                'name': 'OpenAI',
                'api_key_name': 'OPENAI_API_KEY',
                'base_url': 'https://api.openai.com/v1',
                'rate_limit_per_minute': 500,
                'cost_per_1k_tokens': 0.002,
            },
            {
                'name': 'Anthropic',
                'api_key_name': 'ANTHROPIC_API_KEY',
                'base_url': 'https://api.anthropic.com',
                'rate_limit_per_minute': 1000,
                'cost_per_1k_tokens': 0.008,
            },
            {
                'name': 'Local LLM',
                'api_key_name': 'LOCAL_LLM_API_KEY',
                'base_url': 'http://localhost:11434',
                'rate_limit_per_minute': 100,
                'cost_per_1k_tokens': 0.0,
                'is_active': False,
            }
        ]

        for provider_data in providers_data:
            provider, created = AIProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            
            if created or force:
                for key, value in provider_data.items():
                    if key != 'name':
                        setattr(provider, key, value)
                provider.save()
                
                status = 'Created' if created else 'Updated'
                self.stdout.write(f'  {status} provider: {provider.name}')

    def create_models(self, force):
        """Create AI models"""
        openai = AIProvider.objects.get(name='OpenAI')
        anthropic = AIProvider.objects.get(name='Anthropic')
        
        models_data = [
            {
                'provider': openai,
                'name': 'gpt-4',
                'display_name': 'GPT-4',
                'max_tokens': 8192,
                'supports_functions': True,
                'supports_vision': False,
                'cost_per_1k_input_tokens': 0.03,
                'cost_per_1k_output_tokens': 0.06,
            },
            {
                'provider': openai,
                'name': 'gpt-4-turbo',
                'display_name': 'GPT-4 Turbo',
                'max_tokens': 4096,
                'supports_functions': True,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.01,
                'cost_per_1k_output_tokens': 0.03,
            },
            {
                'provider': openai,
                'name': 'gpt-3.5-turbo',
                'display_name': 'GPT-3.5 Turbo',
                'max_tokens': 4096,
                'supports_functions': True,
                'supports_vision': False,
                'cost_per_1k_input_tokens': 0.0015,
                'cost_per_1k_output_tokens': 0.002,
            },
            {
                'provider': anthropic,
                'name': 'claude-3-sonnet-20240229',
                'display_name': 'Claude 3 Sonnet',
                'max_tokens': 4096,
                'supports_functions': False,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.003,
                'cost_per_1k_output_tokens': 0.015,
            },
            {
                'provider': anthropic,
                'name': 'claude-3-haiku-20240307',
                'display_name': 'Claude 3 Haiku',
                'max_tokens': 4096,
                'supports_functions': False,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.00025,
                'cost_per_1k_output_tokens': 0.00125,
            }
        ]

        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                provider=model_data['provider'],
                name=model_data['name'],
                defaults=model_data
            )
            
            if created or force:
                for key, value in model_data.items():
                    if key not in ['provider', 'name']:
                        setattr(model, key, value)
                model.save()
                
                status = 'Created' if created else 'Updated'
                self.stdout.write(f'  {status} model: {model.display_name}')

    def create_templates(self, force):
        """Create content templates"""
        gpt4 = AIModel.objects.get(name='gpt-4')
        gpt35 = AIModel.objects.get(name='gpt-3.5-turbo')
        
        templates_data = [
            {
                'name': 'Comprehensive Tool Review',
                'template_type': 'tool_review',
                'model': gpt4,
                'system_prompt': """You are a technical writer specializing in cloud engineering and DevOps tools. 
Your task is to write comprehensive, unbiased, and technically accurate tool reviews. 
Focus on practical insights, real-world use cases, and technical details that help engineers make informed decisions.
Write in a professional but accessible tone. Include pros, cons, and specific use cases.""",
                'user_prompt_template': """Write a comprehensive review of {tool_name}.

Tool Information:
- Name: {tool_name}
- Description: {tool_description}
- Key Features: {features}
- Website: {website_url}
- GitHub: {github_url}
- Category: {category}

Please structure the review with the following sections:
1. Overview and Description
2. Key Features and Capabilities
3. Use Cases and Target Audience
4. Pros and Cons
5. Getting Started Guide
6. Pricing and Licensing
7. Alternatives and Comparisons
8. Final Verdict and Recommendations

Make the review approximately 1500-2000 words and include specific technical details and practical examples.""",
                'output_format': 'Markdown format with proper headings, bullet points, and code examples where appropriate.',
            },
            {
                'name': 'Tool Comparison Article',
                'template_type': 'comparison',
                'model': gpt4,
                'system_prompt': """You are an expert technical analyst specializing in cloud engineering tools. 
Create detailed, objective comparisons between tools, focusing on technical capabilities, 
use cases, performance, and practical considerations. Provide clear recommendations for different scenarios.""",
                'user_prompt_template': """Create a comprehensive comparison between {tool1_name} and {tool2_name}.

Tool 1: {tool1_name}
- Description: {tool1_description}
- Key Features: {tool1_features}

Tool 2: {tool2_name}
- Description: {tool2_description}
- Key Features: {tool2_features}

Comparison Category: {category}

Structure the comparison with:
1. Executive Summary
2. Feature Comparison Matrix
3. Performance and Scalability
4. Ease of Use and Learning Curve
5. Community and Ecosystem
6. Pricing Comparison
7. Use Case Scenarios
8. Recommendations (when to choose each tool)

Include specific examples and real-world scenarios. Make it 1200-1500 words.""",
                'output_format': 'Markdown with comparison tables, bullet points, and clear section headings.',
            },
            {
                'name': 'How-to Guide Generator',
                'template_type': 'guide',
                'model': gpt35,
                'system_prompt': """You are a technical instructor creating step-by-step guides for cloud engineering tasks. 
Focus on practical, actionable instructions with clear explanations. 
Include prerequisites, code examples, troubleshooting tips, and best practices.""",
                'user_prompt_template': """Create a step-by-step guide for: {guide_title}

Topic Details:
- Main Tool/Technology: {main_tool}
- Target Audience: {target_audience}
- Difficulty Level: {difficulty_level}
- Prerequisites: {prerequisites}

Structure the guide with:
1. Introduction and Prerequisites
2. Step-by-step Instructions
3. Code Examples and Commands
4. Common Issues and Troubleshooting
5. Best Practices and Tips
6. Next Steps and Further Reading

Make it practical and actionable, approximately 1000-1500 words with code examples.""",
                'output_format': 'Markdown with numbered steps, code blocks, and highlighted tips/warnings.',
            },
            {
                'name': 'Tool Overview (Short)',
                'template_type': 'overview',
                'model': gpt35,
                'system_prompt': """Create concise but informative tool overviews for quick reference. 
Focus on key points, main features, and primary use cases. Keep it brief but comprehensive.""",
                'user_prompt_template': """Create a concise overview of {tool_name}.

Tool Information:
- Name: {tool_name}
- Description: {tool_description}
- Category: {category}
- Key Features: {features}

Include:
1. Brief description (2-3 sentences)
2. Key features (bullet points)
3. Primary use cases
4. Quick pros/cons
5. Getting started info

Keep it under 500 words, optimized for quick scanning.""",
                'output_format': 'Markdown with bullet points and short paragraphs for easy scanning.',
            }
        ]

        for template_data in templates_data:
            template, created = ContentTemplate.objects.get_or_create(
                name=template_data['name'],
                template_type=template_data['template_type'],
                defaults=template_data
            )
            
            if created or force:
                for key, value in template_data.items():
                    if key not in ['name', 'template_type']:
                        setattr(template, key, value)
                template.save()
                
                status = 'Created' if created else 'Updated'
                self.stdout.write(f'  {status} template: {template.name}')

        self.stdout.write(self.style.WARNING('\n📝 Summary:'))
        self.stdout.write(f'  - AI Providers: {AIProvider.objects.count()}')
        self.stdout.write(f'  - AI Models: {AIModel.objects.count()}')
        self.stdout.write(f'  - Content Templates: {ContentTemplate.objects.count()}')
        self.stdout.write(self.style.WARNING('\n⚠️  Note: Set up environment variables for API keys:'))
        self.stdout.write('  - OPENAI_API_KEY=your_openai_key')
        self.stdout.write('  - ANTHROPIC_API_KEY=your_anthropic_key')
