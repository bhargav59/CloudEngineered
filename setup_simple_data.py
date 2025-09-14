#!/usr/bin/env python
"""Simple script to set up initial data for CloudEngineered platform."""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.minimal')
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
            'color': '#0891B2',
            'is_featured': True
        },
        {
            'name': 'Container Management',
            'slug': 'container-management',
            'description': 'Container orchestration and management tools',
            'icon': 'fab fa-docker',
            'color': '#7C3AED',
            'is_featured': False
        },
        {
            'name': 'Infrastructure as Code',
            'slug': 'infrastructure-as-code',
            'description': 'Infrastructure automation and provisioning tools',
            'icon': 'fas fa-code',
            'color': '#EA580C',
            'is_featured': False
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
    
    # Create sample tools
    tools_data = [
        # CI/CD Tools
        {
            'name': 'GitHub Actions',
            'slug': 'github-actions',
            'category_slug': 'ci-cd',
            'description': 'GitHub\'s built-in CI/CD platform for automating workflows',
            'website_url': 'https://github.com/features/actions',
            'pricing_model': 'freemium',
            'deployment_types': ['cloud'],
            'tags': ['ci', 'cd', 'github', 'automation'],
            'is_featured': True,
            'is_published': True,
        },
        {
            'name': 'Jenkins',
            'slug': 'jenkins',
            'category_slug': 'ci-cd',
            'description': 'Open-source automation server for CI/CD',
            'website_url': 'https://www.jenkins.io/',
            'github_url': 'https://github.com/jenkinsci/jenkins',
            'pricing_model': 'free',
            'deployment_types': ['self_hosted', 'cloud'],
            'tags': ['ci', 'cd', 'automation', 'open-source'],
            'is_featured': True,
            'is_published': True,
        },
        # Monitoring
        {
            'name': 'Prometheus',
            'slug': 'prometheus',
            'category_slug': 'monitoring',
            'description': 'Open-source monitoring and alerting toolkit',
            'website_url': 'https://prometheus.io/',
            'github_url': 'https://github.com/prometheus/prometheus',
            'pricing_model': 'free',
            'deployment_types': ['self_hosted'],
            'tags': ['monitoring', 'metrics', 'alerting', 'time-series'],
            'is_featured': True,
            'is_published': True,
        },
        {
            'name': 'Grafana',
            'slug': 'grafana',
            'category_slug': 'monitoring',
            'description': 'Open-source analytics and monitoring platform',
            'website_url': 'https://grafana.com/',
            'github_url': 'https://github.com/grafana/grafana',
            'pricing_model': 'freemium',
            'deployment_types': ['cloud', 'self_hosted'],
            'tags': ['monitoring', 'dashboards', 'visualization', 'analytics'],
            'is_featured': True,
            'is_published': True,
        },
        # Security
        {
            'name': 'Snyk',
            'slug': 'snyk',
            'category_slug': 'security',
            'description': 'Developer security platform for finding and fixing vulnerabilities',
            'website_url': 'https://snyk.io/',
            'pricing_model': 'freemium',
            'deployment_types': ['cloud'],
            'tags': ['security', 'vulnerabilities', 'scanning', 'dependencies'],
            'is_featured': True,
            'is_published': True,
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
            'tags': ['cloud', 'aws', 'infrastructure', 'platform'],
            'is_featured': True,
            'is_published': True,
        },
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
            'content': '''# Getting Started with GitHub Actions for CI/CD

GitHub Actions is a powerful CI/CD platform that allows you to automate your development workflows directly in your GitHub repository. In this guide, we'll explore the basics and help you get started.

## What are GitHub Actions?

GitHub Actions makes it easy to automate all your software workflows, now with world-class CI/CD. Build, test, and deploy your code right from GitHub. Make code reviews, branch management, and issue triaging work the way you want.

## Basic Workflow

Here's a simple example of a GitHub Actions workflow:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run tests
      run: npm test
```

This workflow will run tests on every push and pull request to your repository.
''',
            'article_type': 'guide',
            'author': admin_user,
            'is_published': True,
            'is_featured': True,
        },
        {
            'title': 'Monitoring Best Practices with Prometheus and Grafana',
            'slug': 'monitoring-best-practices-prometheus-grafana',
            'excerpt': 'Discover how to implement effective monitoring using Prometheus for metrics collection and Grafana for visualization.',
            'content': '''# Monitoring Best Practices with Prometheus and Grafana

Effective monitoring is crucial for maintaining reliable applications. This guide covers best practices using Prometheus and Grafana.

## Why Prometheus and Grafana?

- **Prometheus**: Excellent for metrics collection and alerting
- **Grafana**: Powerful visualization and dashboard creation
- **Integration**: They work seamlessly together

## Getting Started

1. Install Prometheus
2. Configure metrics collection
3. Set up Grafana dashboards
4. Create alerting rules

## Key Metrics to Monitor

- Application performance metrics
- Infrastructure health
- Business metrics
- Error rates and response times
''',
            'article_type': 'guide',
            'author': admin_user,
            'is_published': True,
            'is_featured': False,
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
    
    print("Initial data setup completed successfully!")
    print(f"Created {Category.objects.count()} categories")
    print(f"Created {Tool.objects.count()} tools")
    print(f"Created {Article.objects.count()} articles")
    print(f"Total users: {User.objects.count()}")
    
    print("\n🎉 CloudEngineered platform is ready!")
    print("Admin credentials: admin@cloudengineered.com / admin123")
    print("You can now run the development server: python manage.py runserver")

if __name__ == '__main__':
    create_initial_data()