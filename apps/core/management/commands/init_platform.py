"""
Management command to initialize the platform with sample data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SiteConfiguration
from apps.tools.models import Category, Tool
from apps.content.models import Article

User = get_user_model()


class Command(BaseCommand):
    help = 'Initialize CloudEngineered platform with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Initializing CloudEngineered platform...'))

        # Create site configuration
        config, created = SiteConfiguration.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'CloudEngineered',
                'site_description': 'Comprehensive reviews and comparisons of cloud engineering and DevOps tools',
                'contact_email': 'contact@cloudengineered.io',
                'support_email': 'support@cloudengineered.io',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Site configuration created'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Site configuration already exists'))

        # Create categories
        categories_data = [
            {
                'name': 'CI/CD',
                'description': 'Continuous Integration and Continuous Deployment tools',
                'icon': 'fas fa-code-branch',
                'color': '#10B981'
            },
            {
                'name': 'Monitoring',
                'description': 'Application and infrastructure monitoring tools',
                'icon': 'fas fa-chart-line',
                'color': '#3B82F6'
            },
            {
                'name': 'Container',
                'description': 'Container orchestration and management tools',
                'icon': 'fab fa-docker',
                'color': '#8B5CF6'
            },
            {
                'name': 'Infrastructure',
                'description': 'Infrastructure as Code and provisioning tools',
                'icon': 'fas fa-server',
                'color': '#F59E0B'
            },
            {
                'name': 'Security',
                'description': 'DevSecOps and security scanning tools',
                'icon': 'fas fa-shield-alt',
                'color': '#EF4444'
            },
            {
                'name': 'API Management',
                'description': 'API gateways and management platforms',
                'icon': 'fas fa-exchange-alt',
                'color': '#06B6D4'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'✅ Created category: {category.name}')

        # Create sample tools
        tools_data = [
            {
                'name': 'Kubernetes',
                'description': 'Production-Grade Container Orchestration platform for automating deployment, scaling, and management of containerized applications.',
                'category': 'Container',
                'website_url': 'https://kubernetes.io/',
                'github_url': 'https://github.com/kubernetes/kubernetes',
                'pricing_model': 'open_source',
                'is_featured': True,
                'features': [
                    'Container orchestration',
                    'Auto-scaling',
                    'Service discovery',
                    'Load balancing',
                    'Self-healing'
                ]
            },
            {
                'name': 'Terraform',
                'description': 'Infrastructure as Code tool that lets you build, change, and version infrastructure safely and efficiently.',
                'category': 'Infrastructure',
                'website_url': 'https://www.terraform.io/',
                'github_url': 'https://github.com/hashicorp/terraform',
                'pricing_model': 'freemium',
                'is_featured': True,
                'features': [
                    'Infrastructure as Code',
                    'Multi-cloud support',
                    'State management',
                    'Plan and apply workflow'
                ]
            },
            {
                'name': 'Prometheus',
                'description': 'Open-source monitoring system with a dimensional data model, flexible query language, and alerting.',
                'category': 'Monitoring',
                'website_url': 'https://prometheus.io/',
                'github_url': 'https://github.com/prometheus/prometheus',
                'pricing_model': 'open_source',
                'is_featured': True,
                'features': [
                    'Time series monitoring',
                    'PromQL query language',
                    'Alerting',
                    'Service discovery'
                ]
            }
        ]

        for tool_data in tools_data:
            try:
                category = Category.objects.get(name=tool_data['category'])
                tool_data['category'] = category
                tool, created = Tool.objects.get_or_create(
                    name=tool_data['name'],
                    defaults=tool_data
                )
                if created:
                    self.stdout.write(f'✅ Created tool: {tool.name}')
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Category not found: {tool_data["category"]}'))

        self.stdout.write(self.style.SUCCESS('🎉 Platform initialization complete!'))
        self.stdout.write(self.style.SUCCESS('Next steps:'))
        self.stdout.write('1. Run: python manage.py runserver')
        self.stdout.write('2. Visit: http://localhost:8000')
        self.stdout.write('3. Admin: http://localhost:8000/admin')
