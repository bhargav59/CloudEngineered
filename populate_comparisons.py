#!/usr/bin/env python
"""
Script to populate tool comparison data for CloudEngineered platform.
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.minimal_check')
django.setup()

from apps.tools.models import Tool, ToolComparison, Category
from apps.users.models import User

def create_comparison_data():
    """Create realistic tool comparison data"""
    print("Creating tool comparisons...")
    
    # Get some users for authoring
    users = list(User.objects.all())
    if not users:
        print("No users found. Please create users first.")
        return
    
    # Get tools by category for comparisons
    tools_by_category = {}
    for category in Category.objects.all():
        category_tools = list(Tool.objects.filter(category=category, is_published=True))
        if len(category_tools) >= 2:
            tools_by_category[category] = category_tools
    
    if not tools_by_category:
        print("Not enough tools found for comparisons.")
        return
    
    comparisons_data = [
        {
            'category': 'Container & Orchestration',
            'title': 'Docker vs Podman: Container Runtime Comparison',
            'tools': ['Docker', 'Podman'],
            'description': 'A comprehensive comparison between Docker and Podman, two popular container runtimes.',
            'introduction': '''Docker and Podman are both container runtimes that allow you to build, run, and manage containers. 
While Docker has been the industry standard for years, Podman has emerged as a compelling alternative with some unique advantages.
This comparison will help you understand the key differences and choose the right tool for your needs.''',
            'conclusion': '''Both Docker and Podman are excellent container runtimes with their own strengths. 
Docker offers better ecosystem support and documentation, while Podman provides better security and rootless operation.''',
            'recommendation': '''For beginners and teams already using Docker, stick with Docker for its ecosystem and community support.
For security-conscious environments or rootless containers, consider Podman as a more secure alternative.'''
        },
        {
            'category': 'CI/CD & DevOps',
            'title': 'Jenkins vs GitLab CI: Which CI/CD Tool is Right for You?',
            'tools': ['Jenkins', 'GitLab CI'],
            'description': 'Compare Jenkins and GitLab CI to find the best continuous integration solution for your team.',
            'introduction': '''Continuous Integration and Continuous Deployment (CI/CD) are crucial for modern software development.
Jenkins and GitLab CI are two popular solutions, each with distinct approaches to automation and deployment pipelines.''',
            'conclusion': '''Jenkins offers more flexibility and plugins, while GitLab CI provides better integration with Git workflows.''',
            'recommendation': '''Choose GitLab CI if you\'re already using GitLab or want an integrated solution. 
Choose Jenkins if you need maximum flexibility and have complex automation requirements.'''
        },
        {
            'category': 'Infrastructure as Code',
            'title': 'Terraform vs Pulumi: Infrastructure as Code Showdown',
            'tools': ['Terraform', 'Pulumi'],
            'description': 'Detailed comparison between Terraform and Pulumi for infrastructure as code implementations.',
            'introduction': '''Infrastructure as Code (IaC) has revolutionized how we manage cloud infrastructure.
Terraform and Pulumi are leading solutions, each offering different approaches to defining and managing infrastructure.''',
            'conclusion': '''Terraform has broader provider support and a larger community, while Pulumi offers familiar programming languages.''',
            'recommendation': '''Choose Terraform for multi-cloud deployments and established workflows.
Choose Pulumi if your team prefers general-purpose programming languages over DSLs.'''
        },
        {
            'category': 'Monitoring & Observability',
            'title': 'Prometheus vs DataDog: Monitoring Solution Comparison',
            'tools': ['Prometheus', 'DataDog'],
            'description': 'Compare open-source Prometheus with commercial DataDog for monitoring and observability needs.',
            'introduction': '''Effective monitoring is essential for maintaining reliable systems.
Prometheus and DataDog represent two different approaches: open-source vs commercial solutions.''',
            'conclusion': '''Prometheus offers flexibility and cost-effectiveness, while DataDog provides comprehensive features and ease of use.''',
            'recommendation': '''Choose Prometheus for cost-conscious teams with Kubernetes environments.
Choose DataDog for comprehensive monitoring with minimal setup and maintenance.'''
        },
        {
            'category': 'Cloud Platforms',
            'title': 'AWS CLI vs Azure CLI: Command-Line Tool Comparison',
            'tools': ['AWS CLI', 'Azure CLI'],
            'description': 'Compare the command-line interfaces for AWS and Azure cloud platforms.',
            'introduction': '''Command-line interfaces are essential tools for cloud engineers managing infrastructure programmatically.
Both AWS CLI and Azure CLI offer powerful capabilities for their respective platforms.''',
            'conclusion': '''Both CLIs are well-designed for their platforms with similar capabilities and approaches.''',
            'recommendation': '''Your choice depends primarily on which cloud platform you\'re using. 
Both tools are excellent for their respective ecosystems.'''
        }
    ]
    
    created_count = 0
    for comp_data in comparisons_data:
        # Find the category
        try:
            category = Category.objects.get(name=comp_data['category'])
        except Category.DoesNotExist:
            print(f"Category '{comp_data['category']}' not found, skipping...")
            continue
        
        # Find the tools
        tools = []
        for tool_name in comp_data['tools']:
            try:
                tool = Tool.objects.get(name=tool_name, category=category)
                tools.append(tool)
            except Tool.DoesNotExist:
                print(f"Tool '{tool_name}' not found in category '{category.name}', trying to find any tool with that name...")
                try:
                    tool = Tool.objects.get(name=tool_name)
                    tools.append(tool)
                except Tool.DoesNotExist:
                    print(f"Tool '{tool_name}' not found anywhere, skipping...")
        
        if len(tools) < 2:
            print(f"Not enough tools found for comparison '{comp_data['title']}', skipping...")
            continue
        
        # Create the comparison
        try:
            comparison, created = ToolComparison.objects.get_or_create(
                title=comp_data['title'],
                defaults={
                    'description': comp_data['description'],
                    'introduction': comp_data['introduction'],
                    'conclusion': comp_data['conclusion'],
                    'recommendation': comp_data['recommendation'],
                    'author': random.choice(users),
                    'is_published': True,
                    'view_count': random.randint(100, 2000),
                    'criteria': [
                        'Ease of Use',
                        'Performance',
                        'Community Support',
                        'Documentation',
                        'Cost',
                        'Security Features'
                    ]
                }
            )
            
            if created:
                # Add the tools to the comparison
                comparison.tools.set(tools)
                created_count += 1
                print(f"  ✓ Created comparison: {comp_data['title']}")
            else:
                print(f"  ⚠ Comparison already exists: {comp_data['title']}")
                
        except Exception as e:
            print(f"  ❌ Error creating comparison '{comp_data['title']}': {str(e)}")
    
    print(f"\nCreated {created_count} new comparisons")
    
    # Display summary
    total_comparisons = ToolComparison.objects.filter(is_published=True).count()
    print(f"Total published comparisons: {total_comparisons}")

if __name__ == '__main__':
    create_comparison_data()