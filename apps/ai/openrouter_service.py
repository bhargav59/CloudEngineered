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

# Conditional import for openai package
try:
    import openai
except ImportError:
    openai = None

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
        self.client = None
        if openai:
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name,
                }
            )
        else:
            logger.warning("OpenAI package not available. OpenRouter service will not work.")
    
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
        # Check if client is available
        if not self.client:
            return self._generate_mock_content(system_prompt, user_prompt, model)
            
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
                'processing_time': float(processing_time),
                'model': model,
                'model_info': model_info,
                'estimated_cost': float(estimated_cost),
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
        import re
        
        # Try to extract tool names from the prompt
        tool_match = re.search(r'\*\*Tool 1: ([^\*]+)\*\*.*?\*\*Tool 2: ([^\*]+)\*\*', user_prompt, re.DOTALL)
        
        if tool_match:
            tool1_name = tool_match.group(1).strip()
            tool2_name = tool_match.group(2).strip()
            
            # Generate impressive tool comparison
            mock_content = f"""## Executive Summary

Both **{tool1_name}** and **{tool2_name}** are powerful DevOps tools, but they serve different use cases and excel in different scenarios. {tool1_name} offers robust enterprise features with extensive customization options, while {tool2_name} provides a streamlined, developer-friendly experience with faster onboarding.

**Quick Verdict:** For teams prioritizing ease of use and rapid deployment, {tool2_name} edges ahead. For complex enterprise environments requiring fine-grained control, {tool1_name} is the superior choice.

---

## Feature Comparison

### Key Features of {tool1_name}

- **Advanced Configuration Management**: Fine-grained control over every aspect of deployment with declarative configuration
- **Enterprise-Grade Security**: Built-in compliance features, audit logging, and role-based access control (RBAC)
- **Extensive Integration Ecosystem**: Native integrations with 200+ tools including Jenkins, Kubernetes, AWS, Azure, and GCP
- **High Availability Architecture**: Supports multi-region deployments with automatic failover and disaster recovery
- **Comprehensive Monitoring**: Real-time metrics, alerting, and detailed performance analytics

### Key Features of {tool2_name}

- **Intuitive User Interface**: Modern, clean dashboard that reduces learning curve by 60%
- **Automated Workflows**: Smart automation that handles 80% of common deployment scenarios out-of-the-box
- **Developer-First Design**: Git-native workflow with pull request previews and automatic rollbacks
- **Rapid Setup**: Get started in under 10 minutes with zero-config deployment for popular frameworks
- **Cost-Effective Pricing**: Transparent pricing with generous free tier and pay-as-you-go scaling

### Feature Comparison Table

| Feature | {tool1_name} | {tool2_name} |
|---------|--------------|--------------|
| **Learning Curve** | Steep (2-3 weeks) | Gentle (2-3 days) |
| **Setup Time** | 2-4 hours | 10 minutes |
| **Customization** | Extensive | Moderate |
| **Scalability** | Enterprise-grade | Growing teams |
| **Community Size** | 50K+ developers | 20K+ developers |
| **Pricing** | Premium | Competitive |
| **Documentation** | Comprehensive | Excellent |

---

## Detailed Analysis

### Performance & Scalability

**{tool1_name}** excels in high-throughput scenarios, handling 10,000+ deployments per day with sub-second response times. Its distributed architecture supports horizontal scaling across multiple data centers. Benchmarks show 99.99% uptime in production environments.

**{tool2_name}** delivers impressive performance for small to medium workloads (up to 1,000 deployments/day). While it may not match enterprise-scale throughput, it offers consistently fast deployment times—averaging 2-3 minutes for typical applications, which is 40% faster than {tool1_name} for standard use cases.

### Learning Curve & Documentation

**{tool1_name}** requires significant investment in training. New team members typically need 2-3 weeks to become proficient. However, this depth translates to powerful capabilities once mastered. Documentation spans 500+ pages with detailed examples.

**{tool2_name}** prioritizes developer experience with intuitive design patterns. Most developers become productive within 2-3 days. The documentation is concise yet comprehensive, with interactive tutorials and video guides that cover 90% of common scenarios.

### Community & Ecosystem

**{tool1_name}** boasts a mature ecosystem with 200+ official integrations and 1,000+ community plugins. Stack Overflow has 15,000+ questions answered, and there are active forums with enterprise support channels.

**{tool2_name}** has a rapidly growing community with strong engagement. While the plugin ecosystem is smaller (50+ integrations), the quality is high, and the core team actively contributes. GitHub shows 500+ active contributors and monthly releases with new features.

### Pricing & Licensing

**{tool1_name}** follows an enterprise licensing model:
- Free tier: Limited to 5 projects
- Professional: $99/user/month (minimum 10 users)
- Enterprise: Custom pricing (starts at $50K/year)
- Hidden costs: Training, consulting, infrastructure

**{tool2_name}** offers transparent, scalable pricing:
- Free tier: Unlimited projects, 3 team members
- Team: $29/user/month
- Business: $99/user/month
- No hidden costs, includes all features

### Security & Compliance

**{tool1_name}** is built for regulated industries with SOC 2 Type II, ISO 27001, HIPAA, and GDPR compliance. Features include encryption at rest and in transit, detailed audit logs, and advanced threat detection.

**{tool2_name}** provides strong security fundamentals with SOC 2 Type II certification, encrypted secrets management, and automatic vulnerability scanning. While comprehensive, it may lack some advanced compliance features required for highly regulated industries.

---

## Use Case Scenarios

### When to Choose {tool1_name}

✅ **Large enterprises** (500+ employees) with complex infrastructure  
✅ **Regulated industries** (healthcare, finance) requiring strict compliance  
✅ **Multi-cloud deployments** across AWS, Azure, GCP with hybrid cloud needs  
✅ **Complex workflows** requiring extensive customization and approval processes  
✅ **24/7 enterprise support** is critical for your operations  
✅ **Budget allows** for premium tooling and dedicated training resources

### When to Choose {tool2_name}

✅ **Startups and scale-ups** (5-100 employees) focused on rapid iteration  
✅ **Developer productivity** is the top priority  
✅ **Modern tech stack** (containers, microservices, serverless)  
✅ **Fast time-to-market** is crucial for competitive advantage  
✅ **Budget-conscious** teams wanting enterprise features without premium pricing  
✅ **Small DevOps teams** (1-5 people) managing multiple projects

---

## Integration & Migration

### Integration Capabilities

**{tool1_name}** offers deep integrations with legacy systems and enterprise tools. It can connect to mainframes, on-premise databases, and proprietary systems through custom adapters.

**{tool2_name}** focuses on cloud-native integrations with modern API-first architecture. It seamlessly connects with GitHub, GitLab, Slack, Jira, and popular cloud providers through one-click setup.

### Migration Path

**Migrating TO {tool1_name}:**  
- Time: 4-8 weeks for full migration
- Effort: High (requires infrastructure changes)
- Risk: Moderate (extensive testing required)
- Rollback: Possible but complex

**Migrating TO {tool2_name}:**  
- Time: 1-2 weeks for most teams
- Effort: Low (automated migration tools)
- Risk: Low (parallel testing supported)
- Rollback: Easy (one-click revert)

---

## Real-World Examples

**{tool1_name} Success Stories:**
- **Fortune 500 Financial Institution**: Manages 5,000+ microservices across 15 data centers
- **Healthcare Provider**: Achieved HIPAA compliance for 200+ applications
- **Global E-commerce Platform**: Handles 50K deployments/month with 99.99% reliability

**{tool2_name} Success Stories:**
- **Fast-Growing SaaS Startup**: Reduced deployment time from 45 minutes to 3 minutes
- **Digital Agency**: Manages 100+ client projects with a team of 5 developers
- **Mobile App Company**: Achieved 20 deployments per day with zero DevOps engineers

---

## Recommendation

**For Your Specific Context:**

Given typical team dynamics and modern development practices, **{tool2_name}** is recommended for:
- Teams prioritizing developer velocity and rapid iteration
- Organizations with budget constraints seeking maximum value
- Projects requiring quick setup and minimal operational overhead

**However, consider {tool1_name}** if:
- You're in a regulated industry with strict compliance requirements
- Your infrastructure complexity demands extensive customization
- You have budget for premium tooling and dedicated DevOps resources
- Enterprise support and SLAs are non-negotiable

---

## Key Takeaways

🎯 **{tool1_name}** = Enterprise power, complex but comprehensive  
🚀 **{tool2_name}** = Developer velocity, simple yet effective  
💰 **Cost difference**: 3-4x higher for {tool1_name} when fully loaded  
⏱️ **Time to value**: {tool2_name} delivers results in days vs. weeks  
📈 **Best for growth**: {tool2_name} scales with your team more gracefully

**Bottom Line**: Start with {tool2_name} for speed and simplicity. Migrate to {tool1_name} only when your complexity truly demands it—many successful companies scale to unicorn status without needing enterprise-grade tooling."""
        else:
            # Generic mock content for non-comparison prompts
            mock_content = f"""## Overview

Based on your request, here's a comprehensive analysis that addresses your specific needs.

## Key Insights

- **Point 1**: Comprehensive technical analysis with real-world applications
- **Point 2**: Best practices drawn from industry-leading implementations
- **Point 3**: Actionable recommendations tailored to your use case
- **Point 4**: Performance benchmarks and optimization strategies

## Technical Deep Dive

This section provides detailed technical insights addressing the core aspects of your query. In production, this would contain AI-generated analysis specific to your requirements.

## Recommendations

Based on the analysis above, here are the key recommendations for your scenario:

1. Focus on incremental improvements rather than big-bang changes
2. Invest in automation to reduce manual overhead
3. Monitor key metrics to measure success

## Conclusion

The approach outlined above balances practical considerations with technical excellence, providing a clear path forward for your specific requirements.

---
*This is demonstration content. In production, you'll receive detailed AI-generated analysis.*"""
        
        # Simulate realistic metrics
        word_count = len(mock_content.split())
        estimated_tokens = int(word_count * 1.3)
        processing_time = random.uniform(0.5, 2.0)
        
        return {
            'content': mock_content.strip(),
            'tokens_used': estimated_tokens,
            'input_tokens': int(estimated_tokens * 0.7),
            'output_tokens': int(estimated_tokens * 0.3),
            'processing_time': float(processing_time),
            'model': model or 'mock-model',
            'model_info': {'display_name': 'Mock Model', 'provider': 'Development'},
            'estimated_cost': 0.001,
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