"""
Management command to populate search suggestions and analytics data.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.core.models import SearchSuggestion, PopularSearch
from apps.tools.models import Tool, Category


class Command(BaseCommand):
    help = 'Populate search suggestions and initial analytics data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all search data before populating',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all search data...'))
            SearchSuggestion.objects.all().delete()
            PopularSearch.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Populating search suggestions...'))
        
        with transaction.atomic():
            self._populate_tool_suggestions()
            self._populate_category_suggestions()
            self._populate_general_suggestions()
            self._populate_popular_searches()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated search suggestions!')
        )

    def _populate_tool_suggestions(self):
        """Add tool names as search suggestions"""
        tools = Tool.objects.all()
        created_count = 0
        
        for tool in tools:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=tool.name,
                defaults={
                    'category': 'Tools',
                    'priority': 2,
                    'search_count': 0
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} tool suggestions')

    def _populate_category_suggestions(self):
        """Add category names as search suggestions"""
        categories = Category.objects.all()
        created_count = 0
        
        for category in categories:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=category.name,
                defaults={
                    'category': 'Categories',
                    'priority': 3,
                    'search_count': 0
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} category suggestions')

    def _populate_general_suggestions(self):
        """Add general cloud/DevOps related search suggestions"""
        general_suggestions = [
            # Cloud Platforms
            ('AWS', 'Cloud Platforms', 5),
            ('Azure', 'Cloud Platforms', 5),
            ('Google Cloud', 'Cloud Platforms', 5),
            ('GCP', 'Cloud Platforms', 4),
            
            # DevOps Tools
            ('Kubernetes', 'Container Orchestration', 5),
            ('Docker', 'Containerization', 5),
            ('CI/CD', 'Development', 5),
            ('Jenkins', 'CI/CD', 4),
            ('GitHub Actions', 'CI/CD', 4),
            ('GitLab CI', 'CI/CD', 4),
            
            # Monitoring & Observability
            ('Prometheus', 'Monitoring', 4),
            ('Grafana', 'Monitoring', 4),
            ('ELK Stack', 'Logging', 4),
            ('Elasticsearch', 'Search & Analytics', 4),
            ('Datadog', 'Monitoring', 3),
            ('New Relic', 'Monitoring', 3),
            
            # Infrastructure
            ('Terraform', 'Infrastructure as Code', 5),
            ('Ansible', 'Configuration Management', 4),
            ('Helm', 'Package Management', 3),
            ('Istio', 'Service Mesh', 3),
            
            # Security
            ('security scanning', 'Security', 4),
            ('vulnerability assessment', 'Security', 3),
            ('compliance tools', 'Security', 3),
            ('SAST', 'Security', 3),
            ('DAST', 'Security', 3),
            
            # Development
            ('API gateway', 'Development', 3),
            ('microservices', 'Architecture', 4),
            ('serverless', 'Architecture', 4),
            ('load balancer', 'Infrastructure', 3),
            ('database tools', 'Data', 3),
            
            # Popular searches
            ('deployment tools', 'General', 4),
            ('monitoring solutions', 'General', 4),
            ('cloud migration', 'General', 3),
            ('backup solutions', 'General', 3),
            ('cost optimization', 'General', 3),
        ]
        
        created_count = 0
        for suggestion_text, category, priority in general_suggestions:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=suggestion_text,
                defaults={
                    'category': category,
                    'priority': priority,
                    'search_count': 0
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} general suggestions')

    def _populate_popular_searches(self):
        """Add some initial popular searches"""
        popular_searches = [
            ('kubernetes', 45, 12),
            ('docker', 38, 15),
            ('monitoring', 32, 18),
            ('ci/cd', 28, 14),
            ('security', 25, 16),
            ('terraform', 22, 11),
            ('aws', 35, 20),
            ('prometheus', 18, 9),
            ('grafana', 16, 8),
            ('jenkins', 20, 10),
        ]
        
        created_count = 0
        for query, search_count, unique_users in popular_searches:
            popular_search, created = PopularSearch.objects.get_or_create(
                query=query,
                defaults={
                    'search_count': search_count,
                    'unique_users': unique_users,
                    'last_week_count': search_count // 4,
                    'last_month_count': search_count,
                    'is_trending': search_count > 30
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} popular searches')
