"""
Anthropic Claude API Integration Service
"""
import anthropic
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Anthropic Claude API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ANTHROPIC_API_KEY', None)
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not configured")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude 3.5 Sonnet
    
    def generate_content(self, prompt, system_prompt=None, max_tokens=4096, temperature=0.7):
        """
        Generate content using Claude
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0-1)
            
        Returns:
            dict: Response with content and metadata
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Claude API not configured',
                'content': ''
            }
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = self.client.messages.create(**kwargs)
            
            # Extract text content
            content = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
            
            return {
                'success': True,
                'content': content,
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                },
                'stop_reason': response.stop_reason
            }
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            return {
                'success': False,
                'error': f"API Error: {str(e)}",
                'content': ''
            }
        except Exception as e:
            logger.error(f"Claude service error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': ''
            }
    
    def generate_tool_review(self, tool_data, review_type='comprehensive'):
        """
        Generate a tool review using Claude
        
        Args:
            tool_data: Dictionary with tool information
            review_type: Type of review (comprehensive, quick, comparison)
            
        Returns:
            dict: Generated review content
        """
        system_prompt = """You are a senior DevOps engineer and technical writer with 10+ years of experience 
reviewing cloud engineering and DevOps tools. Your reviews are known for being:
- Technically accurate and detailed
- Balanced and unbiased
- Practical with real-world use cases
- Well-structured with clear sections
- Focused on helping engineers make informed decisions"""

        prompt = f"""Generate a {review_type} review for the following tool:

Tool Name: {tool_data.get('name', 'Unknown')}
Category: {tool_data.get('category', 'Unknown')}
Description: {tool_data.get('description', 'No description')}
GitHub URL: {tool_data.get('github_url', 'N/A')}
Stars: {tool_data.get('github_stars', 'N/A')}
Primary Language: {tool_data.get('primary_language', 'N/A')}

Please generate a comprehensive review covering:
1. Executive Summary (2-3 sentences)
2. Key Features (bullet points)
3. Technical Architecture
4. Use Cases and Best Fit
5. Pros and Cons
6. Performance Considerations
7. Community and Support
8. Pricing and Licensing
9. Comparison with Alternatives
10. Final Recommendation

Make it informative, technically accurate, and helpful for DevOps engineers."""

        return self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4096,
            temperature=0.7
        )
    
    def verify_technical_accuracy(self, content, context):
        """
        Verify technical accuracy of generated content
        
        Args:
            content: Content to verify
            context: Context information (tool details, etc.)
            
        Returns:
            dict: Verification results and suggestions
        """
        system_prompt = """You are a technical accuracy reviewer for DevOps and cloud engineering content.
Your job is to identify technical inaccuracies, outdated information, and suggest improvements."""

        prompt = f"""Review the following content for technical accuracy:

CONTENT:
{content}

CONTEXT:
{context}

Please provide:
1. Overall accuracy score (1-10)
2. List of any inaccuracies or questionable statements
3. Suggestions for improvement
4. Updated information if needed"""

        return self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.3  # Lower temperature for accuracy checks
        )
