from django.core.management.base import BaseCommand
from apps.ai.models import AIProvider, AIModel


class Command(BaseCommand):
    help = 'Populate AI providers and models'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up AI providers and models...'))

        # Create OpenAI provider
        openai_provider, created = AIProvider.objects.get_or_create(
            name='OpenAI',
            defaults={
                'api_key_name': 'OPENAI_API_KEY',
                'base_url': 'https://api.openai.com/v1',
                'is_active': True,
                'rate_limit_per_minute': 60,
                'cost_per_1k_tokens': 0.002,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created provider: {openai_provider.name}'))

        # Create OpenAI models
        openai_models = [
            {
                'name': 'gpt-4o',
                'display_name': 'GPT-4o',
                'max_tokens': 4096,
                'supports_functions': True,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.005,
                'cost_per_1k_output_tokens': 0.015,
            },
            {
                'name': 'gpt-4o-mini',
                'display_name': 'GPT-4o Mini',
                'max_tokens': 16384,
                'supports_functions': True,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.00015,
                'cost_per_1k_output_tokens': 0.0006,
            },
            {
                'name': 'gpt-3.5-turbo',
                'display_name': 'GPT-3.5 Turbo',
                'max_tokens': 4096,
                'supports_functions': True,
                'supports_vision': False,
                'cost_per_1k_input_tokens': 0.0005,
                'cost_per_1k_output_tokens': 0.0015,
            },
        ]

        for model_data in openai_models:
            model, created = AIModel.objects.get_or_create(
                provider=openai_provider,
                name=model_data['name'],
                defaults=model_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created model: {model.display_name}'))

        # Create Anthropic provider
        anthropic_provider, created = AIProvider.objects.get_or_create(
            name='Anthropic',
            defaults={
                'api_key_name': 'ANTHROPIC_API_KEY',
                'base_url': 'https://api.anthropic.com',
                'is_active': True,
                'rate_limit_per_minute': 60,
                'cost_per_1k_tokens': 0.008,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created provider: {anthropic_provider.name}'))

        # Create Anthropic models
        anthropic_models = [
            {
                'name': 'claude-3-5-sonnet-20241022',
                'display_name': 'Claude 3.5 Sonnet',
                'max_tokens': 8192,
                'supports_functions': True,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.003,
                'cost_per_1k_output_tokens': 0.015,
            },
            {
                'name': 'claude-3-haiku-20240307',
                'display_name': 'Claude 3 Haiku',
                'max_tokens': 4096,
                'supports_functions': True,
                'supports_vision': True,
                'cost_per_1k_input_tokens': 0.00025,
                'cost_per_1k_output_tokens': 0.00125,
            },
        ]

        for model_data in anthropic_models:
            model, created = AIModel.objects.get_or_create(
                provider=anthropic_provider,
                name=model_data['name'],
                defaults=model_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created model: {model.display_name}'))

        self.stdout.write(self.style.SUCCESS('AI providers and models setup complete!'))
        
        # Display summary
        providers_count = AIProvider.objects.count()
        models_count = AIModel.objects.count()
        active_models = AIModel.objects.filter(is_active=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'- {providers_count} AI providers configured\n'
                f'- {models_count} AI models available\n'
                f'- {active_models} active models ready for use'
            )
        )
