"""
Google Gemini AI Service for CloudEngineered
Replaces OpenRouter with free Gemini API
"""

import logging
import threading
from typing import Dict, List, Optional
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini AI API"""
    
    def __init__(self):
        """Initialize Gemini service"""
        self.api_key = settings.GOOGLE_GEMINI_API_KEY
        
        # Validate API key is present
        if not self.api_key:
            raise ValueError(
                "GOOGLE_GEMINI_API_KEY is not configured. "
                "Please set it in your .env file."
            )
        
        self.model_name = getattr(settings, 'AI_MODEL', 'gemini-2.0-flash')
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise
    
    def generate_content(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict:
        """
        Generate content using Gemini AI
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with 'content', 'model', 'tokens_used', 'cost'
        """
        try:
            # Combine system prompt and user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Generate content
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Extract tokens (Gemini provides token count)
            tokens_used = 0
            if hasattr(response, 'usage_metadata'):
                tokens_used = (
                    response.usage_metadata.prompt_token_count +
                    response.usage_metadata.candidates_token_count
                )
            
            return {
                'content': response.text,
                'model': self.model_name,
                'tokens_used': tokens_used,
                'cost': 0.0,  # Free tier
                'provider': 'Google Gemini',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return {
                'content': None,
                'model': self.model_name,
                'tokens_used': 0,
                'cost': 0.0,
                'provider': 'Google Gemini',
                'success': False,
                'error': str(e)
            }
    
    def generate_tool_review(
        self,
        tool_name: str,
        tool_description: str,
        tool_features: List[str],
        **kwargs
    ) -> Dict:
        """Generate a comprehensive tool review"""
        
        system_prompt = """You are an expert technical writer specializing in DevOps and cloud engineering tools.
Write comprehensive, balanced, and informative tool reviews."""
        
        user_prompt = f"""Write a detailed review of {tool_name}.

Tool Description: {tool_description}

Key Features:
{chr(10).join(f'- {feature}' for feature in tool_features)}

Please provide:
1. Overview (2-3 sentences)
2. Key Features Analysis
3. Pros (3-5 points)
4. Cons (3-5 points)
5. Use Cases
6. Final Verdict

Write in a professional, balanced tone. Be specific and provide examples."""
        
        return self.generate_content(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
    
    def generate_tool_comparison(
        self,
        tool1_name: str,
        tool2_name: str,
        tool1_description: str,
        tool2_description: str,
        **kwargs
    ) -> Dict:
        """Generate a detailed comparison between two tools"""
        
        system_prompt = """You are an expert technical analyst specializing in DevOps tool comparisons.
Provide objective, detailed comparisons that help engineers make informed decisions."""
        
        user_prompt = f"""Create a comprehensive comparison between {tool1_name} and {tool2_name}.

{tool1_name}: {tool1_description}
{tool2_name}: {tool2_description}

Please provide:
1. Executive Summary
2. Feature Comparison (detailed table)
3. Architecture & Design Philosophy
4. Performance Comparison
5. Use Case Scenarios
6. Pricing Analysis
7. Community & Support
8. Recommendation

Be objective, detailed, and provide specific examples."""
        
        return self.generate_content(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000
        )
    
    def generate_blog_article(
        self,
        title: str,
        topic: str,
        keywords: List[str],
        **kwargs
    ) -> Dict:
        """Generate a blog article"""
        
        system_prompt = """You are an expert technical content writer for cloud engineering and DevOps.
Write engaging, informative, and SEO-optimized blog articles."""
        
        user_prompt = f"""Write a comprehensive blog article with the title: "{title}"

Topic: {topic}
Keywords to include: {', '.join(keywords)}

Structure:
1. Introduction (hook the reader)
2. Main Content (3-4 detailed sections)
3. Practical Examples
4. Best Practices
5. Conclusion

Write 1000-1500 words. Make it engaging, informative, and practical."""
        
        return self.generate_content(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2500
        )


# Singleton instance with thread safety
_gemini_service = None
_service_lock = threading.Lock()


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance (thread-safe)"""
    global _gemini_service
    if _gemini_service is None:
        with _service_lock:
            # Double-check pattern
            if _gemini_service is None:
                _gemini_service = GeminiService()
    return _gemini_service
