"""
OpenRouter API Service for CloudEngineered

This module provides a service for integrating with OpenRouter API,
which gives access to multiple AI models from different providers
at competitive prices.
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.conf import settings
import openai

logger = logging.getLogger(__name__)


class OpenRouterService:
    """
    OpenRouter API service that provides access to multiple AI models
    through a single interface at competitive pricing.
    """
    
    # Popular OpenRouter models with their costs (per 1M tokens)
    MODELS = {
        # OpenAI Models
        'openai/gpt-4o': {
            'display_name': 'GPT-4o',
            'provider': 'OpenAI',
            'max_tokens': 128000,
            'input_cost': 2.50,  # per 1M tokens
            'output_cost': 10.00,
            'description': 'Latest GPT-4 Omni model with vision capabilities'
        },
        'openai/gpt-4o-mini': {
            'display_name': 'GPT-4o Mini',
            'provider': 'OpenAI', 
            'max_tokens': 128000,
            'input_cost': 0.15,
            'output_cost': 0.60,
            'description': 'Smaller, faster version of GPT-4o'
        },
        'openai/gpt-3.5-turbo': {
            'display_name': 'GPT-3.5 Turbo',
            'provider': 'OpenAI',
            'max_tokens': 16384,
            'input_cost': 0.50,
            'output_cost': 1.50,
            'description': 'Fast and efficient model for most tasks'
        },
        
        # Anthropic Models
        'anthropic/claude-3.5-sonnet': {
            'display_name': 'Claude 3.5 Sonnet',
            'provider': 'Anthropic',
            'max_tokens': 200000,
            'input_cost': 3.00,
            'output_cost': 15.00,
            'description': 'Most capable Claude model with advanced reasoning'
        },
        'anthropic/claude-3-haiku': {
            'display_name': 'Claude 3 Haiku',
            'provider': 'Anthropic',
            'max_tokens': 200000,
            'input_cost': 0.25,
            'output_cost': 1.25,
            'description': 'Fast and cost-effective Claude model'
        },
        
        # Meta Models
        'meta-llama/llama-3.1-8b-instruct': {
            'display_name': 'Llama 3.1 8B',
            'provider': 'Meta',
            'max_tokens': 32768,
            'input_cost': 0.18,
            'output_cost': 0.18,
            'description': 'Open source model with good performance'
        },
        'meta-llama/llama-3.1-70b-instruct': {
            'display_name': 'Llama 3.1 70B',
            'provider': 'Meta',
            'max_tokens': 32768,
            'input_cost': 0.90,
            'output_cost': 0.90,
            'description': 'Large open source model with excellent capabilities'
        },
        
        # Mistral Models
        'mistralai/mistral-7b-instruct': {
            'display_name': 'Mistral 7B',
            'provider': 'Mistral AI',
            'max_tokens': 32768,
            'input_cost': 0.20,
            'output_cost': 0.20,
            'description': 'Efficient European model for various tasks'
        },
        
        # Google Models
        'google/gemini-pro': {
            'display_name': 'Gemini Pro',
            'provider': 'Google',
            'max_tokens': 32768,
            'input_cost': 0.50,
            'output_cost': 1.50,
            'description': 'Google\'s multimodal AI model'
        }
    }
    
    # Default fallback chain for content generation
    DEFAULT_MODEL_FALLBACK = [
        'openai/gpt-4o-mini',      # Primary: Fast and cost-effective
        'anthropic/claude-3-haiku',  # Secondary: Alternative provider
        'meta-llama/llama-3.1-8b-instruct',  # Tertiary: Open source fallback
    ]
    
    def __init__(self):
        """Initialize OpenRouter service"""
        self.api_key = self._get_api_key()
        self.site_url = getattr(settings, 'SITE_URL', 'https://cloudengineered.com')
        self.app_name = getattr(settings, 'OPENROUTER_APP_NAME', 'CloudEngineered')
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": self.site_url,
                "X-Title": self.app_name,
            }
        )
    
    def _get_api_key(self) -> str:
        """Get OpenRouter API key from environment or settings"""
        api_key = os.getenv('OPENROUTER_API_KEY') or getattr(settings, 'OPENROUTER_API_KEY', None)
        
        if not api_key:
            # For development, allow fallback to mock mode
            if settings.DEBUG:
                logger.warning("OpenRouter API key not found. Using mock mode for development.")
                return "mock-api-key"
            else:
                raise ValueError(
                    "OpenRouter API key not found. Please set OPENROUTER_API_KEY "
                    "environment variable or in Django settings."
                )
        
        return api_key
    
    def generate_content(self, 
                        system_prompt: str,
                        user_prompt: str,
                        model: str = None,
                        max_tokens: int = 4096,
                        temperature: float = 0.7,
                        use_fallback: bool = True) -> Dict[str, Any]:
        """
        Generate content using OpenRouter API
        
        Args:
            system_prompt: System prompt for the AI model
            user_prompt: User prompt with specific request
            model: Model name (if None, uses default fallback chain)
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0.0 to 1.0)
            use_fallback: Whether to try fallback models on failure
            
        Returns:
            Dictionary with generated content and metadata
        """
        if self.api_key == "mock-api-key":
            return self._generate_mock_content(system_prompt, user_prompt, model)
        
        models_to_try = [model] if model else self.DEFAULT_MODEL_FALLBACK.copy()
        
        for attempt_model in models_to_try:
            try:
                return self._attempt_generation(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=attempt_model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            except Exception as e:
                logger.warning(f"Model {attempt_model} failed: {str(e)}")
                if not use_fallback or attempt_model == models_to_try[-1]:
                    # If this is the last model or fallback is disabled, raise the error
                    if model:  # User specified a specific model
                        raise Exception(f"Failed to generate content with {model}: {str(e)}")
                    else:
                        raise Exception(f"All fallback models failed. Last error: {str(e)}")
                continue
        
        raise Exception("No models available for content generation")
    
    def _attempt_generation(self, 
                           system_prompt: str,
                           user_prompt: str, 
                           model: str,
                           max_tokens: int,
                           temperature: float) -> Dict[str, Any]:
        """Attempt content generation with a specific model"""
        start_time = time.time()
        
        # Adjust max_tokens based on model capabilities
        model_info = self.MODELS.get(model, {})
        model_max_tokens = model_info.get('max_tokens', 4096)
        actual_max_tokens = min(max_tokens, model_max_tokens)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=actual_max_tokens,
                temperature=temperature
            )
            
            processing_time = time.time() - start_time
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            estimated_cost = self._calculate_cost(model, input_tokens, output_tokens)
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': total_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'processing_time': processing_time,
                'model': model,
                'model_info': model_info,
                'estimated_cost': estimated_cost,
                'usage': {
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens,
                    'total_tokens': total_tokens
                },
                'raw_response': response.model_dump()
            }
            
        except Exception as e:
            logger.error(f"OpenRouter API error for model {model}: {str(e)}")
            raise
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate estimated cost for token usage"""
        model_info = self.MODELS.get(model, {})
        
        if not model_info:
            # Default cost if model not in our list
            input_cost_per_1m = 1.0
            output_cost_per_1m = 2.0
        else:
            input_cost_per_1m = model_info['input_cost']
            output_cost_per_1m = model_info['output_cost']
        
        # Calculate cost (prices are per 1M tokens)
        input_cost = Decimal(input_tokens) * Decimal(input_cost_per_1m) / Decimal(1_000_000)
        output_cost = Decimal(output_tokens) * Decimal(output_cost_per_1m) / Decimal(1_000_000)
        
        return input_cost + output_cost
    
    def _generate_mock_content(self, system_prompt: str, user_prompt: str, model: str = None) -> Dict[str, Any]:
        """Generate mock content for development/testing"""
        import random
        
        # Extract key information from prompts
        content_length = random.choice([500, 1000, 1500, 2000])
        
        mock_content = f"""
# Generated Content (Mock Mode)

This is mock-generated content for development purposes.

## Overview
Based on your request: {user_prompt[:100]}...

## Key Points
- Point 1: Comprehensive analysis of the topic
- Point 2: Detailed technical insights
- Point 3: Best practices and recommendations
- Point 4: Real-world applications and use cases

## Technical Details
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

## Conclusion
This mock content demonstrates the expected format and structure. In production, this would be generated using the actual AI model.

---
*Generated in mock mode for development testing.*
"""
        
        # Simulate realistic metrics
        word_count = len(mock_content.split())
        estimated_tokens = int(word_count * 1.3)
        processing_time = random.uniform(0.5, 2.0)
        
        return {
            'content': mock_content.strip(),
            'tokens_used': estimated_tokens,
            'input_tokens': int(estimated_tokens * 0.7),
            'output_tokens': int(estimated_tokens * 0.3),
            'processing_time': processing_time,
            'model': model or 'mock-model',
            'model_info': {'display_name': 'Mock Model', 'provider': 'Development'},
            'estimated_cost': Decimal('0.001'),
            'usage': {
                'prompt_tokens': int(estimated_tokens * 0.7),
                'completion_tokens': int(estimated_tokens * 0.3),
                'total_tokens': estimated_tokens
            },
            'raw_response': {'mock': True}
        }
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with their information"""
        return [
            {
                'id': model_id,
                'display_name': info['display_name'],
                'provider': info['provider'],
                'max_tokens': info['max_tokens'],
                'input_cost_per_1m': info['input_cost'],
                'output_cost_per_1m': info['output_cost'],
                'description': info['description']
            }
            for model_id, info in self.MODELS.items()
        ]
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        return self.MODELS.get(model, {})
    
    def get_recommended_model(self, task_type: str = 'general') -> str:
        """
        Get recommended model for different task types
        
        Args:
            task_type: Type of task ('general', 'creative', 'technical', 'budget')
            
        Returns:
            Recommended model ID
        """
        recommendations = {
            'general': 'openai/gpt-4o-mini',
            'creative': 'anthropic/claude-3.5-sonnet', 
            'technical': 'openai/gpt-4o',
            'budget': 'meta-llama/llama-3.1-8b-instruct',
            'fast': 'openai/gpt-3.5-turbo',
            'long_context': 'anthropic/claude-3-haiku'
        }
        
        return recommendations.get(task_type, 'openai/gpt-4o-mini')


# Singleton instance for easy access
_openrouter_service = None

def get_openrouter_service() -> OpenRouterService:
    """Get singleton OpenRouter service instance"""
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService()
    return _openrouter_service