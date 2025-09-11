"""
AI Services for Content Generation

This module provides services for AI-powered content generation,
including OpenAI GPT-4 integration and content quality assessment.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import AIProvider, AIModel, ContentTemplate, ContentGeneration, ContentQuality

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class OpenAIService:
    """OpenAI GPT integration service"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise AIServiceError("OpenAI API key not found in environment variables")
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise AIServiceError("openai package not installed. Run: pip install openai")
    
    def generate_content(self, 
                        system_prompt: str, 
                        user_prompt: str, 
                        model: str = "gpt-4", 
                        max_tokens: int = 4096,
                        temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate content using OpenAI GPT models
        
        Args:
            system_prompt: System prompt for the AI model
            user_prompt: User prompt with specific request
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 to 1.0)
            
        Returns:
            Dictionary with generated content and metadata
        """
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'processing_time': processing_time,
                'model': model,
                'raw_response': response.model_dump()
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise AIServiceError(f"OpenAI generation failed: {str(e)}")


class ContentGenerator:
    """High-level content generation service"""
    
    def __init__(self):
        self.openai_service = None
        
    def _init_openai_service(self):
        """Initialize OpenAI service only when needed"""
        if self.openai_service is None:
            try:
                self.openai_service = OpenAIService()
            except AIServiceError as e:
                logger.warning(f"OpenAI service initialization failed: {e}")
                self.openai_service = False
        return self.openai_service
    
    def generate_content(self, 
                        template: ContentTemplate, 
                        input_data: Dict[str, Any], 
                        user: Any = None,
                        mock: bool = False) -> Dict[str, Any]:
        """
        Generate content using AI templates (new interface)
        
        Args:
            template: ContentTemplate instance
            input_data: Dictionary containing input variables
            user: User who initiated the generation
            mock: If True, generate mock content instead of real AI content
            
        Returns:
            Dictionary containing generated content and metadata
        """
        start_time = time.time()
        
        if mock:
            return self._generate_mock_content(template, input_data)
        
        # Initialize OpenAI service
        openai_service = self._init_openai_service()
        if not openai_service:
            # Fall back to mock if OpenAI is not available
            logger.warning("OpenAI service not available, falling back to mock mode")
            return self._generate_mock_content(template, input_data)
        
        try:
            # Format the prompts with input data
            formatted_system_prompt = self._format_prompt(template.system_prompt, input_data)
            formatted_user_prompt = self._format_prompt(template.user_prompt_template, input_data)
            
            # Get AI model configuration
            ai_model = template.model
            
            # Generate content using OpenAI
            result = openai_service.generate_content(
                system_prompt=formatted_system_prompt,
                user_prompt=formatted_user_prompt,
                model=ai_model.name,
                max_tokens=ai_model.max_tokens,
                temperature=0.7
            )
            
            processing_time = time.time() - start_time
            
            # Calculate cost estimate
            input_tokens = result['usage']['prompt_tokens']
            output_tokens = result['usage']['completion_tokens']
            total_tokens = result['usage']['total_tokens']
            
            cost = self._calculate_cost(ai_model, input_tokens, output_tokens)
            
            return {
                'content': result['content'],
                'tokens_used': total_tokens,
                'cost': cost,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise AIServiceError(f"Content generation failed: {str(e)}")
    
    def _generate_mock_content(self, template: ContentTemplate, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock content for testing purposes"""
        import random
        
        tool_name = input_data.get('tool_name', 'Sample Tool')
        category = input_data.get('category', 'Development')
        
        if template.template_type == 'tool_review':
            content = f"""
# {tool_name} Review

## Overview
{tool_name} is a powerful tool in the {category} category that offers comprehensive solutions for modern development workflows.

## Key Features
- Feature 1: Advanced functionality for enhanced productivity
- Feature 2: Seamless integration with popular development tools
- Feature 3: User-friendly interface with intuitive design
- Feature 4: Robust performance and reliability

## Pros
✅ Easy to use and learn
✅ Great community support
✅ Regular updates and improvements
✅ Excellent documentation

## Cons
❌ May have a learning curve for beginners
❌ Some advanced features require premium subscription
❌ Limited offline functionality

## Use Cases
- Web development projects
- Mobile application development
- DevOps and CI/CD pipelines
- Team collaboration and project management

## Pricing
{input_data.get('pricing', 'Various pricing options available')}

## Conclusion
{tool_name} is a solid choice for developers looking for a reliable tool in the {category} space. While it has some limitations, its benefits far outweigh the drawbacks.

**Rating: 4.2/5 stars**
"""
        elif template.template_type == 'tutorial':
            content = f"""
# Getting Started with {tool_name}

## Introduction
This tutorial will guide you through the basics of using {tool_name} for your {category} projects.

## Prerequisites
- Basic knowledge of software development
- A computer with internet access
- Text editor or IDE

## Step 1: Installation
Instructions for installing {tool_name}...

## Step 2: Configuration
How to configure {tool_name} for your needs...

## Step 3: First Project
Creating your first project with {tool_name}...

## Conclusion
You've successfully learned the basics of {tool_name}!
"""
        else:
            content = f"""
# {tool_name} - {template.get_template_type_display()}

This is a mock-generated piece of content for {tool_name} in the {category} category.

## Content Details
- Tool: {tool_name}
- Category: {category}
- Template Type: {template.template_type}
- Generated: Mock mode

## Description
{input_data.get('tool_description', 'A comprehensive tool for modern development needs.')}

This content is generated in mock mode for testing purposes.
"""
        
        # Simulate realistic metrics
        word_count = len(content.split())
        estimated_tokens = word_count * 1.3  # Rough estimate
        estimated_cost = random.uniform(0.01, 0.05)
        processing_time = random.uniform(1.0, 3.0)
        
        return {
            'content': content.strip(),
            'tokens_used': int(estimated_tokens),
            'cost': round(estimated_cost, 4),
            'processing_time': round(processing_time, 2)
        }
    
    def _format_prompt(self, prompt_template: str, input_data: Dict[str, Any]) -> str:
        """Format prompt template with input data"""
        try:
            return prompt_template.format(**input_data)
        except KeyError as e:
            logger.warning(f"Missing template variable {e}, using placeholder")
            # Replace missing variables with placeholders
            import re
            formatted = prompt_template
            for match in re.finditer(r'\{(\w+)\}', prompt_template):
                var_name = match.group(1)
                if var_name not in input_data:
                    formatted = formatted.replace(f'{{{var_name}}}', f'[{var_name}]')
            return formatted
        except Exception as e:
            logger.error(f"Prompt formatting failed: {str(e)}")
            return prompt_template
    
    def generate_from_template(self, 
                              template_id: int, 
                              input_data: Dict[str, Any],
                              user_id: Optional[int] = None) -> ContentGeneration:
        """
        Generate content using a predefined template
        
        Args:
            template_id: ID of the ContentTemplate to use
            input_data: Dictionary of input parameters for the template
            user_id: ID of the user initiating the generation
            
        Returns:
            ContentGeneration instance with the generated content
        """
        try:
            template = ContentTemplate.objects.get(id=template_id, is_active=True)
        except ContentTemplate.DoesNotExist:
            raise AIServiceError(f"Template with ID {template_id} not found or inactive")
        
        # Create generation record
        generation = ContentGeneration.objects.create(
            template=template,
            initiated_by_id=user_id,
            input_data=input_data,
            status='processing'
        )
        
        try:
            # Render the prompt template with input data
            rendered_prompt = self._render_prompt_template(template.user_prompt_template, input_data)
            generation.generated_prompt = rendered_prompt
            generation.save()
            
            # Generate content using AI service
            ai_response = self.openai_service.generate_content(
                system_prompt=template.system_prompt,
                user_prompt=rendered_prompt,
                model=template.model.name,
                max_tokens=template.model.max_tokens
            )
            
            # Update generation record with results
            generation.generated_content = ai_response['content']
            generation.raw_response = ai_response['raw_response']
            generation.tokens_used = ai_response['tokens_used']
            generation.processing_time = ai_response['processing_time']
            generation.estimated_cost = self._calculate_cost(
                template.model,
                ai_response['input_tokens'],
                ai_response['output_tokens']
            )
            generation.mark_completed()
            
            # Create quality assessment
            self._assess_content_quality(generation)
            
            logger.info(f"Successfully generated content for template {template.name}")
            return generation
            
        except Exception as e:
            generation.mark_failed(str(e))
            logger.error(f"Content generation failed: {str(e)}")
            raise AIServiceError(f"Content generation failed: {str(e)}")
    
    def _render_prompt_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render prompt template with input data"""
        try:
            return template.format(**data)
        except KeyError as e:
            raise AIServiceError(f"Missing required template variable: {e}")
        except Exception as e:
            raise AIServiceError(f"Template rendering failed: {str(e)}")
    
    def _calculate_cost(self, model: AIModel, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate estimated cost for token usage"""
        input_cost = (Decimal(input_tokens) / 1000) * model.cost_per_1k_input_tokens
        output_cost = (Decimal(output_tokens) / 1000) * model.cost_per_1k_output_tokens
        return input_cost + output_cost
    
    def _assess_content_quality(self, generation: ContentGeneration) -> ContentQuality:
        """Assess quality of generated content"""
        content = generation.generated_content
        
        # Basic content analysis
        word_count = len(content.split())
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        has_headings = any(line.startswith('#') or line.startswith('##') for line in content.split('\n'))
        has_links = '[' in content and '](' in content
        has_lists = any(line.strip().startswith(('-', '*', '1.')) for line in content.split('\n'))
        
        # Calculate readability score (simple implementation)
        readability_score = self._calculate_readability_score(content)
        
        quality = ContentQuality.objects.create(
            generation=generation,
            word_count=word_count,
            paragraph_count=paragraph_count,
            has_headings=has_headings,
            has_links=has_links,
            has_lists=has_lists,
            readability_score=readability_score,
            requires_human_review=self._requires_human_review(content, word_count)
        )
        
        return quality
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate simple readability score (Flesch Reading Ease approximation)"""
        words = len(content.split())
        sentences = content.count('.') + content.count('!') + content.count('?')
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        # Simplified calculation - in production, use proper readability libraries
        score = 206.835 - (1.015 * avg_sentence_length)
        return max(0.0, min(100.0, score))
    
    def _requires_human_review(self, content: str, word_count: int) -> bool:
        """Determine if content requires human review"""
        # Simple heuristics - can be enhanced with more sophisticated analysis
        if word_count < 200:  # Too short
            return True
        if word_count > 5000:  # Too long
            return True
        if content.count('TODO') > 0 or content.count('FIXME') > 0:
            return True
        return False


class ToolAnalyzer:
    """Service for analyzing tools and generating insights"""
    
    def __init__(self):
        self.content_generator = ContentGenerator()
    
    def analyze_github_repository(self, github_url: str) -> Dict[str, Any]:
        """
        Analyze a GitHub repository and extract tool information
        
        Args:
            github_url: URL of the GitHub repository
            
        Returns:
            Dictionary with tool analysis data
        """
        # In a real implementation, this would:
        # 1. Fetch repository data using GitHub API
        # 2. Analyze README, documentation, code structure
        # 3. Extract features, technologies used, etc.
        # 4. Generate insights using AI
        
        # Placeholder implementation
        repo_name = github_url.split('/')[-1]
        return {
            'name': repo_name,
            'description': f"Analysis of {repo_name}",
            'technologies': [],
            'features': [],
            'use_cases': [],
            'github_url': github_url
        }
    
    def generate_tool_review(self, tool_data: Dict[str, Any], user_id: Optional[int] = None) -> ContentGeneration:
        """
        Generate a comprehensive tool review
        
        Args:
            tool_data: Dictionary with tool information
            user_id: ID of the user requesting the review
            
        Returns:
            ContentGeneration instance with the generated review
        """
        # Get tool review template
        try:
            template = ContentTemplate.objects.get(template_type='tool_review', is_active=True)
        except ContentTemplate.DoesNotExist:
            raise AIServiceError("No active tool review template found")
        
        return self.content_generator.generate_from_template(
            template_id=template.id,
            input_data=tool_data,
            user_id=user_id
        )


# Convenience functions for common operations
def generate_tool_review(tool_name: str, tool_description: str, features: List[str], **kwargs) -> ContentGeneration:
    """Generate a tool review with basic information"""
    analyzer = ToolAnalyzer()
    tool_data = {
        'tool_name': tool_name,
        'tool_description': tool_description,
        'features': ', '.join(features),
        **kwargs
    }
    return analyzer.generate_tool_review(tool_data)


def generate_content_from_template(template_id: int, **template_vars) -> ContentGeneration:
    """Generate content using a template with provided variables"""
    generator = ContentGenerator()
    return generator.generate_from_template(template_id, template_vars)
