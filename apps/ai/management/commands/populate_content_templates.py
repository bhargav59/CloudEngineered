from django.core.management.base import BaseCommand
from apps.ai.models import ContentTemplate, AIModel


class Command(BaseCommand):
    help = 'Populate content templates for AI generation'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating content templates...'))

        # Get default AI model
        try:
            default_model = AIModel.objects.filter(name='gpt-4o-mini', is_active=True).first()
            if not default_model:
                default_model = AIModel.objects.filter(is_active=True).first()
        except:
            self.stdout.write(self.style.ERROR('No AI models found. Run setup_ai_providers first.'))
            return

        # Tool Review Template
        tool_review_template, created = ContentTemplate.objects.get_or_create(
            name='Tool Review Template',
            template_type='tool_review',
            defaults={
                'system_prompt': """You are an expert DevOps engineer and technical writer specializing in cloud infrastructure and automation tools. Write detailed, accurate, and practical tool reviews for technical professionals.""",
                'user_prompt_template': """Write a comprehensive and professional review of the DevOps/Cloud tool: {tool_name}

Tool Description: {tool_description}
Key features: {features}
Website: {website_url}
Category: {category}

Please provide a detailed review covering:

1. **Overview & Purpose**: What the tool does and its primary use cases
2. **Key Features**: Main capabilities and functionalities  
3. **Pros**: Advantages and strengths
4. **Cons**: Limitations and potential drawbacks
5. **Use Cases**: Ideal scenarios for using this tool
6. **Pricing Model**: General pricing approach
7. **Integration Capabilities**: How it works with other tools
8. **Learning Curve**: Ease of adoption and learning
9. **Community & Support**: Documentation, community, and support quality
10. **Overall Rating**: Summary and recommendation (1-5 stars)

Please write in a professional, informative tone suitable for DevOps engineers and technical decision-makers. 
Focus on practical insights and real-world applications.

Format the response as structured text with clear sections and bullet points where appropriate.""",
                'output_format': 'Structured text with sections: Overview, Features, Pros, Cons, Use Cases, Pricing, Integration, Learning Curve, Community, Rating',
                'model': default_model,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {tool_review_template.name}'))

        # Tutorial Article Template
        tutorial_template, created = ContentTemplate.objects.get_or_create(
            name='Tutorial Article Template',
            template_type='tutorial',
            defaults={
                'system_prompt': """You are an experienced DevOps engineer and technical educator. Create comprehensive, practical tutorials that help readers learn and implement DevOps tools and practices.""",
                'user_prompt_template': """Write a comprehensive tutorial article titled: "{title}"

Topic: {topic}
Target Audience: {target_audience} level
Estimated Reading Time: {reading_time} minutes

Please create a detailed tutorial that includes:

1. **Introduction**: 
   - What readers will learn
   - Why this topic is important
   - Brief overview of the process

2. **Prerequisites**: 
   - Required knowledge level
   - Tools and software needed
   - System requirements

3. **Step-by-Step Guide**:
   - Clear, numbered steps
   - Code examples with explanations
   - Screenshots descriptions where helpful
   - Commands and configurations

4. **Best Practices**:
   - Industry recommendations
   - Security considerations
   - Performance optimization tips

5. **Troubleshooting**:
   - Common issues and solutions
   - Error messages and fixes
   - Debugging tips

6. **Conclusion**:
   - Summary of what was accomplished
   - Next steps for readers
   - Advanced topics to explore

7. **Additional Resources**:
   - Official documentation links
   - Useful tools and extensions
   - Further reading suggestions

Format the article in Markdown with:
- Proper headings (H1, H2, H3)
- Code blocks with syntax highlighting
- Lists and bullet points
- Links to resources
- Clear step numbering

Make it practical, actionable, and valuable for DevOps professionals. Target approximately 1500-2500 words.""",
                'output_format': 'Markdown formatted article with sections: Introduction, Prerequisites, Step-by-Step Guide, Best Practices, Troubleshooting, Conclusion, Resources',
                'model': default_model,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {tutorial_template.name}'))

        # Tool Comparison Template
        comparison_template, created = ContentTemplate.objects.get_or_create(
            name='Tool Comparison Template',
            template_type='comparison',
            defaults={
                'system_prompt': """You are a senior DevOps consultant with extensive experience evaluating and comparing different tools. Provide objective, detailed comparisons that help technical teams make informed decisions.""",
                'user_prompt_template': """Create a comprehensive comparison of these DevOps/Cloud tools: {tools_list}

Comparison focus: {comparison_focus}
Target audience: {target_audience}

Please provide a detailed comparison covering:
1. Executive Summary with key differentiators
2. Feature Comparison Matrix
3. Detailed Analysis of strengths/weaknesses
4. Use Case Scenarios
5. Pricing Analysis
6. Integration & Ecosystem
7. Implementation Considerations
8. Final Recommendations

Format with clear sections, comparison tables, and practical insights for technical decision-makers.""",
                'output_format': 'Structured comparison with sections and tables',
                'model': default_model,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {comparison_template.name}'))

        # How-to Guide Template
        howto_template, created = ContentTemplate.objects.get_or_create(
            name='How-to Guide Template',
            template_type='guide',
            defaults={
                'system_prompt': """You are a DevOps practitioner who excels at creating clear, actionable how-to guides. Focus on practical solutions and real-world scenarios.""",
                'user_prompt_template': """Write a practical how-to guide: "{title}"

Objective: {objective}
Tools involved: {tools}
Difficulty level: {difficulty_level}

Create a practical guide with:
1. Goal & Overview
2. Before You Begin (prerequisites)
3. Step-by-Step Instructions
4. Validation & Testing
5. Optimization Tips
6. Troubleshooting

Keep it concise but comprehensive, focusing on getting things done efficiently.""",
                'output_format': 'Practical guide with numbered steps and code blocks',
                'model': default_model,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {howto_template.name}'))

        # News Article Template
        news_template, created = ContentTemplate.objects.get_or_create(
            name='News Article Template',
            template_type='news',
            defaults={
                'system_prompt': """You are a DevOps industry analyst who writes engaging news articles about tool updates, industry trends, and technology developments.""",
                'user_prompt_template': """Write a news article about: "{title}"

Topic: {topic}
Key points: {key_points}
Source information: {sources}

Create an informative news article with:
1. Headline & Lead
2. Main Story (what happened and why it matters)
3. Technical Details
4. Industry Perspective
5. Practical Impact
6. Looking Forward

Write in a journalistic style that's informative, engaging, and technically accurate for DevOps professionals. Target 800-1200 words.""",
                'output_format': 'News article format with sections and subheadings',
                'model': default_model,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created template: {news_template.name}'))

        self.stdout.write(self.style.SUCCESS('Content templates created successfully!'))
        
        # Display summary
        total_templates = ContentTemplate.objects.count()
        active_templates = ContentTemplate.objects.filter(is_active=True).count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary:\n'
                f'- {total_templates} content templates available\n'
                f'- {active_templates} active templates ready for use'
            )
        )
