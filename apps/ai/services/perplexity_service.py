"""
Perplexity AI Integration Service
"""
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PerplexityService:
    """Service for interacting with Perplexity AI API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'PERPLEXITY_API_KEY', None)
        if not self.api_key:
            logger.warning("PERPLEXITY_API_KEY not configured")
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"  # Real-time research model
    
    def search_and_summarize(self, query, max_tokens=2048):
        """
        Search the web and provide a comprehensive summary
        
        Args:
            query: Search query
            max_tokens: Maximum tokens in response
            
        Returns:
            dict: Search results and summary
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Perplexity API not configured',
                'content': '',
                'citations': []
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a research assistant helping to gather accurate, up-to-date information about DevOps and cloud engineering tools."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.2,  # Lower for factual research
                "return_citations": True,
                "return_images": False
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract content and citations
            content = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            return {
                'success': True,
                'content': content,
                'citations': citations,
                'model': data['model'],
                'usage': data.get('usage', {})
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Perplexity API request error: {str(e)}")
            return {
                'success': False,
                'error': f"API Request Error: {str(e)}",
                'content': '',
                'citations': []
            }
        except Exception as e:
            logger.error(f"Perplexity service error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'content': '',
                'citations': []
            }
    
    def research_tool(self, tool_name, tool_category=None):
        """
        Research a specific tool using real-time web search
        
        Args:
            tool_name: Name of the tool
            tool_category: Category (optional)
            
        Returns:
            dict: Research results with citations
        """
        category_context = f" in the {tool_category} category" if tool_category else ""
        
        query = f"""Research the DevOps/cloud engineering tool "{tool_name}"{category_context}. 
Provide comprehensive information including:
1. Current version and latest updates
2. Key features and capabilities
3. Technical requirements and dependencies
4. Pricing model and licensing
5. Community size and activity
6. Known limitations or issues
7. Recent news or developments
8. Comparison with similar tools

Focus on accurate, up-to-date information from official sources."""

        return self.search_and_summarize(query)
    
    def research_tool_comparison(self, tool1_name, tool2_name, comparison_criteria=None):
        """
        Research and compare two tools
        
        Args:
            tool1_name: First tool name
            tool2_name: Second tool name
            comparison_criteria: Specific criteria to compare (optional)
            
        Returns:
            dict: Comparison research results
        """
        criteria_text = ""
        if comparison_criteria:
            criteria_text = f" focusing on: {', '.join(comparison_criteria)}"
        
        query = f"""Compare {tool1_name} vs {tool2_name} for DevOps/cloud engineering{criteria_text}.

Provide a detailed comparison including:
1. Feature comparison matrix
2. Performance benchmarks
3. Pricing differences
4. Use case recommendations
5. Pros and cons of each
6. Community and ecosystem
7. Learning curve and documentation
8. Enterprise readiness

Use the most current information available."""

        return self.search_and_summarize(query, max_tokens=3072)
    
    def get_latest_news(self, tool_name, days=30):
        """
        Get latest news and updates about a tool
        
        Args:
            tool_name: Tool name
            days: Number of days to look back
            
        Returns:
            dict: Latest news and updates
        """
        query = f"""What are the latest news, updates, and developments for {tool_name} 
in the last {days} days? Include:
1. Version releases
2. New features
3. Bug fixes or security updates
4. Community discussions
5. Integration announcements
6. Performance improvements

Provide only recent, verified information with sources."""

        return self.search_and_summarize(query, max_tokens=2048)
    
    def verify_information(self, statement, context="DevOps tools"):
        """
        Verify a specific statement or claim
        
        Args:
            statement: Statement to verify
            context: Context for verification
            
        Returns:
            dict: Verification results with evidence
        """
        query = f"""Verify the following statement in the context of {context}:

"{statement}"

Provide:
1. Verification status (True/False/Partially True/Unknown)
2. Evidence supporting or refuting the statement
3. Current accurate information
4. Reliable sources"""

        return self.search_and_summarize(query, max_tokens=1536)
