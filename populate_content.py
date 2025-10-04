"""
Populate CloudEngineered platform with tools and content using Gemini AI
This script creates realistic data so no pages are empty
"""

import os
import django
import sys
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.tools.models import Tool, Category
from apps.content.models import Article
from apps.ai.gemini_service import get_gemini_service
from django.contrib.auth import get_user_model

User = get_user_model()

# Initialize Gemini service
gemini = get_gemini_service()

def create_superuser():
    """Create superuser if doesn't exist"""
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        print("Creating superuser...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@cloudengineered.com',
            password='admin123',
            first_name='Cloud',
            last_name='Admin'
        )
        print(f"✅ Created superuser: admin / admin123")
        return user
    else:
        print("✅ Superuser already exists")
        return User.objects.get(username='admin')

def create_categories():
    """Create tool categories"""
    categories_data = [
        {
            'name': 'Containerization',
            'slug': 'containerization',
            'description': 'Container platforms and orchestration tools for modern cloud deployments',
            'icon': '🐳'
        },
        {
            'name': 'CI/CD',
            'slug': 'ci-cd',
            'description': 'Continuous Integration and Deployment tools for automated workflows',
            'icon': '🚀'
        },
        {
            'name': 'Monitoring',
            'slug': 'monitoring',
            'description': 'Application and infrastructure monitoring solutions',
            'icon': '📊'
        },
        {
            'name': 'Cloud Platforms',
            'slug': 'cloud-platforms',
            'description': 'Major cloud service providers and infrastructure platforms',
            'icon': '☁️'
        },
        {
            'name': 'DevOps Tools',
            'slug': 'devops-tools',
            'description': 'Essential DevOps automation and management tools',
            'icon': '⚙️'
        },
        {
            'name': 'Security',
            'slug': 'security',
            'description': 'Security scanning, compliance, and vulnerability management tools',
            'icon': '🔒'
        },
        {
            'name': 'Databases',
            'slug': 'databases',
            'description': 'Database systems and data management platforms',
            'icon': '💾'
        },
        {
            'name': 'Infrastructure as Code',
            'slug': 'infrastructure-as-code',
            'description': 'Tools for managing infrastructure through code',
            'icon': '📝'
        }
    ]
    
    print("\n📁 Creating categories...")
    created = []
    for cat_data in categories_data:
        category, created_flag = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'icon': cat_data.get('icon', '📦'),
                'is_featured': True
            }
        )
        if created_flag:
            print(f"  ✅ Created: {category.name}")
            created.append(category)
        else:
            print(f"  ℹ️  Exists: {category.name}")
    
    return Category.objects.all()

def create_tools_with_ai(categories):
    """Create tools with AI-generated content"""
    
    tools_data = [
        # Containerization
        {'name': 'Docker', 'category': 'containerization', 'website': 'https://www.docker.com', 'pricing': 'Free / $7/month', 'features': ['Container Runtime', 'Image Management', 'Docker Compose', 'Swarm Mode']},
        {'name': 'Kubernetes', 'category': 'containerization', 'website': 'https://kubernetes.io', 'pricing': 'Free', 'features': ['Container Orchestration', 'Auto-scaling', 'Service Discovery', 'Load Balancing']},
        {'name': 'Podman', 'category': 'containerization', 'website': 'https://podman.io', 'pricing': 'Free', 'features': ['Daemonless Containers', 'Rootless Mode', 'Docker Compatible', 'Pod Management']},
        {'name': 'Rancher', 'category': 'containerization', 'website': 'https://rancher.com', 'pricing': 'Free / Enterprise', 'features': ['Multi-cluster Management', 'Kubernetes Dashboard', 'RBAC', 'App Catalog']},
        
        # CI/CD
        {'name': 'Jenkins', 'category': 'ci-cd', 'website': 'https://www.jenkins.io', 'pricing': 'Free', 'features': ['Pipeline as Code', '1800+ Plugins', 'Distributed Builds', 'REST API']},
        {'name': 'GitLab CI', 'category': 'ci-cd', 'website': 'https://about.gitlab.com', 'pricing': 'Free / $29/user/month', 'features': ['Auto DevOps', 'Container Registry', 'Security Scanning', 'Kubernetes Integration']},
        {'name': 'GitHub Actions', 'category': 'ci-cd', 'website': 'https://github.com/features/actions', 'pricing': 'Free / $0.008/min', 'features': ['Workflow Automation', 'Matrix Builds', 'Marketplace', 'Self-hosted Runners']},
        {'name': 'CircleCI', 'category': 'ci-cd', 'website': 'https://circleci.com', 'pricing': 'Free / $30/month', 'features': ['Docker Support', 'Parallel Jobs', 'SSH Debugging', 'Orbs']},
        {'name': 'ArgoCD', 'category': 'ci-cd', 'website': 'https://argo-cd.readthedocs.io', 'pricing': 'Free', 'features': ['GitOps', 'Kubernetes Native', 'Multi-cluster', 'SSO Integration']},
        
        # Monitoring
        {'name': 'Prometheus', 'category': 'monitoring', 'website': 'https://prometheus.io', 'pricing': 'Free', 'features': ['Time Series DB', 'PromQL', 'Alerting', 'Service Discovery']},
        {'name': 'Grafana', 'category': 'monitoring', 'website': 'https://grafana.com', 'pricing': 'Free / $299/month', 'features': ['Dashboards', 'Multi-datasource', 'Alerting', 'Plugins']},
        {'name': 'Datadog', 'category': 'monitoring', 'website': 'https://www.datadoghq.com', 'pricing': '$15/host/month', 'features': ['APM', 'Log Management', 'Infrastructure Monitoring', 'AI Insights']},
        {'name': 'New Relic', 'category': 'monitoring', 'website': 'https://newrelic.com', 'pricing': 'Free / $99/month', 'features': ['Full-stack Observability', 'APM', 'Real User Monitoring', 'Alerts']},
        
        # Cloud Platforms
        {'name': 'AWS', 'category': 'cloud-platforms', 'website': 'https://aws.amazon.com', 'pricing': 'Pay-as-you-go', 'features': ['200+ Services', 'Global Infrastructure', 'Managed Services', 'AI/ML Tools']},
        {'name': 'Google Cloud', 'category': 'cloud-platforms', 'website': 'https://cloud.google.com', 'pricing': 'Pay-as-you-go', 'features': ['BigQuery', 'GKE', 'AI Platform', 'Serverless']},
        {'name': 'Microsoft Azure', 'category': 'cloud-platforms', 'website': 'https://azure.microsoft.com', 'pricing': 'Pay-as-you-go', 'features': ['Hybrid Cloud', 'Azure AD', 'AKS', 'DevOps Services']},
        {'name': 'DigitalOcean', 'category': 'cloud-platforms', 'website': 'https://www.digitalocean.com', 'pricing': '$4/month', 'features': ['Droplets', 'Kubernetes', 'App Platform', 'Managed Databases']},
        
        # DevOps Tools
        {'name': 'Terraform', 'category': 'infrastructure-as-code', 'website': 'https://www.terraform.io', 'pricing': 'Free / Enterprise', 'features': ['Infrastructure as Code', 'Multi-cloud', 'State Management', 'Modules']},
        {'name': 'Ansible', 'category': 'devops-tools', 'website': 'https://www.ansible.com', 'pricing': 'Free / Enterprise', 'features': ['Agentless', 'YAML Playbooks', 'Idempotent', 'Extensive Modules']},
        {'name': 'Helm', 'category': 'devops-tools', 'website': 'https://helm.sh', 'pricing': 'Free', 'features': ['Kubernetes Package Manager', 'Charts', 'Release Management', 'Templating']},
        
        # Security
        {'name': 'Snyk', 'category': 'security', 'website': 'https://snyk.io', 'pricing': 'Free / $98/month', 'features': ['Vulnerability Scanning', 'Container Security', 'License Compliance', 'Auto-fix']},
        {'name': 'Trivy', 'category': 'security', 'website': 'https://trivy.dev', 'pricing': 'Free', 'features': ['Container Scanning', 'IaC Scanning', 'Secret Detection', 'SBOM Generation']},
        {'name': 'Vault', 'category': 'security', 'website': 'https://www.vaultproject.io', 'pricing': 'Free / Enterprise', 'features': ['Secret Management', 'Encryption as a Service', 'Dynamic Secrets', 'PKI']},
        
        # Databases
        {'name': 'PostgreSQL', 'category': 'databases', 'website': 'https://www.postgresql.org', 'pricing': 'Free', 'features': ['ACID Compliant', 'JSON Support', 'Full-text Search', 'Replication']},
        {'name': 'MongoDB', 'category': 'databases', 'website': 'https://www.mongodb.com', 'pricing': 'Free / $57/month', 'features': ['Document DB', 'Horizontal Scaling', 'Aggregation', 'ACID Transactions']},
        {'name': 'Redis', 'category': 'databases', 'website': 'https://redis.io', 'pricing': 'Free / Managed', 'features': ['In-memory DB', 'Caching', 'Pub/Sub', 'Streams']},
    ]
    
    print("\n🔧 Creating tools with AI-generated descriptions...")
    
    created_tools = []
    for idx, tool_data in enumerate(tools_data, 1):
        # Find category
        category = categories.filter(slug=tool_data['category']).first()
        if not category:
            print(f"  ⚠️  Category not found: {tool_data['category']}")
            continue
        
        # Check if tool exists
        if Tool.objects.filter(name=tool_data['name']).exists():
            print(f"  ℹ️  [{idx}/{len(tools_data)}] Exists: {tool_data['name']}")
            continue
        
        print(f"  🤖 [{idx}/{len(tools_data)}] Generating AI content for {tool_data['name']}...")
        
        # Generate description with AI
        prompt = f"""Write a compelling 2-3 sentence description for {tool_data['name']}, a {category.name.lower()} tool. 
        Focus on its main value proposition and why developers choose it. Be concise and professional."""
        
        try:
            result = gemini.generate_content(prompt, temperature=0.7, max_tokens=150)
            description = result['content'].strip()
            
            # Create tool
            tool = Tool.objects.create(
                name=tool_data['name'],
                slug=tool_data['name'].lower().replace(' ', '-'),
                description=description,
                category=category,
                website_url=tool_data['website'],
                pricing_model='freemium' if 'Free' in tool_data['pricing'] else 'paid',
                features=tool_data['features'],
                is_published=True,
                rating_sum=int((4.0 + (idx % 5) * 0.2) * 10),  # Initial ratings
                rating_count=10,  # Simulated 10 reviews
                tags=['popular', 'devops', category.slug]
            )
            
            created_tools.append(tool)
            print(f"      ✅ Created with AI description")
            
        except Exception as e:
            print(f"      ⚠️  AI generation failed: {str(e)[:100]}")
            # Create with basic description
            tool = Tool.objects.create(
                name=tool_data['name'],
                slug=tool_data['name'].lower().replace(' ', '-'),
                description=f"{tool_data['name']} is a popular {category.name.lower()} tool used by developers worldwide.",
                category=category,
                website_url=tool_data['website'],
                pricing_model='freemium' if 'Free' in tool_data['pricing'] else 'paid',
                features=tool_data['features'],
                is_published=True,
                rating_sum=int((4.0 + (idx % 5) * 0.2) * 10),
                rating_count=10,
                tags=['popular', 'devops', category.slug]
            )
            created_tools.append(tool)
            print(f"      ✅ Created with basic description")
    
    return created_tools

def create_articles_with_ai(tools, categories, author):
    """Create blog articles with AI-generated content"""
    
    print("\n📝 Creating articles with AI-generated content...")
    
    article_topics = [
        {
            'type': 'comparison',
            'title': 'Docker vs Kubernetes: Which Container Technology Should You Choose?',
            'tools': ['Docker', 'Kubernetes'],
            'category': 'containerization'
        },
        {
            'type': 'review',
            'title': 'Complete Guide to Getting Started with Terraform in 2025',
            'tools': ['Terraform'],
            'category': 'infrastructure-as-code'
        },
        {
            'type': 'guide',
            'title': 'Best CI/CD Tools for Modern DevOps Teams',
            'tools': ['Jenkins', 'GitLab CI', 'GitHub Actions'],
            'category': 'ci-cd'
        },
        {
            'type': 'comparison',
            'title': 'AWS vs Google Cloud vs Azure: Complete Cloud Comparison 2025',
            'tools': ['AWS', 'Google Cloud', 'Microsoft Azure'],
            'category': 'cloud-platforms'
        },
        {
            'type': 'tutorial',
            'title': 'Setting Up Prometheus and Grafana for Kubernetes Monitoring',
            'tools': ['Prometheus', 'Grafana', 'Kubernetes'],
            'category': 'monitoring'
        },
        {
            'type': 'review',
            'title': 'Why Developers Are Switching from Docker to Podman',
            'tools': ['Podman', 'Docker'],
            'category': 'containerization'
        },
        {
            'type': 'guide',
            'title': 'Complete Guide to Container Security with Trivy and Snyk',
            'tools': ['Trivy', 'Snyk'],
            'category': 'security'
        },
        {
            'type': 'comparison',
            'title': 'PostgreSQL vs MongoDB: Choosing the Right Database',
            'tools': ['PostgreSQL', 'MongoDB'],
            'category': 'databases'
        },
        {
            'type': 'tutorial',
            'title': 'Deploy Your First Application with ArgoCD and GitOps',
            'tools': ['ArgoCD', 'Kubernetes'],
            'category': 'ci-cd'
        },
        {
            'type': 'review',
            'title': 'Ansible vs Terraform: Infrastructure Automation Showdown',
            'tools': ['Ansible', 'Terraform'],
            'category': 'devops-tools'
        },
        {
            'type': 'guide',
            'title': 'Top 10 DevOps Tools Every Developer Should Know in 2025',
            'tools': ['Docker', 'Kubernetes', 'Jenkins', 'Terraform'],
            'category': 'devops-tools'
        },
        {
            'type': 'tutorial',
            'title': 'Mastering Helm: Package Management for Kubernetes',
            'tools': ['Helm', 'Kubernetes'],
            'category': 'devops-tools'
        },
    ]
    
    created_articles = []
    
    for idx, article_data in enumerate(article_topics, 1):
        # Check if article exists
        if Article.objects.filter(title=article_data['title']).exists():
            print(f"  ℹ️  [{idx}/{len(article_topics)}] Exists: {article_data['title'][:50]}...")
            continue
        
        print(f"  🤖 [{idx}/{len(article_topics)}] Generating: {article_data['title'][:60]}...")
        
        # Find category
        category = categories.filter(slug=article_data['category']).first()
        
        # Find related tools
        related_tool_ids = []
        for tool_name in article_data['tools']:
            tool = Tool.objects.filter(name=tool_name).first()
            if tool:
                related_tool_ids.append(tool.id)
        
        # Generate article content with AI
        prompt = f"""Write a comprehensive blog article with the title: "{article_data['title']}"

This is a {article_data['type']} article about {', '.join(article_data['tools'])}.

Structure the article with:
1. Introduction (2-3 paragraphs)
2. Main content sections with clear headings
3. Practical examples or comparisons
4. Conclusion with key takeaways

Write in a professional but friendly tone. Target audience: DevOps engineers and developers.
Length: 800-1200 words. Use markdown formatting for headings.
"""
        
        try:
            result = gemini.generate_content(prompt, temperature=0.7, max_tokens=2000)
            content = result['content'].strip()
            
            # Generate excerpt
            excerpt_prompt = f"Write a compelling 2-sentence excerpt for an article titled '{article_data['title']}'. Make it engaging and SEO-friendly."
            excerpt_result = gemini.generate_content(excerpt_prompt, temperature=0.7, max_tokens=100)
            excerpt = excerpt_result['content'].strip()
            
            # Create article
            article = Article.objects.create(
                title=article_data['title'],
                slug=article_data['title'].lower()[:50].replace(' ', '-').replace(':', '').replace('?', ''),
                excerpt=excerpt,
                content=content,
                article_type=article_data['type'],
                category=category,
                author=author,
                related_tools=related_tool_ids,
                is_published=True,
                is_featured=(idx <= 4),  # First 4 are featured
                published_at=timezone.now() - timedelta(days=len(article_topics) - idx),
                ai_generated=True,
                ai_provider='Google Gemini',
                ai_model='gemini-2.0-flash',
                tags=['devops', 'cloud', 'tutorial', article_data['category']]
            )
            
            created_articles.append(article)
            print(f"      ✅ Created with AI content ({article.word_count} words)")
            
        except Exception as e:
            print(f"      ⚠️  AI generation failed: {str(e)[:100]}")
            # Create with placeholder content
            article = Article.objects.create(
                title=article_data['title'],
                slug=article_data['title'].lower()[:50].replace(' ', '-').replace(':', '').replace('?', ''),
                excerpt=f"Learn about {', '.join(article_data['tools'])} in this comprehensive guide.",
                content=f"# {article_data['title']}\n\nThis article provides a detailed look at {', '.join(article_data['tools'])}.\n\nContent coming soon...",
                article_type=article_data['type'],
                category=category,
                author=author,
                related_tools=related_tool_ids,
                is_published=True,
                is_featured=(idx <= 4),
                published_at=timezone.now() - timedelta(days=len(article_topics) - idx),
                tags=['devops', 'cloud', 'tutorial']
            )
            created_articles.append(article)
            print(f"      ✅ Created with placeholder content")
    
    return created_articles

def main():
    print("=" * 70)
    print("🚀 CloudEngineered Content Population Script")
    print("=" * 70)
    print("\nThis script will populate your database with:")
    print("  • Tool categories")
    print("  • DevOps tools with AI-generated descriptions")
    print("  • Blog articles with AI-generated content")
    print("  • All using FREE Google Gemini API")
    print()
    
    # Create superuser
    author = create_superuser()
    
    # Create categories
    categories = create_categories()
    print(f"\n✅ Total categories: {categories.count()}")
    
    # Create tools
    tools = create_tools_with_ai(categories)
    total_tools = Tool.objects.count()
    print(f"\n✅ Total tools: {total_tools}")
    
    # Create articles
    articles = create_articles_with_ai(Tool.objects.all(), categories, author)
    total_articles = Article.objects.count()
    print(f"\n✅ Total articles: {total_articles}")
    
    print("\n" + "=" * 70)
    print("🎉 Content Population Complete!")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"  • Categories: {categories.count()}")
    print(f"  • Tools: {total_tools}")
    print(f"  • Articles: {total_articles}")
    print(f"  • Superuser: admin / admin123")
    print(f"\n🌐 Next steps:")
    print(f"  1. Start server: python manage.py runserver 0.0.0.0:8000")
    print(f"  2. Visit: http://localhost:8000/")
    print(f"  3. Admin: http://localhost:8000/admin/")
    print(f"\n✅ All pages now have content - no empty pages!")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
