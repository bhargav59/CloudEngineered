#!/usr/bin/env python
"""
Script to populate comprehensive tool comparison data for CloudEngineered platform.
This creates detailed, technical comparisons similar to the Terraform vs Pulumi example.
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

def create_comprehensive_comparisons():
    """Create detailed technical tool comparisons"""
    print("Creating comprehensive tool comparisons...")
    
    # Get users for authoring
    users = list(User.objects.all())
    if not users:
        print("No users found. Please create users first.")
        return
    
    # Delete existing comparisons to avoid duplicates
    ToolComparison.objects.all().delete()
    print("Cleared existing comparisons")
    
    # Comprehensive comparison data
    comparisons_data = [
        {
            'title': 'Terraform vs Pulumi: Infrastructure as Code Deep Dive',
            'description': 'A comprehensive comparison between Terraform and Pulumi for Infrastructure as Code implementations, covering language support, state management, ecosystem, and more.',
            'tool_names': ['Terraform', 'Pulumi'],
            'introduction': '''Terraform and Pulumi are both popular Infrastructure as Code (IaC) tools, but they differ significantly in approach, flexibility, and ecosystem. This comprehensive comparison will help you understand the key differences and choose the right tool for your cloud engineering needs.''',
            'sections': {
                'Language & Syntax': {
                    'terraform': {
                        'description': 'Uses HCL (HashiCorp Configuration Language), a declarative DSL.',
                        'details': [
                            'Great for describing infrastructure in a straightforward, YAML-like style',
                            'Limited programming constructs (loops, conditionals exist but are basic)',
                            'Domain-specific language designed specifically for infrastructure',
                            'Clear separation between configuration and logic'
                        ],
                        'pros': ['Simple to learn', 'Clear intent', 'Domain-specific clarity'],
                        'cons': ['Limited programming constructs', 'Verbose for complex logic']
                    },
                    'pulumi': {
                        'description': 'Uses general-purpose programming languages: TypeScript, JavaScript, Python, Go, C#, Java.',
                        'details': [
                            'Full access to programming constructs (loops, conditionals, classes, functions)',
                            'Easier integration with existing app codebases',
                            'Rich IDE support with autocomplete and debugging',
                            'Familiar development patterns and best practices'
                        ],
                        'pros': ['Flexibility & code reuse', 'Full programming power', 'IDE support'],
                        'cons': ['Can be over-engineered', 'Steeper learning curve for ops teams']
                    }
                },
                'State Management': {
                    'terraform': {
                        'description': 'State stored locally or in remote backends (S3, GCS, Terraform Cloud, etc.).',
                        'details': [
                            'Mature state handling with locking to avoid race conditions',
                            'Multiple backend options for team collaboration',
                            'State file contains sensitive information',
                            'Manual state operations available for troubleshooting'
                        ],
                        'pros': ['Mature and battle-tested', 'Multiple backend options', 'Good locking mechanisms'],
                        'cons': ['Manual state management needed', 'State file security concerns']
                    },
                    'pulumi': {
                        'description': 'Stores state in Pulumi Service by default (SaaS).',
                        'details': [
                            'Can also use self-managed backends (S3, Azure Blob, GCS)',
                            'Automatic secrets management with strong encryption',
                            'Built-in state inspection and history',
                            'Automatic state backup and recovery'
                        ],
                        'pros': ['Automatic secrets encryption', 'Built-in state history', 'Easy setup'],
                        'cons': ['Default SaaS dependency', 'Less control over state format']
                    }
                },
                'Ecosystem & Providers': {
                    'terraform': {
                        'description': 'Extremely large provider ecosystem.',
                        'details': [
                            'Backed by HashiCorp and huge community support',
                            'Many providers mature and well-tested',
                            'Over 3000+ providers available',
                            'Industry standard with wide adoption'
                        ],
                        'pros': ['Largest ecosystem', 'Mature providers', 'Industry standard'],
                        'cons': ['Provider quality varies', 'Some providers lag behind']
                    },
                    'pulumi': {
                        'description': 'Also supports many providers (uses Terraform providers via Pulumi Terraform Bridge).',
                        'details': [
                            'Some providers are native (AWS, Azure, GCP, Kubernetes)',
                            'Can leverage existing Terraform providers',
                            'Richer experience with native providers',
                            'Growing ecosystem with active development'
                        ],
                        'pros': ['Native provider experience', 'Terraform provider compatibility', 'Active development'],
                        'cons': ['Smaller ecosystem than Terraform', 'Some providers are wrappers']
                    }
                },
                'Learning Curve & Adoption': {
                    'terraform': {
                        'description': 'Easier for beginners, especially those new to programming.',
                        'details': [
                            'Declarative model is more straightforward',
                            'Extensive documentation and tutorials',
                            'Large community and Stack Overflow support',
                            'Clear separation of concerns'
                        ],
                        'pros': ['Beginner-friendly', 'Extensive community', 'Clear documentation'],
                        'cons': ['Less familiar to developers', 'Limited to HCL syntax']
                    },
                    'pulumi': {
                        'description': 'Familiar for developers, but heavier learning curve for ops teams.',
                        'details': [
                            'Power users love the flexibility but may over-engineer',
                            'Familiar development patterns and tooling',
                            'Strong IDE support and debugging capabilities',
                            'Natural fit for DevOps teams with programming background'
                        ],
                        'pros': ['Developer-friendly', 'Powerful abstractions', 'IDE support'],
                        'cons': ['Can be over-engineered', 'Ops team learning curve']
                    }
                }
            },
            'feature_matrix': {
                'Language Support': {'terraform': '⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐⭐'},
                'State Management': {'terraform': '⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐⭐'},
                'Provider Ecosystem': {'terraform': '⭐⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐'},
                'Learning Curve': {'terraform': '⭐⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐'},
                'Community Support': {'terraform': '⭐⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐'},
                'CI/CD Integration': {'terraform': '⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐⭐'},
                'Cost': {'terraform': '⭐⭐⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐'},
                'Modularity': {'terraform': '⭐⭐⭐', 'pulumi': '⭐⭐⭐⭐⭐'}
            },
            'summary_table': {
                'Language': {'terraform': 'HCL (DSL)', 'pulumi': 'General-purpose (TS, Python, Go, etc.)'},
                'State Management': {'terraform': 'Local/Remote (Terraform Cloud, S3, etc.)', 'pulumi': 'Pulumi Service (default), or self-hosted'},
                'Ecosystem': {'terraform': 'Very large', 'pulumi': 'Large, with some Terraform reuse'},
                'Modularity': {'terraform': 'Modules (limited)', 'pulumi': 'Full programming abstractions'},
                'Learning Curve': {'terraform': 'Easier for beginners', 'pulumi': 'Easier for devs, harder for ops'},
                'CI/CD Integration': {'terraform': 'Mature, widely adopted', 'pulumi': 'Strong, dev-focused'},
                'Cost': {'terraform': 'Free OSS, Cloud pricing', 'pulumi': 'Free OSS, Service pricing'},
                'Community': {'terraform': 'Larger, industry-standard', 'pulumi': 'Growing, developer-friendly'}
            },
            'use_case_recommendations': {
                'Choose Terraform if': [
                    'Your team prefers a declarative DSL',
                    'You want a widely adopted, ops-friendly tool',
                    'You need stability and a huge ecosystem',
                    'Multi-cloud deployments with established workflows',
                    'Team has limited programming experience'
                ],
                'Choose Pulumi if': [
                    'Your team is developer-heavy and comfortable with programming languages',
                    'You want to build reusable infrastructure libraries',
                    'You need advanced logic or integration with app code',
                    'Strong IDE support and debugging capabilities are important',
                    'You prefer infrastructure as real code rather than configuration'
                ]
            },
            'conclusion': '''Both Terraform and Pulumi are excellent IaC tools with their own strengths. Terraform has broader provider support and a larger community, while Pulumi offers familiar programming languages and powerful abstractions. Your choice should depend on your team's background, requirements, and preferences.''',
            'recommendation': '''For teams new to IaC or with strong ops backgrounds, Terraform provides a gentler learning curve and industry-standard approach. For development-heavy teams or those needing complex infrastructure logic, Pulumi offers more flexibility and familiar programming patterns.'''
        },
        {
            'title': 'Docker vs Podman: Container Runtime Security and Architecture',
            'description': 'An in-depth comparison of Docker and Podman container runtimes, focusing on security models, architecture differences, and operational considerations.',
            'tool_names': ['Docker', 'Podman'],
            'introduction': '''Docker and Podman are both container runtimes that allow you to build, run, and manage containers. While Docker has been the industry standard for years, Podman has emerged as a compelling alternative with unique security advantages and architectural differences.''',
            'sections': {
                'Architecture & Security Model': {
                    'docker': {
                        'description': 'Client-server architecture with a daemon running as root.',
                        'details': [
                            'Docker daemon runs with root privileges',
                            'All containers share the same daemon process',
                            'Client communicates with daemon via REST API',
                            'Requires Docker daemon to be running at all times'
                        ],
                        'pros': ['Mature and stable', 'Wide ecosystem support', 'Easy to use'],
                        'cons': ['Security concerns with root daemon', 'Single point of failure']
                    },
                    'podman': {
                        'description': 'Daemonless architecture with rootless container support.',
                        'details': [
                            'No central daemon required',
                            'Runs containers as regular user processes',
                            'Each container is an independent process',
                            'Better security isolation by default'
                        ],
                        'pros': ['Enhanced security', 'No daemon dependency', 'Rootless operation'],
                        'cons': ['Newer with smaller ecosystem', 'Some Docker features missing']
                    }
                },
                'Container Management': {
                    'docker': {
                        'description': 'Comprehensive container lifecycle management through Docker daemon.',
                        'details': [
                            'Docker Compose for multi-container applications',
                            'Docker Swarm for orchestration',
                            'Rich CLI with extensive options',
                            'Integrated volume and network management'
                        ],
                        'pros': ['Feature-complete', 'Excellent tooling', 'Compose integration'],
                        'cons': ['Daemon dependency', 'Resource overhead']
                    },
                    'podman': {
                        'description': 'Direct container management with systemd integration.',
                        'details': [
                            'Podman Compose for Docker Compose compatibility',
                            'Native systemd integration for service management',
                            'Pods concept similar to Kubernetes',
                            'Direct integration with systemd for auto-start'
                        ],
                        'pros': ['Systemd integration', 'Kubernetes-like pods', 'No daemon overhead'],
                        'cons': ['Limited orchestration', 'Compose compatibility issues']
                    }
                },
                'Image Compatibility': {
                    'docker': {
                        'description': 'Native support for Docker images and registries.',
                        'details': [
                            'Full compatibility with Docker Hub',
                            'Native support for all Docker image formats',
                            'Extensive registry ecosystem',
                            'Image layering and caching optimizations'
                        ],
                        'pros': ['Perfect image compatibility', 'Optimized caching', 'Registry ecosystem'],
                        'cons': ['Proprietary format dependencies', 'Vendor lock-in concerns']
                    },
                    'podman': {
                        'description': 'OCI-compliant with Docker image compatibility.',
                        'details': [
                            'Supports Docker images and OCI format',
                            'Compatible with Docker Hub and other registries',
                            'Can run most Docker containers without modification',
                            'Better support for OCI standards'
                        ],
                        'pros': ['OCI compliance', 'Docker compatibility', 'Open standards'],
                        'cons': ['Some Docker-specific features unsupported', 'Performance differences']
                    }
                }
            },
            'feature_matrix': {
                'Security Model': {'docker': '⭐⭐⭐', 'podman': '⭐⭐⭐⭐⭐'},
                'Performance': {'docker': '⭐⭐⭐⭐', 'podman': '⭐⭐⭐⭐'},
                'Ecosystem Support': {'docker': '⭐⭐⭐⭐⭐', 'podman': '⭐⭐⭐'},
                'Ease of Use': {'docker': '⭐⭐⭐⭐⭐', 'podman': '⭐⭐⭐⭐'},
                'Rootless Operation': {'docker': '⭐⭐', 'podman': '⭐⭐⭐⭐⭐'},
                'Image Compatibility': {'docker': '⭐⭐⭐⭐⭐', 'podman': '⭐⭐⭐⭐'},
                'Orchestration': {'docker': '⭐⭐⭐⭐', 'podman': '⭐⭐⭐'},
                'Resource Usage': {'docker': '⭐⭐⭐', 'podman': '⭐⭐⭐⭐⭐'}
            },
            'summary_table': {
                'Architecture': {'docker': 'Client-server with daemon', 'podman': 'Daemonless'},
                'Security': {'docker': 'Root daemon (security concerns)', 'podman': 'Rootless by default'},
                'Compatibility': {'docker': 'Native Docker images', 'podman': 'OCI + Docker compatible'},
                'Orchestration': {'docker': 'Docker Swarm, Compose', 'podman': 'Systemd, limited Compose'},
                'Ecosystem': {'docker': 'Huge, mature', 'podman': 'Growing, Red Hat backed'},
                'Performance': {'docker': 'Optimized, daemon overhead', 'podman': 'Good, no daemon overhead'},
                'Learning Curve': {'docker': 'Easy, industry standard', 'podman': 'Moderate, similar to Docker'},
                'Enterprise Support': {'docker': 'Docker Enterprise', 'podman': 'Red Hat support'}
            },
            'use_case_recommendations': {
                'Choose Docker if': [
                    'You need maximum ecosystem compatibility',
                    'Your team is already familiar with Docker',
                    'You rely heavily on Docker Compose',
                    'You need the most mature tooling and support',
                    'Performance optimization is critical'
                ],
                'Choose Podman if': [
                    'Security is a top priority',
                    'You want rootless container operation',
                    'You prefer systemd integration',
                    'You want to avoid daemon dependencies',
                    'You\'re building for Red Hat/CentOS environments'
                ]
            },
            'conclusion': '''Both Docker and Podman are excellent container runtimes with different architectural approaches. Docker offers maturity and ecosystem support, while Podman provides enhanced security and modern architecture without daemon dependencies.''',
            'recommendation': '''For most teams and production environments, Docker remains the safer choice due to its maturity and ecosystem. However, for security-conscious environments or new deployments, Podman offers compelling advantages with its rootless operation and modern architecture.'''
        },
        {
            'title': 'Kubernetes vs Docker Swarm: Container Orchestration Platforms',
            'description': 'A detailed comparison between Kubernetes and Docker Swarm for container orchestration, covering complexity, scalability, and operational considerations.',
            'tool_names': ['Kubernetes', 'Docker Swarm'],
            'introduction': '''Container orchestration has become essential for managing containerized applications at scale. Kubernetes and Docker Swarm represent two different philosophies: Kubernetes offers comprehensive features and flexibility, while Docker Swarm provides simplicity and ease of use.''',
            'sections': {
                'Architecture & Complexity': {
                    'kubernetes': {
                        'description': 'Complex, feature-rich orchestration platform with extensive capabilities.',
                        'details': [
                            'Master-worker architecture with multiple components',
                            'Extensive API surface with numerous resource types',
                            'Highly configurable and extensible',
                            'Steep learning curve but powerful capabilities'
                        ],
                        'pros': ['Highly scalable', 'Feature-rich', 'Industry standard', 'Extensible'],
                        'cons': ['Complex setup', 'Steep learning curve', 'Resource intensive']
                    },
                    'docker-swarm': {
                        'description': 'Simple, integrated orchestration solution built into Docker.',
                        'details': [
                            'Manager-worker architecture with simple setup',
                            'Limited but focused feature set',
                            'Easy to understand and operate',
                            'Quick to get started with minimal configuration'
                        ],
                        'pros': ['Simple setup', 'Easy to learn', 'Integrated with Docker', 'Low overhead'],
                        'cons': ['Limited features', 'Less scalable', 'Smaller ecosystem']
                    }
                },
                'Scalability & Performance': {
                    'kubernetes': {
                        'description': 'Designed for large-scale, enterprise deployments.',
                        'details': [
                            'Can handle thousands of nodes and containers',
                            'Horizontal pod autoscaling and cluster autoscaling',
                            'Advanced scheduling and resource management',
                            'High availability and fault tolerance'
                        ],
                        'pros': ['Massive scale', 'Auto-scaling', 'Advanced scheduling', 'High availability'],
                        'cons': ['Resource overhead', 'Complex scaling decisions']
                    },
                    'docker-swarm': {
                        'description': 'Suitable for small to medium-scale deployments.',
                        'details': [
                            'Good performance for moderate workloads',
                            'Simple scaling operations',
                            'Lower resource overhead',
                            'Limited advanced scheduling features'
                        ],
                        'pros': ['Low overhead', 'Simple scaling', 'Good performance'],
                        'cons': ['Limited scale', 'Basic scheduling', 'Fewer HA options']
                    }
                },
                'Ecosystem & Community': {
                    'kubernetes': {
                        'description': 'Massive ecosystem with CNCF backing and industry adoption.',
                        'details': [
                            'Huge community and ecosystem',
                            'Extensive third-party tools and integrations',
                            'Cloud provider managed services',
                            'Continuous innovation and development'
                        ],
                        'pros': ['Huge ecosystem', 'Industry standard', 'Cloud integration', 'Active development'],
                        'cons': ['Overwhelming choices', 'Rapid change', 'Tool fragmentation']
                    },
                    'docker-swarm': {
                        'description': 'Smaller but focused ecosystem with Docker Inc. backing.',
                        'details': [
                            'Limited but stable ecosystem',
                            'Direct Docker integration',
                            'Fewer third-party tools',
                            'Slower innovation pace'
                        ],
                        'pros': ['Stable', 'Docker integration', 'Focused approach'],
                        'cons': ['Limited ecosystem', 'Fewer tools', 'Less innovation']
                    }
                }
            },
            'feature_matrix': {
                'Complexity': {'kubernetes': '⭐⭐', 'docker-swarm': '⭐⭐⭐⭐⭐'},
                'Scalability': {'kubernetes': '⭐⭐⭐⭐⭐', 'docker-swarm': '⭐⭐⭐'},
                'Features': {'kubernetes': '⭐⭐⭐⭐⭐', 'docker-swarm': '⭐⭐⭐'},
                'Learning Curve': {'kubernetes': '⭐⭐', 'docker-swarm': '⭐⭐⭐⭐⭐'},
                'Ecosystem': {'kubernetes': '⭐⭐⭐⭐⭐', 'docker-swarm': '⭐⭐'},
                'Cloud Integration': {'kubernetes': '⭐⭐⭐⭐⭐', 'docker-swarm': '⭐⭐⭐'},
                'Resource Usage': {'kubernetes': '⭐⭐', 'docker-swarm': '⭐⭐⭐⭐'},
                'High Availability': {'kubernetes': '⭐⭐⭐⭐⭐', 'docker-swarm': '⭐⭐⭐'}
            },
            'summary_table': {
                'Setup Complexity': {'kubernetes': 'Complex', 'docker-swarm': 'Simple'},
                'Learning Curve': {'kubernetes': 'Steep', 'docker-swarm': 'Gentle'},
                'Scalability': {'kubernetes': 'Massive (1000+ nodes)', 'docker-swarm': 'Moderate (100s of nodes)'},
                'Features': {'kubernetes': 'Comprehensive', 'docker-swarm': 'Basic but sufficient'},
                'Ecosystem': {'kubernetes': 'Huge', 'docker-swarm': 'Limited'},
                'Cloud Support': {'kubernetes': 'Excellent (EKS, GKE, AKS)', 'docker-swarm': 'Basic'},
                'Resource Overhead': {'kubernetes': 'High', 'docker-swarm': 'Low'},
                'Best For': {'kubernetes': 'Large-scale, complex apps', 'docker-swarm': 'Simple, small-scale apps'}
            },
            'use_case_recommendations': {
                'Choose Kubernetes if': [
                    'You need to scale to hundreds or thousands of nodes',
                    'You require advanced features like autoscaling and advanced networking',
                    'You want access to the largest ecosystem of tools',
                    'You\'re building for cloud-native applications',
                    'You have dedicated platform engineering resources'
                ],
                'Choose Docker Swarm if': [
                    'You want simple, quick setup and operation',
                    'Your team is already familiar with Docker',
                    'You have small to medium-scale applications',
                    'You prefer simplicity over advanced features',
                    'You want minimal operational overhead'
                ]
            },
            'conclusion': '''Kubernetes and Docker Swarm serve different needs in the container orchestration space. Kubernetes is the clear choice for large-scale, complex deployments, while Docker Swarm excels in scenarios where simplicity and ease of use are priorities.''',
            'recommendation': '''Choose Kubernetes if you need enterprise-scale features and have the resources to manage its complexity. Choose Docker Swarm if you want to get started quickly with container orchestration and don\'t need advanced features.'''
        }
    ]
    
    created_count = 0
    for comp_data in comparisons_data:
        # Find the tools
        tools = []
        for tool_name in comp_data['tool_names']:
            try:
                tool = Tool.objects.filter(name__icontains=tool_name).first()
                if tool:
                    tools.append(tool)
                else:
                    print(f"Tool '{tool_name}' not found, skipping...")
            except Exception as e:
                print(f"Error finding tool '{tool_name}': {str(e)}")
        
        if len(tools) < 2:
            print(f"Not enough tools found for comparison '{comp_data['title']}', skipping...")
            continue
        
        # Create the comparison
        try:
            comparison = ToolComparison.objects.create(
                title=comp_data['title'],
                description=comp_data['description'],
                introduction=comp_data['introduction'],
                conclusion=comp_data['conclusion'],
                recommendation=comp_data['recommendation'],
                sections=comp_data['sections'],
                feature_matrix=comp_data['feature_matrix'],
                summary_table=comp_data['summary_table'],
                use_case_recommendations=comp_data['use_case_recommendations'],
                author=random.choice(users),
                is_published=True,
                view_count=random.randint(500, 5000),
                criteria=[
                    'Architecture',
                    'Ease of Use',
                    'Performance', 
                    'Scalability',
                    'Security',
                    'Community Support',
                    'Documentation',
                    'Cost',
                    'Learning Curve',
                    'Ecosystem'
                ]
            )
            
            # Add the tools to the comparison
            comparison.tools.set(tools)
            created_count += 1
            print(f"  ✓ Created comprehensive comparison: {comp_data['title']}")
                
        except Exception as e:
            print(f"  ❌ Error creating comparison '{comp_data['title']}': {str(e)}")
    
    print(f"\nCreated {created_count} comprehensive comparisons")
    
    # Display summary
    total_comparisons = ToolComparison.objects.filter(is_published=True).count()
    print(f"Total published comparisons: {total_comparisons}")

if __name__ == '__main__':
    create_comprehensive_comparisons()