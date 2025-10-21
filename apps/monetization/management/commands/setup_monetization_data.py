"""
Management command to set up initial monetization data
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.monetization.models import PremiumTier
from apps.monetization.premium_reports import ReportTemplate
from apps.monetization.consulting import ConsultingPackage


class Command(BaseCommand):
    help = 'Set up initial monetization data (tiers, packages, templates)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up monetization data...'))

        with transaction.atomic():
            # Create Premium Tiers
            self.stdout.write('Creating premium subscription tiers...')
            self.create_premium_tiers()

            # Create Report Templates
            self.stdout.write('Creating report templates...')
            self.create_report_templates()

            # Create Consulting Packages
            self.stdout.write('Creating consulting packages...')
            self.create_consulting_packages()

        self.stdout.write(self.style.SUCCESS('✅ Monetization data setup complete!'))

    def create_premium_tiers(self):
        """Create premium subscription tiers"""
        tiers = [
            {
                'name': 'Pro',
                'slug': 'pro',
                'description': 'For teams building with DevOps tools',
                'price_monthly': Decimal('29.00'),
                'price_yearly': Decimal('290.00'),
                'discount_percentage': 17,
                'features': [
                    "Custom tool recommendations powered by AI",
                    "Team collaboration (up to 10 members)",
                    "Integration roadmaps with timelines",
                    "Advanced cost calculators with TCO analysis",
                    "Priority email support (24hr response)",
                    "Advanced analytics and insights",
                    "PDF/CSV report exports",
                    "API access for automation"
                ],
                'limits': {
                    'api_calls_per_month': 10000,
                    'report_downloads': 50,
                    'custom_recommendations': 20
                },
                'access_level': 2,
                'max_team_members': 10,
                'is_featured': True,
                'sort_order': 1,
                'badge_text': 'Most Popular'
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'description': 'For organizations at scale',
                'price_monthly': Decimal('99.00'),
                'price_yearly': Decimal('990.00'),
                'discount_percentage': 17,
                'features': [
                    "Everything in Pro",
                    "Unlimited team members",
                    "White-label reports with your branding",
                    "Dedicated account manager",
                    "Custom integrations (webhooks, SSO)",
                    "99.9% SLA guarantee",
                    "Priority phone support",
                    "$500/year consulting credits",
                    "Advanced security features",
                    "Custom training sessions"
                ],
                'limits': {
                    'api_calls_per_month': 100000,
                    'report_downloads': -1,  # Unlimited
                    'custom_recommendations': -1  # Unlimited
                },
                'access_level': 3,
                'max_team_members': 999,
                'is_featured': False,
                'sort_order': 2,
                'badge_text': 'Best Value'
            }
        ]

        for tier_data in tiers:
            tier, created = PremiumTier.objects.get_or_create(
                slug=tier_data['slug'],
                defaults=tier_data
            )
            if created:
                self.stdout.write(f'  ✓ Created tier: {tier.name}')
            else:
                self.stdout.write(f'  - Tier already exists: {tier.name}')

    def create_report_templates(self):
        """Create report templates"""
        templates = [
            {
                'name': 'CI/CD Tool Comparison Report',
                'slug': 'cicd-comparison',
                'description': 'Comprehensive comparison of CI/CD tools for your specific needs',
                'report_type': 'tool_comparison',
                'price_basic': Decimal('29.00'),
                'price_standard': Decimal('59.00'),
                'price_premium': Decimal('99.00'),
                'basic_features': [
                    'Compare up to 3 CI/CD tools',
                    'Basic pros and cons analysis',
                    'Feature comparison matrix',
                    'Pricing overview',
                    '10-15 page PDF report'
                ],
                'standard_features': [
                    'Compare up to 5 CI/CD tools',
                    'Detailed feature analysis',
                    'Cost calculator with TCO',
                    'Integration assessment',
                    'Migration complexity analysis',
                    'Security considerations',
                    '20-30 page PDF report'
                ],
                'premium_features': [
                    'Unlimited tool comparisons',
                    'Custom recommendations for your tech stack',
                    'Implementation timeline',
                    'ROI projections',
                    'Team training recommendations',
                    '30-minute consultation call',
                    '40+ page comprehensive PDF report'
                ]
            },
            {
                'name': 'Container Orchestration Assessment',
                'slug': 'container-orchestration',
                'description': 'In-depth analysis of Kubernetes, Docker Swarm, and alternatives',
                'report_type': 'tool_comparison',
                'price_basic': Decimal('29.00'),
                'price_standard': Decimal('59.00'),
                'price_premium': Decimal('99.00'),
                'basic_features': [
                    'Kubernetes vs Docker Swarm comparison',
                    'Basic architecture overview',
                    'Pricing comparison',
                    '10-15 page report'
                ],
                'standard_features': [
                    'Full orchestration platform comparison',
                    'Scaling and performance analysis',
                    'Security best practices',
                    'Cost projections',
                    '20-30 page report'
                ],
                'premium_features': [
                    'Custom architecture recommendations',
                    'Migration planning guide',
                    'Disaster recovery strategies',
                    'Consultation call',
                    '40+ page report'
                ],
            },
            {
                'name': 'DevOps Monitoring Stack Report',
                'slug': 'monitoring-stack',
                'description': 'Choose the right monitoring tools for your infrastructure',
                'report_type': 'tech_stack',
                'price_basic': Decimal('29.00'),
                'price_standard': Decimal('59.00'),
                'price_premium': Decimal('99.00'),
                'basic_features': [
                    'Top 3 monitoring tools compared',
                    'Feature matrix',
                    'Pricing overview',
                    '10-15 page report'
                ],
                'standard_features': [
                    '5+ monitoring solutions analyzed',
                    'Integration capabilities',
                    'Alert management comparison',
                    'Cost-benefit analysis',
                    '20-30 page report'
                ],
                'premium_features': [
                    'Complete observability stack recommendation',
                    'Custom dashboard designs',
                    'Implementation roadmap',
                    'Consultation call',
                    '40+ page report'
                ],
            },
            {
                'name': 'Cloud Migration Planning Report',
                'slug': 'cloud-migration',
                'description': 'Step-by-step guide for migrating to AWS, GCP, or Azure',
                'report_type': 'migration_plan',
                'price_basic': Decimal('39.00'),
                'price_standard': Decimal('79.00'),
                'price_premium': Decimal('149.00'),
                'basic_features': [
                    'Cloud provider comparison',
                    'Basic migration checklist',
                    'Cost estimates',
                    '15-20 page report'
                ],
                'standard_features': [
                    'Detailed migration phases',
                    'Service mapping',
                    'Risk assessment',
                    'Cost optimization strategies',
                    '30-40 page report'
                ],
                'premium_features': [
                    'Custom migration roadmap',
                    'Architecture diagrams',
                    'Rollback strategies',
                    'Team training plan',
                    '60-minute consultation',
                    '50+ page report'
                ],
            },
            {
                'name': 'Security & Compliance Audit',
                'slug': 'security-audit',
                'description': 'DevSecOps tools and compliance assessment',
                'report_type': 'security_audit',
                'price_basic': Decimal('49.00'),
                'price_standard': Decimal('99.00'),
                'price_premium': Decimal('199.00'),
                'basic_features': [
                    'Top security tools overview',
                    'Basic compliance checklist',
                    'Vulnerability scanning comparison',
                    '15-20 page report'
                ],
                'standard_features': [
                    'Comprehensive security tool analysis',
                    'Compliance framework mapping',
                    'Security posture assessment',
                    'Cost analysis',
                    '35-45 page report'
                ],
                'premium_features': [
                    'Custom security roadmap',
                    'Zero-trust architecture design',
                    'Compliance automation strategy',
                    'Incident response planning',
                    '90-minute consultation',
                    '60+ page report'
                ],
            }
        ]

        for template_data in templates:
            template, created = ReportTemplate.objects.get_or_create(
                slug=template_data['slug'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'  ✓ Created template: {template.name}')
            else:
                self.stdout.write(f'  - Template already exists: {template.name}')

    def create_consulting_packages(self):
        """Create consulting packages"""
        packages = [
            {
                'name': 'Discovery Call',
                'slug': 'discovery-call',
                'description': 'Quick 30-minute call to understand your needs and provide initial guidance',
                'package_type': 'discovery',
                'price': Decimal('149.00'),
                'duration_hours': Decimal('0.5'),
                'deliverables': [
                    'Initial assessment of current tools',
                    'Pain point identification',
                    'High-level tool recommendations',
                    'Q&A session',
                    'Email summary of discussion'
                ],
                'sort_order': 1
            },
            {
                'name': 'Strategy Session',
                'slug': 'strategy-session',
                'description': 'Deep dive into your DevOps challenges with actionable recommendations',
                'package_type': 'strategy',
                'price': Decimal('399.00'),
                'duration_hours': Decimal('1.0'),
                'deliverables': [
                    'Deep dive into current tech stack',
                    'Detailed tool recommendations',
                    'Implementation timeline (high-level)',
                    'Cost-benefit analysis',
                    'Written summary report (5-10 pages)',
                    '1 week email support'
                ],
                'sort_order': 2
            },
            {
                'name': 'Deep Dive Analysis',
                'slug': 'deep-dive',
                'description': 'Comprehensive 2-hour session with detailed analysis and roadmap',
                'package_type': 'deep_dive',
                'price': Decimal('799.00'),
                'duration_hours': Decimal('2.0'),
                'deliverables': [
                    'Everything in Strategy Session',
                    'Multiple solution scenarios',
                    'Risk assessment matrix',
                    'Detailed migration planning',
                    'Team training recommendations',
                    'Architecture review',
                    '15-20 page detailed report',
                    '2 weeks email support'
                ],
                'sort_order': 3
            },
            {
                'name': 'Team Workshop',
                'slug': 'team-workshop',
                'description': 'Half-day hands-on workshop for your entire team',
                'package_type': 'workshop',
                'price': Decimal('1499.00'),
                'duration_hours': Decimal('4.0'),
                'deliverables': [
                    'Everything in Deep Dive',
                    'Hands-on exercises and demos',
                    'Team alignment session',
                    'Tool evaluation workshop',
                    'Live architecture review',
                    'Implementation playbook',
                    '25-30 page comprehensive report',
                    '30 days email support'
                ],
                'sort_order': 4
            },
            {
                'name': 'Comprehensive Assessment',
                'slug': 'comprehensive',
                'description': 'Full-day complete DevOps transformation planning',
                'package_type': 'full_day',
                'price': Decimal('2999.00'),
                'duration_hours': Decimal('8.0'),
                'deliverables': [
                    'Everything in Team Workshop',
                    'Complete DevOps transformation roadmap',
                    'Full tech stack audit',
                    'Custom tool selection matrix',
                    'Integration planning',
                    'Cost optimization strategies',
                    'Security review',
                    'Performance benchmarking plan',
                    '50+ page detailed report',
                    '90 days email support',
                    'Quarterly follow-up calls'
                ],
                'sort_order': 5
            },
            {
                'name': 'Ongoing Retainer',
                'slug': 'retainer',
                'description': 'Monthly retainer for continuous DevOps guidance and support',
                'package_type': 'ongoing',
                'price': Decimal('1999.00'),
                'duration_hours': Decimal('10.0'),  # 10 hours
                'deliverables': [
                    '10 hours per month consulting time',
                    'Priority scheduling',
                    'Unlimited email support',
                    'Monthly strategy calls',
                    'Quarterly comprehensive reviews',
                    'Tool evaluation on demand',
                    'Architecture reviews',
                    'Emergency support available'
                ],
                'sort_order': 6
            }
        ]

        for package_data in packages:
            package, created = ConsultingPackage.objects.get_or_create(
                slug=package_data['slug'],
                defaults=package_data
            )
            if created:
                self.stdout.write(f'  ✓ Created package: {package.name}')
            else:
                self.stdout.write(f'  - Package already exists: {package.name}')
