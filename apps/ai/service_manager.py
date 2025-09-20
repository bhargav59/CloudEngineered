"""
Unified AI Service Manager for CloudEngineered platform.
Provides flexible access to multiple AI providers with automatic fallback.
"""

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

import json
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings

try:
    from apps.ai.openrouter_service import OpenRouterService
except ImportError:
    OpenRouterService = None

logger = logging.getLogger(__name__)


class AIServiceManager:
    """
    Unified AI service that can use OpenRouter, OpenAI, or Anthropic APIs
    with intelligent provider selection and fallback.
    """
    
    def __init__(self):
        """Initialize all available AI services."""
        
        # Initialize OpenRouter (default provider)
        self.openrouter_service = None
        if OpenRouterService and openai:
            try:
                self.openrouter_service = OpenRouterService()
                logger.info("OpenRouter service initialized successfully")
            except Exception as e:
                logger.warning(f"OpenRouter service initialization failed: {e}")
        else:
            logger.warning("OpenRouter service unavailable - missing dependencies")
        
        # Initialize direct OpenAI client if API key is available
        self.openai_client = None
        if openai and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Direct OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Direct OpenAI client initialization failed: {e}")
        
        # Initialize direct Anthropic client if API key is available
        self.anthropic_client = None
        if anthropic and hasattr(settings, 'ANTHROPIC_API_KEY') and settings.ANTHROPIC_API_KEY:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Direct Anthropic client initialized successfully")
            except Exception as e:
                logger.warning(f"Direct Anthropic client initialization failed: {e}")
        
        # Provider priority: Direct APIs first (faster), then OpenRouter
        self.provider_priority = self._determine_provider_priority()
        
    def _determine_provider_priority(self) -> List[str]:
        """Determine provider priority based on available configurations."""
        priority = []
        
        # Direct APIs have priority (faster, no proxy)
        if self.openai_client:
            priority.append('openai_direct')
        if self.anthropic_client:
            priority.append('anthropic_direct')
        
        # OpenRouter as fallback (provides access to multiple models)
        if self.openrouter_service:
            priority.append('openrouter')
        
        logger.info(f"AI provider priority: {priority}")
        return priority
    
    def generate_content(self, 
                        system_prompt: str, 
                        user_prompt: str,
                        content_type: str = "general",
                        preferred_provider: Optional[str] = None,
                        model: Optional[str] = None,
                        max_tokens: int = 2000,
                        temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate content using the best available AI provider.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User input/request
            content_type: Type of content (tool_review, trend_analysis, etc.)
            preferred_provider: Specific provider to use ('openai_direct', 'anthropic_direct', 'openrouter')
            model: Specific model to use (if using OpenRouter)
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            
        Returns:
            Dictionary with generated content and metadata
        """
        
        # Determine which providers to try
        providers_to_try = []
        
        if preferred_provider:
            if preferred_provider in self.provider_priority:
                providers_to_try = [preferred_provider]
            else:
                logger.warning(f"Preferred provider {preferred_provider} not available, using fallback")
                providers_to_try = self.provider_priority
        else:
            providers_to_try = self.provider_priority
        
        last_error = None
        
        for provider in providers_to_try:
            try:
                logger.info(f"Attempting content generation with {provider}")
                
                if provider == 'openai_direct':
                    return self._generate_with_openai_direct(
                        system_prompt, user_prompt, max_tokens, temperature
                    )
                elif provider == 'anthropic_direct':
                    return self._generate_with_anthropic_direct(
                        system_prompt, user_prompt, max_tokens, temperature
                    )
                elif provider == 'openrouter':
                    return self._generate_with_openrouter(
                        system_prompt, user_prompt, content_type, model, max_tokens, temperature
                    )
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider} failed: {str(e)}")
                continue
        
        # If all providers failed, provide mock content
        if last_error:
            logger.warning(f"All AI providers failed. Last error: {str(last_error)}. Using mock content.")
            return self._generate_mock_content(system_prompt, user_prompt, content_type)
        else:
            logger.warning("No AI providers available. Using mock content.")
            return self._generate_mock_content(system_prompt, user_prompt, content_type)
    
    def _generate_with_openai_direct(self, 
                                   system_prompt: str, 
                                   user_prompt: str,
                                   max_tokens: int, 
                                   temperature: float) -> Dict[str, Any]:
        """Generate content using direct OpenAI API."""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Use cost-effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return {
            "success": True,
            "content": response.choices[0].message.content,
            "provider": "openai_direct",
            "model": "gpt-4o-mini",
            "tokens_used": response.usage.total_tokens,
            "cost_estimate": None  # OpenAI doesn't provide cost in response
        }
    
    def _generate_with_anthropic_direct(self, 
                                      system_prompt: str, 
                                      user_prompt: str,
                                      max_tokens: int, 
                                      temperature: float) -> Dict[str, Any]:
        """Generate content using direct Anthropic API."""
        
        response = self.anthropic_client.messages.create(
            model="claude-3-haiku-20240307",  # Use cost-effective model
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return {
            "success": True,
            "content": response.content[0].text,
            "provider": "anthropic_direct", 
            "model": "claude-3-haiku-20240307",
            "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            "cost_estimate": None  # Anthropic doesn't provide cost in response
        }
    
    def _generate_with_openrouter(self, 
                                system_prompt: str, 
                                user_prompt: str,
                                content_type: str,
                                model: Optional[str],
                                max_tokens: int, 
                                temperature: float) -> Dict[str, Any]:
        """Generate content using OpenRouter service."""
        
        # Use OpenRouter's built-in model selection if no specific model requested
        if not model:
            model = self._get_best_model_for_content_type(content_type)
        
        result = self.openrouter_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            use_fallback=True  # Allow OpenRouter to try fallback models
        )
        
        return {
            "success": True,
            "content": result["content"],
            "provider": "openrouter",
            "model": result["model"],
            "tokens_used": result.get("tokens_used"),
            "cost_estimate": result.get("estimated_cost")
        }
    
    def _get_best_model_for_content_type(self, content_type: str) -> str:
        """Get the best OpenRouter model for a specific content type."""
        
        model_recommendations = {
            'tool_review': 'openai/gpt-4o-mini',  # Fast and cost-effective
            'trend_analysis': 'anthropic/claude-3-haiku',  # Good analytical capabilities
            'how_to_guide': 'openai/gpt-4o-mini',  # Clear step-by-step instructions
            'comparison': 'anthropic/claude-3-sonnet',  # Better reasoning
            'general': 'openai/gpt-4o-mini'  # Default choice
        }
        
        return model_recommendations.get(content_type, 'openai/gpt-4o-mini')
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get status of all AI providers."""
        return {
            'openai_direct': self.openai_client is not None,
            'anthropic_direct': self.anthropic_client is not None,
            'openrouter': self.openrouter_service is not None
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get detailed information about available providers."""
        return {
            'priority': self.provider_priority,
            'available': self.get_available_providers(),
            'openrouter_models': list(self.openrouter_service.MODELS.keys()) if self.openrouter_service else [],
            'config_status': {
                'openai_api_key': bool(getattr(settings, 'OPENAI_API_KEY', None)),
                'anthropic_api_key': bool(getattr(settings, 'ANTHROPIC_API_KEY', None)),
                'openrouter_api_key': bool(getattr(settings, 'OPENROUTER_API_KEY', None))
            }
        }
    
    def _generate_mock_content(self, system_prompt: str, user_prompt: str, content_type: str) -> Dict[str, Any]:
        """Generate mock content when AI services are unavailable."""
        
        mock_content_templates = {
            'tool_review': """
            ## Tool Overview
            This is a comprehensive analysis of a development tool based on community feedback and documentation review.
            
            ## Key Features
            - Feature 1: Core functionality that addresses primary use cases
            - Feature 2: Advanced capabilities for power users
            - Feature 3: Integration options with popular workflows
            
            ## Pros
            ✅ User-friendly interface and documentation
            ✅ Strong community support and active development
            ✅ Good performance and reliability
            
            ## Cons
            ❌ Learning curve for advanced features
            ❌ Some limitations in complex scenarios
            ❌ Pricing may be a consideration for small teams
            
            ## Conclusion
            This tool offers solid value for development teams looking to improve their workflow efficiency. 
            Consider your specific requirements and team size when evaluating.
            """,
            
            'trend_analysis': """
            ## Current Trends Analysis
            
            Based on industry observations and community discussions, here are the key trends:
            
            ### Emerging Technologies
            - Cloud-native solutions continue to gain adoption
            - Developer experience improvements are prioritized
            - Security integration becomes more seamless
            
            ### Market Dynamics
            - Increased focus on automation and efficiency
            - Growing importance of collaboration features
            - Cost optimization remains a key consideration
            
            ### Future Outlook
            The landscape continues to evolve with new innovations addressing developer productivity and operational efficiency.
            """,
            
            'general': """
            ## Analysis Summary
            
            This analysis provides insights into the requested topic based on available information and industry best practices.
            
            ### Key Points
            - Important consideration 1
            - Relevant factor 2
            - Strategic recommendation 3
            
            ### Recommendations
            Based on the analysis, we recommend evaluating options carefully and considering long-term implications.
            """
        }
        
        # Get appropriate template
        template = mock_content_templates.get(content_type, mock_content_templates['general'])
        
        return {
            "success": True,
            "content": template.strip(),
            "provider": "mock",
            "model": "mock-content-generator",
            "tokens_used": len(template.split()),
            "cost_estimate": 0.0,
            "is_mock": True,
            "note": "This is mock content generated due to unavailable AI services. Install openai package and configure API keys for real AI generation."
        }