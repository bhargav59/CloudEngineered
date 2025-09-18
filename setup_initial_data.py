#!/usr/bin/env python
"""Script to set up initial data for CloudEngineered platform."""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import Category, Tool
from apps.content.models import Article
from django.contrib.auth import get_user_model

User = get_user_model()

def create_initial_data():
    print("Creating initial data for CloudEngineered platform...")
    
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@cloudengineered.com',
            password='admin123'
        )
        print("Created admin user (username: admin, password: admin123)")
    else:
        admin_user = User.objects.get(username='admin')
        print("Admin user already exists")
    
    # Create categories
    categories_data = [
        {
            'name': 'CI/CD',
            'slug': 'ci-cd',
            'description': 'Continuous Integration and Continuous Deployment tools',
            'icon': 'fas fa-sync-alt',
            'color': '#4F46E5',
            'is_featured': True
        },
        {
            'name': 'Monitoring',
            'slug': 'monitoring',
            'description': 'Application and infrastructure monitoring tools',
            'icon': 'fas fa-chart-line',
            'color': '#059669',
            'is_featured': True
        },
        {
            'name': 'Security',
            'slug': 'security',
            'description': 'Security scanning and vulnerability management tools',
            'icon': 'fas fa-shield-alt',
            'color': '#DC2626',
            'is_featured': True
        },
        {
            'name': 'Cloud Platforms',
            'slug': 'cloud-platforms',
            'description': 'Cloud computing platforms and services',
            'icon': 'fas fa-cloud',
            'color': '#2563EB',
            'is_featured': True
        },
        {
            'name': 'Container Management',
            'slug': 'container-management',
            'description': 'Container orchestration and management tools',
            'icon': 'fab fa-docker',
            'color': '#7C3AED',
            'is_featured': True
        },
        {
            'name': 'Infrastructure as Code',
            'slug': 'infrastructure-as-code',
            'description': 'Tools for managing infrastructure through code',
            'icon': 'fas fa-code',
            'color': '#EA580C',
            'is_featured': True
        }
    ]
    
    print("Creating categories...")
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Category already exists: {category.name}")
    
    # Create some sample tools
    tools_data = [
        # CI/CD Tools
        {
            'name': 'GitHub Actions',
            'slug': 'github-actions',
            'category_slug': 'ci-cd',
            'description': 'GitHub\'s built-in CI/CD platform for automating workflows',
            'website_url': 'https://github.com/features/actions',
            'github_url': 'https://github.com/actions',
            'pricing_model': 'freemium',
            'deployment_types': ['cloud'],
            'tags': 'ci, cd, github, workflows, automation',
            'is_featured': True
        },
        {
            'name': 'Jenkins',
            'slug': 'jenkins',
            'category_slug': 'ci-cd',
            'description': 'Open source automation server for CI/CD pipelines',
            'website_url': 'https://www.jenkins.io/',
            'github_url': 'https://github.com/jenkinsci/jenkins',
            'pricing_model': 'free',
            'deployment_types': ['self_hosted'],
            'tags': 'ci, cd, automation, open source',
            'is_featured': True
        },
        # Monitoring Tools
        {
            'name': 'Prometheus',
            'slug': 'prometheus',
            'category_slug': 'monitoring',
            'description': 'Open-source monitoring and alerting toolkit',
            'website_url': 'https://prometheus.io/',
            'github_url': 'https://github.com/prometheus/prometheus',
            'pricing_model': 'free',
            'deployment_types': ['self_hosted'],
            'tags': 'monitoring, metrics, alerting, open source',
            'is_featured': True
        },
        {
            'name': 'Datadog',
            'slug': 'datadog',
            'category_slug': 'monitoring',
            'description': 'Cloud-based monitoring and analytics platform',
            'website_url': 'https://www.datadoghq.com/',
            'pricing_model': 'paid',
            'deployment_types': ['cloud'],
            'tags': 'monitoring, analytics, apm, logs',
            'is_featured': True
        },
        # Security Tools
        {
            'name': 'Snyk',
            'slug': 'snyk',
            'category_slug': 'security',
            'description': 'Developer security platform for finding and fixing vulnerabilities',
            'website_url': 'https://snyk.io/',
            'pricing_model': 'freemium',
            'deployment_types': ['cloud'],
            'tags': 'security, vulnerabilities, scanning, dependencies',
            'is_featured': True
        },
        # Cloud Platforms
        {
            'name': 'AWS',
            'slug': 'aws',
            'category_slug': 'cloud-platforms',
            'description': 'Amazon Web Services - comprehensive cloud computing platform',
            'website_url': 'https://aws.amazon.com/',
            'pricing_model': 'pay_per_use',
            'deployment_types': ['cloud'],
            'tags': 'cloud, aws, infrastructure, platform',
            'is_featured': True
        },
        # Container Management
        {
            'name': 'Kubernetes',
            'slug': 'kubernetes',
            'category_slug': 'container-management',
            'description': 'Open-source container orchestration platform',
            'website_url': 'https://kubernetes.io/',
            'github_url': 'https://github.com/kubernetes/kubernetes',
            'pricing_model': 'free',
            'deployment_types': ['self_hosted'],
            'tags': 'containers, orchestration, kubernetes, k8s',
            'is_featured': True
        },
        # Infrastructure as Code
        {
            'name': 'Terraform',
            'slug': 'terraform',
            'category_slug': 'infrastructure-as-code',
            'description': 'Infrastructure as code software tool by HashiCorp',
            'website_url': 'https://www.terraform.io/',
            'github_url': 'https://github.com/hashicorp/terraform',
            'pricing_model': 'freemium',
            'deployment_types': ['self_hosted'],
            'tags': 'iac, terraform, infrastructure, hashicorp',
            'is_featured': True
        }
    ]
    
    print("Creating tools...")
    for tool_data in tools_data:
        category = Category.objects.get(slug=tool_data['category_slug'])
        tool_data.pop('category_slug')  # Remove this as it's not a model field
        
        tool, created = Tool.objects.get_or_create(
            slug=tool_data['slug'],
            defaults={**tool_data, 'category': category}
        )
        if created:
            print(f"Created tool: {tool.name}")
        else:
            print(f"Tool already exists: {tool.name}")
    
    # Create sample articles
    articles_data = [
        {
            'title': 'Getting Started with GitHub Actions for CI/CD',
            'slug': 'getting-started-github-actions-ci-cd',
            'excerpt': 'Learn how to set up automated workflows using GitHub Actions for your projects.',
            'content': '''
# Getting Started with GitHub Actions for CI/CD

GitHub Actions provides a powerful platform for automating your software development workflows directly in your GitHub repository.

## What are GitHub Actions?

GitHub Actions are automated workflows that you can set up in your repository to build, test, package, release, or deploy any code project on GitHub.

## Basic Workflow Structure

A workflow is defined in a YAML file in your repository's `.github/workflows` directory:

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest
```

This workflow will run tests whenever code is pushed to the main branch or a pull request is created.
            ''',
            'article_type': 'guide',
            'author': admin_user,
            'is_featured': True
        },
        {
            'title': 'Comparing Monitoring Solutions: Prometheus vs Datadog',
            'slug': 'prometheus-vs-datadog-monitoring-comparison',
            'excerpt': 'A detailed comparison of two popular monitoring solutions for modern applications.',
            'content': '''
# Prometheus vs Datadog: Monitoring Solutions Compared

Choosing the right monitoring solution is crucial for maintaining reliable applications. Let's compare two popular options.

## Prometheus: Open Source Monitoring

**Pros:**
- Free and open source
- Powerful query language (PromQL)
- Large ecosystem of exporters
- Self-hosted for complete control

**Cons:**
- Requires more setup and maintenance
- Limited built-in visualization
- Storage scalability challenges

## Datadog: Cloud-Based Monitoring

**Pros:**
- Easy setup and configuration
- Rich visualization and dashboards
- Comprehensive feature set
- Excellent support

**Cons:**
- Can be expensive at scale
- Vendor lock-in
- Less customization flexibility

## Conclusion

Choose Prometheus if you need cost-effective, highly customizable monitoring and have the resources to manage it. Choose Datadog if you want a comprehensive, managed solution with minimal setup overhead.
            ''',
            'article_type': 'comparison',
            'author': admin_user,
            'is_featured': True
        }
    ]
    
    print("Creating articles...")
    for article_data in articles_data:
        article, created = Article.objects.get_or_create(
            slug=article_data['slug'],
            defaults=article_data
        )
        if created:
            print(f"Created article: {article.title}")
        else:
            print(f"Article already exists: {article.title}")
    
    print("\nInitial data creation completed!")
    print("\nYou can now:")
    print("1. Access the admin panel at /admin/ (username: admin, password: admin123)")
    print("2. Browse tools at /tools/")
    print("3. Read articles at /articles/")
    print("4. Start the development server with: python manage.py runserver")

if __name__ == '__main__':
    create_initial_data()
