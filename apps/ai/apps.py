"""
AI Integration App for CloudEngineered

This app handles all AI-powered features including:
- Content generation using OpenAI GPT-4
- Tool analysis and review generation
- SEO optimization
- Content quality assurance
- Automated writing workflows
"""

from django.apps import AppConfig


class AiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai'
    verbose_name = 'AI Integration'
