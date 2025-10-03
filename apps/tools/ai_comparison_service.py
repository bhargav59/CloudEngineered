"""
AI-Powered Tool Comparison Service

This service provides real-time, intelligent tool comparisons using AI models.
Users can request custom comparisons based on their specific needs, and the AI
generates detailed, contextual analysis.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from django.conf import settings
from apps.ai.services import OpenAIService, AIServiceError

logger = logging.getLogger(__name__)


class AIComparisonService:
    """
    Service for generating AI-powered tool comparisons in real-time.
    """
    
    def __init__(self):
        """Initialize the AI comparison service."""
        self.ai_service = OpenAIService()
        self.default_model = getattr(
            settings, 
            'AI_COMPARISON_MODEL', 
            'gpt-4o-mini'  # Don't prefix with 'openai/' - the service will add it
        )
    
    def generate_comparison(self,
                          tool1_data: Dict[str, Any],
                          tool2_data: Dict[str, Any],
                          user_query: str,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive comparison between two tools using AI.
        
        Args:
            tool1_data: Dictionary with tool 1 information
            tool2_data: Dictionary with tool 2 information
            user_query: User's specific comparison question
            context: Additional context (use case, budget, team size, etc.)
            
        Returns:
            Dictionary with structured comparison data
        """
        start_time = time.time()
        
        try:
            # Build the prompts
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(
                tool1_data, 
                tool2_data, 
                user_query, 
                context or {}
            )
            
            # Generate comparison using AI
            response = self.ai_service.generate_content(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.default_model,
                max_tokens=4096,
                temperature=0.7
            )
            
            # Parse and structure the response
            comparison_result = self._parse_response(response)
            
            # Add metadata
            processing_time = time.time() - start_time
            comparison_result['metadata'] = {
                'processing_time': round(processing_time, 2),
                'model_used': self.default_model,
                'tokens_used': response.get('usage', {}).get('total_tokens', 0),
                'timestamp': time.time()
            }
            
            return comparison_result
            
        except Exception as e:
            logger.error(f"Error generating comparison: {str(e)}")
            raise AIServiceError(f"Failed to generate comparison: {str(e)}")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the AI model."""
        return """You are an expert DevOps and Cloud Engineering consultant with deep knowledge of infrastructure tools, CI/CD systems, monitoring solutions, and cloud platforms.

Your role is to provide detailed, unbiased comparisons between tools based on:
- Technical capabilities and features
- Use cases and ideal scenarios
- Performance and scalability
- Learning curve and documentation
- Community support and ecosystem
- Pricing and licensing
- Integration capabilities
- Security considerations
- Real-world deployment patterns

Provide practical, actionable insights that help users make informed decisions. Structure your responses with clear sections and specific examples.

Always be objective, mentioning both strengths and weaknesses of each tool. Consider the user's specific context and requirements when making recommendations."""
    
    def _build_user_prompt(self,
                          tool1: Dict[str, Any],
                          tool2: Dict[str, Any],
                          user_query: str,
                          context: Dict[str, Any]) -> str:
        """Build the user prompt with tool information and context."""
        
        # Extract tool information
        tool1_name = tool1.get('name', 'Tool 1')
        tool1_desc = tool1.get('description', 'No description available')
        tool1_category = tool1.get('category', 'General')
        tool1_tags = ', '.join(tool1.get('tags', []))
        
        tool2_name = tool2.get('name', 'Tool 2')
        tool2_desc = tool2.get('description', 'No description available')
        tool2_category = tool2.get('category', 'General')
        tool2_tags = ', '.join(tool2.get('tags', []))
        
        # Build context information
        context_str = ""
        if context:
            context_items = []
            if context.get('use_case'):
                context_items.append(f"Use Case: {context['use_case']}")
            if context.get('team_size'):
                context_items.append(f"Team Size: {context['team_size']}")
            if context.get('budget'):
                context_items.append(f"Budget: {context['budget']}")
            if context.get('experience_level'):
                context_items.append(f"Experience Level: {context['experience_level']}")
            if context.get('existing_tools'):
                context_items.append(f"Existing Tools: {context['existing_tools']}")
            
            if context_items:
                context_str = "\n\n**User Context:**\n" + "\n".join(f"- {item}" for item in context_items)
        
        prompt = f"""Please provide a comprehensive comparison between these two tools:

**Tool 1: {tool1_name}**
- Category: {tool1_category}
- Description: {tool1_desc}
- Tags: {tool1_tags}

**Tool 2: {tool2_name}**
- Category: {tool2_category}
- Description: {tool2_desc}
- Tags: {tool2_tags}

**User's Question:**
{user_query}{context_str}

Please structure your response as follows:

## Executive Summary
[Brief 2-3 sentence overview of which tool might be better for the user's needs]

## Feature Comparison

### Key Features of {tool1_name}
[List 4-5 key features with brief explanations]

### Key Features of {tool2_name}
[List 4-5 key features with brief explanations]

### Feature Comparison Table
[Create a comparison table of important features]

## Detailed Analysis

### Performance & Scalability
[Compare performance characteristics, scalability limits, resource usage]

### Learning Curve & Documentation
[Compare ease of use, documentation quality, onboarding experience]

### Community & Ecosystem
[Compare community size, plugin ecosystem, third-party integrations]

### Pricing & Licensing
[Compare costs, licensing models, hidden costs]

### Security & Compliance
[Compare security features, compliance certifications, audit capabilities]

## Use Case Scenarios

### When to Choose {tool1_name}
[Specific scenarios where tool 1 is the better choice]

### When to Choose {tool2_name}
[Specific scenarios where tool 2 is the better choice]

## Integration & Migration

### Integration Capabilities
[How each tool integrates with other systems]

### Migration Path
[If switching between tools, what's the migration effort?]

## Real-World Examples
[Brief examples of companies or scenarios using each tool]

## Recommendation
[Based on the user's query and context, provide a specific recommendation with reasoning]

## Key Takeaways
[3-5 bullet points summarizing the most important differences]

---

Make your response practical, specific, and actionable. Use concrete examples where possible."""
        
        return prompt
    
    def _parse_response(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the AI response into structured data."""
        
        content = ai_response.get('content', '')
        
        # Extract sections using markdown headers
        sections = self._extract_sections(content)
        
        return {
            'full_text': content,
            'sections': sections,
            'raw_response': ai_response,
            'success': True
        }
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections from the response."""
        sections = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        
        for line in lines:
            # Check if line is a header
            if line.startswith('##'):
                # Save previous section if exists
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                # Add line to current section
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def generate_quick_comparison(self,
                                 tool1_name: str,
                                 tool2_name: str,
                                 focus_area: str = None) -> Dict[str, Any]:
        """
        Generate a quick comparison summary (shorter, faster).
        
        Args:
            tool1_name: Name of first tool
            tool2_name: Name of second tool
            focus_area: Optional area to focus on (e.g., 'performance', 'pricing')
            
        Returns:
            Quick comparison data
        """
        focus_text = f" focusing on {focus_area}" if focus_area else ""
        
        prompt = f"""Provide a concise comparison between {tool1_name} and {tool2_name}{focus_text}.

Include:
1. Main differences (3-4 points)
2. Quick recommendation (1-2 sentences)
3. One key advantage of each tool

Keep the response under 300 words."""
        
        try:
            response = self.ai_service.generate_content(
                system_prompt="You are a concise DevOps tool expert. Provide brief, actionable comparisons.",
                user_prompt=prompt,
                model=self.default_model,
                max_tokens=500,
                temperature=0.5
            )
            
            return {
                'summary': response.get('content', ''),
                'success': True,
                'type': 'quick'
            }
            
        except Exception as e:
            logger.error(f"Error generating quick comparison: {str(e)}")
            return {
                'summary': 'Unable to generate comparison at this time.',
                'success': False,
                'error': str(e)
            }
    
    def suggest_comparison_questions(self, tool1_name: str, tool2_name: str) -> List[str]:
        """
        Suggest relevant comparison questions for two tools.
        
        Args:
            tool1_name: Name of first tool
            tool2_name: Name of second tool
            
        Returns:
            List of suggested questions
        """
        return [
            f"Which is better for small teams, {tool1_name} or {tool2_name}?",
            f"What are the main differences between {tool1_name} and {tool2_name}?",
            f"How does {tool1_name} compare to {tool2_name} in terms of performance?",
            f"Which has better documentation and community support?",
            f"What's the cost difference between {tool1_name} and {tool2_name}?",
            f"Can I migrate from {tool1_name} to {tool2_name} easily?",
            f"Which tool is better for enterprise use cases?",
            f"How do they compare in terms of learning curve?"
        ]


# Singleton instance
_comparison_service = None

def get_comparison_service() -> AIComparisonService:
    """Get or create the singleton comparison service instance."""
    global _comparison_service
    if _comparison_service is None:
        _comparison_service = AIComparisonService()
    return _comparison_service
