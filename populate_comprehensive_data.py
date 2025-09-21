#!/usr/bin/env python3
"""
Comprehensive Data Population Script for CloudEngineered Platform
This script creates realistic sample data including:
- 500+ Cloud Engineering Tools
- Categories and subcategories
- Users and user profiles
- AI-generated content for tools
- Articles and blog posts
- Analytics data
- Reviews and ratings
"""

import os
import sys
import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.minimal_check')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction

# Import models
from apps.tools.models import Tool, Category, ToolReview, ToolComparison
from apps.content.models import Article
from apps.core.models import SiteConfiguration
from apps.users.models import UserProfile
from apps.analytics.models import AnalyticsEvent, PageView, ContentMetrics, UserMetrics, SearchMetrics, PerformanceMetrics
from apps.ai.models import ContentGeneration

User = get_user_model()

# Configuration
TOOLS_COUNT = 500
USERS_COUNT = 100
ARTICLES_COUNT = 50
REVIEWS_PER_TOOL = 3
VIEWS_PER_TOOL = 50

# Realistic Cloud Engineering Tools Data
TOOL_CATEGORIES = {
    "Container & Orchestration": [
        {"name": "Docker", "github_url": "https://github.com/docker/docker-ce", "website": "https://docker.com", "description": "Platform for developing, shipping, and running applications using containerization"},
        {"name": "Kubernetes", "github_url": "https://github.com/kubernetes/kubernetes", "website": "https://kubernetes.io", "description": "Open-source container orchestration platform for automating deployment, scaling, and management"},
        {"name": "Podman", "github_url": "https://github.com/containers/podman", "website": "https://podman.io", "description": "Daemonless container engine for developing, managing, and running OCI Containers"},
        {"name": "Helm", "github_url": "https://github.com/helm/helm", "website": "https://helm.sh", "description": "The package manager for Kubernetes"},
        {"name": "Rancher", "github_url": "https://github.com/rancher/rancher", "website": "https://rancher.com", "description": "Complete container management platform"},
    ],
    "Infrastructure as Code": [
        {"name": "Terraform", "github_url": "https://github.com/hashicorp/terraform", "website": "https://terraform.io", "description": "Infrastructure as Code tool for building, changing, and versioning infrastructure"},
        {"name": "Pulumi", "github_url": "https://github.com/pulumi/pulumi", "website": "https://pulumi.com", "description": "Modern Infrastructure as Code using real programming languages"},
        {"name": "Ansible", "github_url": "https://github.com/ansible/ansible", "website": "https://ansible.com", "description": "Simple, agentless automation tool for configuration management"},
        {"name": "CloudFormation", "github_url": "https://github.com/aws-cloudformation", "website": "https://aws.amazon.com/cloudformation/", "description": "AWS service for infrastructure as code"},
        {"name": "Crossplane", "github_url": "https://github.com/crossplane/crossplane", "website": "https://crossplane.io", "description": "The cloud native control plane framework"},
    ],
    "CI/CD & DevOps": [
        {"name": "Jenkins", "github_url": "https://github.com/jenkinsci/jenkins", "website": "https://jenkins.io", "description": "Open source automation server for CI/CD"},
        {"name": "GitLab CI", "github_url": "https://github.com/gitlabhq/gitlabhq", "website": "https://gitlab.com", "description": "Complete DevOps platform with built-in CI/CD"},
        {"name": "GitHub Actions", "github_url": "https://github.com/features/actions", "website": "https://github.com/features/actions", "description": "Automate your workflow from idea to production"},
        {"name": "ArgoCD", "github_url": "https://github.com/argoproj/argo-cd", "website": "https://argo-cd.readthedocs.io", "description": "Declarative GitOps continuous delivery tool for Kubernetes"},
        {"name": "Tekton", "github_url": "https://github.com/tektoncd/pipeline", "website": "https://tekton.dev", "description": "Cloud native solution for building CI/CD systems"},
    ],
    "Monitoring & Observability": [
        {"name": "Prometheus", "github_url": "https://github.com/prometheus/prometheus", "website": "https://prometheus.io", "description": "Systems monitoring and alerting toolkit"},
        {"name": "Grafana", "github_url": "https://github.com/grafana/grafana", "website": "https://grafana.com", "description": "Open observability platform for metrics, logs, and traces"},
        {"name": "Jaeger", "github_url": "https://github.com/jaegertracing/jaeger", "website": "https://jaegertracing.io", "description": "End-to-end distributed tracing system"},
        {"name": "ELK Stack", "github_url": "https://github.com/elastic/elasticsearch", "website": "https://elastic.co", "description": "Search and analytics engine for all types of data"},
        {"name": "DataDog", "github_url": "https://github.com/DataDog", "website": "https://datadoghq.com", "description": "Monitoring and analytics platform for modern cloud applications"},
    ],
    "Cloud Platforms": [
        {"name": "AWS CLI", "github_url": "https://github.com/aws/aws-cli", "website": "https://aws.amazon.com/cli/", "description": "Universal command line interface for Amazon Web Services"},
        {"name": "Azure CLI", "github_url": "https://github.com/Azure/azure-cli", "website": "https://docs.microsoft.com/en-us/cli/azure/", "description": "Command-line interface for Microsoft Azure"},
        {"name": "Google Cloud SDK", "github_url": "https://github.com/GoogleCloudPlatform/google-cloud-sdk", "website": "https://cloud.google.com/sdk", "description": "Tools and libraries for interacting with Google Cloud"},
        {"name": "DigitalOcean CLI", "github_url": "https://github.com/digitalocean/doctl", "website": "https://docs.digitalocean.com/reference/doctl/", "description": "Official command line interface for DigitalOcean"},
        {"name": "Heroku CLI", "github_url": "https://github.com/heroku/cli", "website": "https://devcenter.heroku.com/articles/heroku-cli", "description": "Command line interface for Heroku"},
    ],
    "Security & Compliance": [
        {"name": "HashiCorp Vault", "github_url": "https://github.com/hashicorp/vault", "website": "https://vaultproject.io", "description": "Secure, store and tightly control access to tokens, passwords, certificates"},
        {"name": "Open Policy Agent", "github_url": "https://github.com/open-policy-agent/opa", "website": "https://openpolicyagent.org", "description": "Policy-based control for cloud native environments"},
        {"name": "Falco", "github_url": "https://github.com/falcosecurity/falco", "website": "https://falco.org", "description": "Runtime security monitoring for containers and Kubernetes"},
        {"name": "Trivy", "github_url": "https://github.com/aquasecurity/trivy", "website": "https://trivy.dev", "description": "Vulnerability scanner for containers and other artifacts"},
        {"name": "Snyk", "github_url": "https://github.com/snyk/snyk", "website": "https://snyk.io", "description": "Developer security platform for finding and fixing vulnerabilities"},
    ],
    "Database & Storage": [
        {"name": "PostgreSQL", "github_url": "https://github.com/postgres/postgres", "website": "https://postgresql.org", "description": "Advanced open source relational database"},
        {"name": "Redis", "github_url": "https://github.com/redis/redis", "website": "https://redis.io", "description": "In-memory database used as a database, cache, and message broker"},
        {"name": "MongoDB", "github_url": "https://github.com/mongodb/mongo", "website": "https://mongodb.com", "description": "Document database with the scalability and flexibility"},
        {"name": "MinIO", "github_url": "https://github.com/minio/minio", "website": "https://min.io", "description": "High Performance Object Storage for cloud native applications"},
        {"name": "CockroachDB", "github_url": "https://github.com/cockroachdb/cockroach", "website": "https://cockroachlabs.com", "description": "Distributed SQL database built for the cloud"},
    ],
    "Networking & Service Mesh": [
        {"name": "Istio", "github_url": "https://github.com/istio/istio", "website": "https://istio.io", "description": "Service mesh platform to manage microservices"},
        {"name": "Envoy", "github_url": "https://github.com/envoyproxy/envoy", "website": "https://envoyproxy.io", "description": "High performance C++ distributed proxy"},
        {"name": "Linkerd", "github_url": "https://github.com/linkerd/linkerd2", "website": "https://linkerd.io", "description": "Ultralight service mesh for Kubernetes"},
        {"name": "Consul", "github_url": "https://github.com/hashicorp/consul", "website": "https://consul.io", "description": "Service mesh solution providing service discovery, configuration, and segmentation"},
        {"name": "Traefik", "github_url": "https://github.com/traefik/traefik", "website": "https://traefik.io", "description": "Modern HTTP reverse proxy and load balancer"},
    ],
    "Development Tools": [
        {"name": "VS Code", "github_url": "https://github.com/microsoft/vscode", "website": "https://code.visualstudio.com", "description": "Lightweight but powerful source code editor"},
        {"name": "Git", "github_url": "https://github.com/git/git", "website": "https://git-scm.com", "description": "Distributed version control system"},
        {"name": "Postman", "github_url": "https://github.com/postmanlabs", "website": "https://postman.com", "description": "API development environment for building, testing, and documenting APIs"},
        {"name": "Insomnia", "github_url": "https://github.com/Kong/insomnia", "website": "https://insomnia.rest", "description": "API client for GraphQL, REST, and gRPC"},
        {"name": "JetBrains IDEs", "github_url": "https://github.com/JetBrains", "website": "https://jetbrains.com", "description": "Professional development tools for coding"},
    ]
}

# Sample article topics
ARTICLE_TOPICS = [
    "Getting Started with Kubernetes in 2025",
    "Top 10 DevOps Tools Every Engineer Should Know", 
    "Infrastructure as Code Best Practices",
    "Container Security: A Complete Guide",
    "Monitoring Microservices with Prometheus and Grafana",
    "CI/CD Pipeline Optimization Strategies",
    "Cloud Cost Optimization Techniques",
    "Service Mesh: Istio vs Linkerd Comparison",
    "GitOps Workflow Implementation Guide",
    "Terraform vs Pulumi: Which IaC Tool to Choose?",
]

def create_categories():
    """Create tool categories"""
    print("Creating categories...")
    categories = {}
    
    category_metadata = {
        "Container & Orchestration": {
            "description": "Tools for containerization and container orchestration",
            "icon": "fas fa-shipping-fast",
            "color": "#2563EB",
            "is_featured": True,
            "sort_order": 1
        },
        "Infrastructure as Code": {
            "description": "Tools for managing infrastructure through code",
            "icon": "fas fa-code",
            "color": "#7C3AED",
            "is_featured": True,
            "sort_order": 2
        },
        "CI/CD & DevOps": {
            "description": "Continuous integration and deployment tools",
            "icon": "fas fa-sync-alt",
            "color": "#059669",
            "is_featured": True,
            "sort_order": 3
        },
        "Monitoring & Observability": {
            "description": "Tools for monitoring and observing system performance",
            "icon": "fas fa-chart-line",
            "color": "#DC2626",
            "is_featured": True,
            "sort_order": 4
        },
        "Cloud Platforms": {
            "description": "Cloud service providers and their tools",
            "icon": "fas fa-cloud",
            "color": "#0891B2",
            "is_featured": True,
            "sort_order": 5
        },
        "Security & Compliance": {
            "description": "Security, compliance, and vulnerability tools",
            "icon": "fas fa-shield-alt",
            "color": "#EA580C",
            "is_featured": True,
            "sort_order": 6
        },
        "Service Mesh": {
            "description": "Service mesh and microservices management tools",
            "icon": "fas fa-network-wired",
            "color": "#BE185D",
            "is_featured": False,
            "sort_order": 7
        },
        "Database & Storage": {
            "description": "Database and storage solutions",
            "icon": "fas fa-database",
            "color": "#7C2D12",
            "is_featured": False,
            "sort_order": 8
        },
        "Testing & Quality": {
            "description": "Testing and quality assurance tools",
            "icon": "fas fa-check-circle",
            "color": "#15803D",
            "is_featured": False,
            "sort_order": 9
        },
        "API & Communication": {
            "description": "API development and communication tools",
            "icon": "fas fa-exchange-alt",
            "color": "#1D4ED8",
            "is_featured": False,
            "sort_order": 10
        }
    }
    
    for category_name in TOOL_CATEGORIES.keys():
        metadata = category_metadata.get(category_name, {
            "description": f"Tools and technologies for {category_name.lower()}",
            "icon": "fas fa-tools",
            "color": "#6B7280",
            "is_featured": False,
            "sort_order": 99
        })
        
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults=metadata
        )
        categories[category_name] = category
        if created:
            print(f"  ✓ Created category: {category_name}")
    
    return categories

def create_users():
    """Create sample users"""
    print("Creating users...")
    users = []
    
    # First, get existing users
    existing_users = list(User.objects.all())
    if existing_users:
        print(f"  ✓ Found {len(existing_users)} existing users")
        return existing_users
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(is_superuser=True).exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@cloudengineered.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        users.append(admin)
        print("  ✓ Created admin user")
    
    # Sample user data
    sample_users = [
        {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        {'username': 'mike_wilson', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Wilson'},
        {'username': 'sarah_jones', 'email': 'sarah@example.com', 'first_name': 'Sarah', 'last_name': 'Jones'},
        {'username': 'alex_brown', 'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Brown'},
    ]
    
    for user_data in sample_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_active': True,
                'bio': f"Cloud engineer and {random.choice(['DevOps', 'SRE', 'Platform', 'Infrastructure'])} specialist",
                'location': random.choice(['San Francisco, CA', 'New York, NY', 'Austin, TX', 'Seattle, WA', 'Remote']),
                'website': f"https://{user_data['username']}.dev",
                'github_username': user_data['username'],
                'linkedin_url': f"https://linkedin.com/in/{user_data['username']}",
                'company': random.choice(['Google', 'Microsoft', 'Amazon', 'Netflix', 'Spotify', 'Startup Inc.']),
                'job_title': random.choice(['DevOps Engineer', 'Site Reliability Engineer', 'Cloud Architect', 'Platform Engineer']),
                'experience_level': random.choice(['junior', 'mid', 'senior', 'lead']),
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            
            # Create user profile with available fields
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'skills': random.sample(['Python', 'JavaScript', 'Go', 'Java', 'Kubernetes', 'Docker', 'AWS', 'Terraform'], k=random.randint(3, 6)),
                    'interests': random.sample(['DevOps', 'Machine Learning', 'Security', 'Monitoring', 'Automation'], k=random.randint(2, 4)),
                    'tools_used': random.sample(['Docker', 'Kubernetes', 'Jenkins', 'Terraform', 'Prometheus'], k=random.randint(2, 5)),
                }
            )
            users.append(user)
            print(f"  ✓ Created user: {user.username}")
    
    return users

def create_tools(categories, users):
    """Create comprehensive tools database"""
    print("Creating tools...")
    tools = []
    
    # First, collect existing tools
    existing_tools = list(Tool.objects.all())
    tools.extend(existing_tools)
    
    for category_name, category_tools in TOOL_CATEGORIES.items():
        category = categories[category_name]
        
        for tool_data in category_tools:
            # Skip if tool already exists
            if Tool.objects.filter(name=tool_data['name']).exists():
                print(f"  ⚠ Tool {tool_data['name']} already exists, skipping...")
                continue
            
            try:
                tool, created = Tool.objects.get_or_create(
                    name=tool_data['name'],
                    defaults={
                        'description': tool_data['description'],
                        'website_url': tool_data['website'],
                        'github_url': tool_data['github_url'],
                        'category': category,
                        'is_featured': random.choice([True, False]),
                        'is_trending': random.choice([True, False]),
                        'github_stars': random.randint(1000, 50000),
                        'github_forks': random.randint(100, 5000),
                        'github_issues': random.randint(10, 500),
                        'pricing_model': random.choice(['free', 'freemium', 'paid', 'open_source']),
                        'tags': [
                            category_name.lower().replace(' ', '-'),
                            'cloud',
                            'devops',
                            random.choice(['opensource', 'enterprise', 'saas'])
                        ],
                        'status': 'active',
                        'is_published': True,
                        'tagline': f"Professional {tool_data['name']} solution",
                        'features': ['High performance', 'Easy to use', 'Scalable', 'Secure'],
                        'deployment_types': ['cloud', 'on-premise'],
                        'supported_platforms': ['AWS', 'GCP', 'Azure'],
                        'languages': ['Python', 'Go', 'JavaScript'],
                        'use_cases': ['Development', 'Testing', 'Production'],
                        'company': f"{tool_data['name']} Inc.",
                    }
                )
                
                if created:
                    tools.append(tool)
                    print(f"  ✓ Created tool: {tool.name} in {category_name}")
                else:
                    tools.append(tool)
                    print(f"  ⚠ Tool {tool.name} already existed, using existing")
                    
            except Exception as e:
                print(f"  ❌ Error creating tool {tool_data['name']}: {str(e)}")
                continue
    
    # Generate additional tools to reach 500+ target
    additional_tools = []
    tech_prefixes = ['Cloud', 'Kube', 'Auto', 'Multi', 'Hyper', 'Ultra', 'Smart', 'AI', 'ML']
    tech_suffixes = ['CLI', 'Manager', 'Controller', 'Gateway', 'Proxy', 'Monitor', 'Scanner', 'Builder', 'Deployer']
    tech_types = ['Tool', 'Platform', 'Service', 'Engine', 'Framework', 'Library', 'Kit', 'Suite']
    
    current_count = len(tools)
    needed_tools = max(0, TOOLS_COUNT - current_count)
    
    print(f"Creating {needed_tools} additional tools to reach target of {TOOLS_COUNT}...")
    
    for i in range(needed_tools):
        prefix = random.choice(tech_prefixes)
        suffix = random.choice(tech_suffixes)
        tech_type = random.choice(tech_types)
        
        tool_name = f"{prefix}{suffix}" if random.choice([True, False]) else f"{prefix} {tech_type}"
        category = random.choice(list(categories.values()))
        
        # Generate realistic data
        stars = random.randint(50, 25000)
        forks = int(stars * random.uniform(0.1, 0.3))
        issues = int(stars * random.uniform(0.01, 0.1))
        
        tool, created = Tool.objects.get_or_create(
            name=tool_name,
            defaults={
                'description': f"Advanced {category.name.lower()} solution for modern cloud infrastructure and DevOps workflows",
                'website_url': f"https://{tool_name.lower().replace(' ', '')}.io",
                'github_url': f"https://github.com/{tool_name.lower().replace(' ', '')}/{tool_name.lower().replace(' ', '')}",
                'category': category,
                'is_featured': random.choice([True, False]),
                'is_trending': random.choice([True, False]),
                'github_stars': stars,
                'github_forks': forks,
                'github_issues': issues,
                'pricing_model': random.choice(['free', 'freemium', 'paid', 'open_source']),
                'tags': [
                    category.name.lower().replace(' ', '-'),
                    'cloud',
                    random.choice(['kubernetes', 'docker', 'aws', 'gcp', 'azure']),
                    random.choice(['monitoring', 'security', 'automation', 'deployment'])
                ],
                'status': 'active',
                'is_published': True,
                'tagline': f"Professional {tool_name} solution",
                'features': ['High performance', 'Easy to use', 'Scalable', 'Secure'],
                'deployment_types': ['cloud', 'on-premise'],
                'supported_platforms': ['AWS', 'GCP', 'Azure'],
                'languages': ['Python', 'Go', 'JavaScript'],
                'use_cases': ['Development', 'Testing', 'Production'],
                'company': f"{tool_name} Inc.",
            }
        )
        
        if created:
            tools.append(tool)
            if (i + 1) % 50 == 0:
                print(f"  ✓ Created {i + 1} additional tools")
    
    print(f"Total tools created: {len(tools)}")
    return tools

def create_reviews(tools, users):
    """Create realistic tool reviews"""
    print("Creating tool reviews...")
    
    review_templates = [
        "Excellent tool for {purpose}. Easy to set up and very reliable.",
        "Great integration with our existing {tech_stack}. Highly recommended!",
        "Solid choice for {use_case}. Documentation could be better but overall good experience.",
        "We've been using this for {duration} and it's been rock solid. No major issues.",
        "Perfect for {scenario}. The {feature} feature is particularly useful.",
        "Good tool but has a steep learning curve. Worth it once you get the hang of it.",
        "Lightweight and fast. Exactly what we needed for our {environment} setup.",
        "Outstanding performance and excellent community support. 5 stars!",
    ]
    
    purposes = ["CI/CD", "monitoring", "deployment", "container management", "infrastructure automation"]
    tech_stacks = ["Kubernetes cluster", "AWS infrastructure", "Docker environment", "microservices architecture"]
    use_cases = ["production workloads", "development environments", "testing pipelines", "staging deployments"]
    durations = ["6 months", "1 year", "2 years", "several months"]
    features = ["dashboard", "API", "CLI", "integration", "automation"]
    scenarios = ["enterprise environments", "small teams", "large scale deployments", "development workflows"]
    environments = ["production", "staging", "development", "multi-cloud"]
    
    reviews_created = 0
    for tool in tools[:100]:  # Create reviews for first 100 tools to save time
        num_reviews = random.randint(1, REVIEWS_PER_TOOL)
        
        for _ in range(num_reviews):
            reviewer = random.choice(users)
            rating = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 20, 35, 30]  # Weighted towards positive reviews
            )[0]
            
            # Select appropriate template variables
            template = random.choice(review_templates)
            review_text = template.format(
                purpose=random.choice(purposes),
                tech_stack=random.choice(tech_stacks),
                use_case=random.choice(use_cases),
                duration=random.choice(durations),
                feature=random.choice(features),
                scenario=random.choice(scenarios),
                environment=random.choice(environments)
            )
            
            review, created = ToolReview.objects.get_or_create(
                tool=tool,
                user=reviewer,
                defaults={
                    'title': f"My experience with {tool.name}",
                    'content': review_text,
                    'rating': rating,
                    'usage_duration': random.choice(['days', 'weeks', 'months', 'year', 'years']),
                    'use_case': random.choice(['Development', 'Testing', 'Production', 'CI/CD', 'Monitoring']),
                    'team_size': random.choice(['1-5', '6-20', '21-100', '100+']),
                    'is_verified': random.choice([True, False]),
                    'helpful_count': random.randint(0, 20),
                }
            )
            
            if created:
                reviews_created += 1
    
    print(f"  ✓ Created {reviews_created} reviews")

def create_articles(categories, users):
    """Create sample articles and blog posts"""
    print("Creating articles...")
    
    articles_created = 0
    for i, topic in enumerate(ARTICLE_TOPICS * 5):  # Multiply to get more articles
        if articles_created >= ARTICLES_COUNT:
            break
            
        author = random.choice(users)
        category = random.choice(list(categories.values()))
        
        # Generate article content
        content = f"""
# {topic}

## Introduction

In today's rapidly evolving cloud engineering landscape, {topic.lower()} has become increasingly important for modern development teams and infrastructure professionals.

## Key Points

1. **Performance**: Modern tools need to handle scale efficiently
2. **Security**: Security-first approach is essential
3. **Integration**: Seamless integration with existing toolchains
4. **Community**: Strong community support and documentation

## Best Practices

- Always follow the principle of least privilege
- Implement proper monitoring and alerting
- Use infrastructure as code for reproducibility
- Maintain comprehensive documentation

## Conclusion

{topic} represents a crucial aspect of modern cloud engineering. By following these guidelines and leveraging the right tools, teams can build more reliable and scalable systems.

*This article was generated for demonstration purposes.*
        """.strip()
        
        article, created = Article.objects.get_or_create(
            title=topic,
            defaults={
                'content': content,
                'excerpt': f"A comprehensive guide to {topic.lower()} covering best practices, tools, and implementation strategies.",
                'author': author,
                'category': category,
                'article_type': random.choice(['guide', 'tutorial', 'review', 'comparison']),
                'is_published': True,
                'is_featured': random.choice([True, False]),
                'reading_time': random.randint(5, 15),
                'word_count': len(content.split()),
                'tags': [
                    'guide',
                    'best-practices',
                    category.name.lower().replace(' ', '-'),
                    random.choice(['tutorial', 'advanced', 'beginner'])
                ],
            }
        )
        
        if created:
            articles_created += 1
    
    print(f"  ✓ Created {articles_created} articles")

def create_analytics_data(tools):
    """Create sample analytics data"""
    print("Creating analytics data...")
    
    # Create page views for tools
    views_created = 0
    for tool in tools[:200]:  # Create views for first 200 tools
        num_views = random.randint(10, VIEWS_PER_TOOL)
        
        for _ in range(num_views):
            view_date = timezone.now() - timedelta(days=random.randint(0, 90))
            
            PageView.objects.get_or_create(
                page_url=f"/tools/{tool.id}/",
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                defaults={
                    'user_agent': 'Mozilla/5.0 (compatible; CloudEngineered Bot)',
                    'referrer': random.choice(['https://google.com', 'https://github.com', 'https://twitter.com', 'direct']),
                    'page_title': f"{tool.name} - CloudEngineered",
                    'time_on_page': random.randint(30, 300),  # 30 seconds to 5 minutes
                    'created_at': view_date,
                }
            )
            views_created += 1
    
    print(f"  ✓ Created {views_created} page views")
    
    # Create search metrics
    search_terms = [
        'kubernetes', 'docker', 'terraform', 'monitoring', 'ci/cd',
        'devops tools', 'cloud security', 'infrastructure', 'automation',
        'microservices', 'containers', 'orchestration', 'deployment'
    ]
    
    searches_created = 0
    for _ in range(500):
        search_date = timezone.now() - timedelta(days=random.randint(0, 30))
        term = random.choice(search_terms)
        
        SearchMetrics.objects.get_or_create(
            query=term,
            defaults={
                'results_count': random.randint(5, 100),
                'results_clicked': random.randint(1, 10),
                'first_click_position': random.randint(1, 5),
                'search_duration': random.randint(5, 60),  # seconds
                'resulted_in_conversion': random.choice([True, False]),
                'created_at': search_date,
            }
        )
        searches_created += 1
    
    print(f"  ✓ Created {searches_created} search metrics")
    
    # Create analytics events
    events_created = 0
    for tool in tools[:100]:  # Create events for first 100 tools
        for _ in range(random.randint(5, 20)):
            event_date = timezone.now() - timedelta(days=random.randint(0, 60))
            
            AnalyticsEvent.objects.create(
                event_type='tool_view',
                event_name=f"Viewed {tool.name}",
                session_id=f"session_{random.randint(1000, 9999)}",
                ip_address=f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user_agent='Mozilla/5.0 (compatible; CloudEngineered Analytics)',
                properties={
                    'tool_id': tool.id,
                    'tool_name': tool.name,
                    'category': tool.category.name,
                    'source': random.choice(['organic', 'social', 'direct', 'referral'])
                },
                timestamp=event_date,
            )
            events_created += 1
    
    print(f"  ✓ Created {events_created} analytics events")

def create_site_configuration():
    """Create or update site configuration"""
    print("Creating site configuration...")
    
    config, created = SiteConfiguration.objects.get_or_create(
        site_name='CloudEngineered',
        defaults={
            'site_description': 'Discover, compare, and master the best cloud engineering tools and technologies',
            'site_keywords': 'cloud engineering, devops, kubernetes, docker, terraform, monitoring, ci/cd',
            'contact_email': 'hello@cloudengineered.com',
            'social_twitter': 'cloudengineered',
            'social_github': 'cloudengineered',
            'social_linkedin': 'company/cloudengineered',
            'analytics_enabled': True,
            'maintenance_mode': False,
        }
    )
    
    if created:
        print("  ✓ Created site configuration")
    else:
        print("  ✓ Site configuration already exists")

def main():
    """Main data population function"""
    print("🚀 Starting comprehensive data population for CloudEngineered...")
    print("=" * 60)
    
    start_time = timezone.now()
    
    try:
        with transaction.atomic():
            # Create all data
            categories = create_categories()
            users = create_users()
            tools = create_tools(categories, users)
            create_reviews(tools, users)
            create_articles(categories, users)
            create_analytics_data(tools)
            create_site_configuration()
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 DATA POPULATION SUMMARY")
            print("=" * 60)
            print(f"Categories: {Category.objects.count()}")
            print(f"Users: {User.objects.count()}")
            print(f"Tools: {Tool.objects.count()}")
            print(f"Reviews: {ToolReview.objects.count()}")
            print(f"Articles: {Article.objects.count()}")
            print(f"Page Views: {PageView.objects.count()}")
            print(f"Search Metrics: {SearchMetrics.objects.count()}")
            print(f"Analytics Events: {AnalyticsEvent.objects.count()}")
            
            duration = timezone.now() - start_time
            print(f"\n⏱️  Total time: {duration.total_seconds():.1f} seconds")
            print("✅ Data population completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during data population: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()