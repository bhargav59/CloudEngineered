"""
Multi-Model AI Orchestrator
Coordinates multiple AI services for optimal content generation
"""
from .openrouter_service import OpenRouterService
from .claude_service import ClaudeService
from .perplexity_service import PerplexityService
import logging

logger = logging.getLogger(__name__)


class MultiModelOrchestrator:
    """Orchestrates multiple AI models for content generation pipeline"""
    
    def __init__(self):
        self.openrouter = OpenRouterService()
        self.claude = ClaudeService()
        self.perplexity = PerplexityService()
    
    def generate_comprehensive_review(self, tool_data):
        """
        Generate a comprehensive tool review using multiple AI models
        
        Pipeline:
        1. Perplexity: Research latest information
        2. GPT-4: Generate initial draft
        3. Claude: Verify technical accuracy and enhance
        
        Args:
            tool_data: Dictionary with tool information
            
        Returns:
            dict: Complete review with metadata
        """
        logger.info(f"Starting comprehensive review generation for {tool_data.get('name')}")
        
        # Step 1: Research with Perplexity
        logger.info("Step 1: Researching with Perplexity")
        research = self.perplexity.research_tool(
            tool_name=tool_data.get('name'),
            tool_category=tool_data.get('category')
        )
        
        if research['success']:
            # Enhance tool_data with research
            tool_data['research'] = research['content']
            tool_data['citations'] = research['citations']
        else:
            logger.warning(f"Perplexity research failed: {research.get('error')}")
            tool_data['research'] = "No additional research available"
            tool_data['citations'] = []
        
        # Step 2: Generate draft with GPT-4
        logger.info("Step 2: Generating draft with GPT-4")
        gpt_prompt = self._build_review_prompt(tool_data, include_research=True)
        
        gpt_response = self.openrouter.generate_content(
            prompt=gpt_prompt,
            model='openai/gpt-4-turbo',
            max_tokens=4096,
            temperature=0.7
        )
        
        if not gpt_response['success']:
            logger.error(f"GPT-4 generation failed: {gpt_response.get('error')}")
            return {
                'success': False,
                'error': 'Failed to generate review draft',
                'content': ''
            }
        
        draft_content = gpt_response['content']
        
        # Step 3: Verify and enhance with Claude
        logger.info("Step 3: Verifying with Claude")
        verification = self.claude.verify_technical_accuracy(
            content=draft_content,
            context=str(tool_data)
        )
        
        if verification['success']:
            # If accuracy score is provided, log it
            logger.info(f"Claude verification complete")
        
        # Step 4: Final polish with Claude if needed
        if verification['success'] and 'suggestions' in verification.get('content', ''):
            logger.info("Step 4: Final polish with Claude")
            polish_prompt = f"""Please improve this review based on the verification feedback:

ORIGINAL REVIEW:
{draft_content}

VERIFICATION FEEDBACK:
{verification['content']}

Please provide an enhanced version that addresses any issues."""

            enhanced = self.claude.generate_content(
                prompt=polish_prompt,
                max_tokens=4096,
                temperature=0.6
            )
            
            if enhanced['success']:
                final_content = enhanced['content']
            else:
                final_content = draft_content
        else:
            final_content = draft_content
        
        # Compile results
        return {
            'success': True,
            'content': final_content,
            'metadata': {
                'research_citations': tool_data.get('citations', []),
                'models_used': ['perplexity', 'gpt-4', 'claude-3.5'],
                'verification_performed': verification['success'],
                'tokens_used': {
                    'gpt4': gpt_response.get('usage', {}),
                    'claude': verification.get('usage', {})
                }
            }
        }
    
    def generate_comparison(self, tool1_data, tool2_data):
        """
        Generate a tool comparison using multiple models
        
        Args:
            tool1_data: First tool data
            tool2_data: Second tool data
            
        Returns:
            dict: Comparison content
        """
        logger.info(f"Generating comparison: {tool1_data.get('name')} vs {tool2_data.get('name')}")
        
        # Research comparison with Perplexity
        research = self.perplexity.research_tool_comparison(
            tool1_name=tool1_data.get('name'),
            tool2_name=tool2_data.get('name')
        )
        
        # Build comparison prompt
        prompt = f"""Generate a comprehensive comparison between {tool1_data.get('name')} and {tool2_data.get('name')}.

TOOL 1: {tool1_data.get('name')}
- Category: {tool1_data.get('category')}
- Description: {tool1_data.get('description')}
- GitHub Stars: {tool1_data.get('github_stars', 'N/A')}

TOOL 2: {tool2_data.get('name')}
- Category: {tool2_data.get('category')}
- Description: {tool2_data.get('description')}
- GitHub Stars: {tool2_data.get('github_stars', 'N/A')}

RESEARCH DATA:
{research.get('content', 'No additional research')}

Create a detailed comparison with:
1. Feature Matrix (side-by-side)
2. Performance Comparison
3. Pricing and Licensing
4. Use Case Recommendations
5. Pros and Cons
6. Migration Considerations
7. Community and Support
8. Final Verdict"""

        # Generate with GPT-4
        response = self.openrouter.generate_content(
            prompt=prompt,
            model='openai/gpt-4-turbo',
            max_tokens=4096,
            temperature=0.7
        )
        
        if response['success']:
            return {
                'success': True,
                'content': response['content'],
                'citations': research.get('citations', []),
                'metadata': {
                    'models_used': ['perplexity', 'gpt-4'],
                    'research_performed': research['success']
                }
            }
        
        return response
    
    def _build_review_prompt(self, tool_data, include_research=True):
        """Build a comprehensive review prompt"""
        research_section = ""
        if include_research and 'research' in tool_data:
            research_section = f"""

RESEARCH DATA:
{tool_data['research']}

Use this research data to ensure accuracy and include current information."""

        return f"""Generate a comprehensive, technically accurate review for:

TOOL: {tool_data.get('name')}
CATEGORY: {tool_data.get('category')}
DESCRIPTION: {tool_data.get('description')}
GITHUB: {tool_data.get('github_url', 'N/A')}
STARS: {tool_data.get('github_stars', 'N/A')}
LANGUAGE: {tool_data.get('primary_language', 'N/A')}
{research_section}

Create a comprehensive review with these sections:

1. Executive Summary (2-3 sentences)
2. Key Features (detailed bullet points)
3. Technical Architecture
4. Installation and Setup
5. Use Cases and Best Practices
6. Performance Analysis
7. Pros and Cons
8. Comparison with Alternatives
9. Community and Support
10. Pricing and Licensing
11. Final Recommendation

Make it informative, technically accurate, and valuable for DevOps engineers making tool decisions."""
