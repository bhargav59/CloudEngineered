"""
AI Content Generation Service for CloudEngineered platform.
"""

import openai
import anthropic
import json
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from apps.tools.models import Tool


class AIContentGenerator:
    """
    AI-powered content generation using OpenAI GPT-4 and Anthropic Claude.
    """
    
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=settings.OPENAI_API_KEY
        ) if settings.OPENAI_API_KEY else None
        
        self.anthropic_client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY
        ) if settings.ANTHROPIC_API_KEY else None
    
    def generate_tool_review(self, tool: Tool, provider: str = "openai") -> Dict[str, Any]:
        """
        Generate a comprehensive tool review using AI.
        
        Args:
            tool: Tool instance to generate review for
            provider: AI provider to use ("openai" or "anthropic")
        
        Returns:
            Dictionary containing generated review content
        """
        
        prompt = self._build_tool_review_prompt(tool)
        
        if provider == "openai" and self.openai_client:
            return self._generate_with_openai(prompt, "tool_review")
        elif provider == "anthropic" and self.anthropic_client:
            return self._generate_with_anthropic(prompt, "tool_review")
        else:
            raise ValueError(f"Provider {provider} not available or not configured")
    
    def generate_tool_comparison(self, tools: List[Tool], criteria: List[str] = None) -> Dict[str, Any]:
        """
        Generate a comparison between multiple tools.
        
        Args:
            tools: List of tools to compare
            criteria: Specific criteria to focus on
        
        Returns:
            Dictionary containing generated comparison content
        """
        
        if len(tools) < 2:
            raise ValueError("At least 2 tools required for comparison")
        
        prompt = self._build_comparison_prompt(tools, criteria)
        return self._generate_with_openai(prompt, "tool_comparison")
    
    def generate_trend_analysis(self, category: str, tools: List[Tool]) -> Dict[str, Any]:
        """
        Generate trend analysis for a tool category.
        
        Args:
            category: Tool category name
            tools: List of tools in the category
        
        Returns:
            Dictionary containing trend analysis content
        """
        
        prompt = self._build_trend_analysis_prompt(category, tools)
        return self._generate_with_openai(prompt, "trend_analysis")
    
    def generate_how_to_guide(self, tool: Tool, use_case: str) -> Dict[str, Any]:
        """
        Generate a how-to guide for a specific tool and use case.
        
        Args:
            tool: Tool instance
            use_case: Specific use case to focus on
        
        Returns:
            Dictionary containing how-to guide content
        """
        
        prompt = self._build_how_to_prompt(tool, use_case)
        return self._generate_with_anthropic(prompt, "how_to_guide")
    
    def _build_tool_review_prompt(self, tool: Tool) -> str:
        """Build prompt for tool review generation."""
        
        tool_info = {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.name,
            "website": tool.website_url,
            "github": tool.github_url,
            "pricing_model": tool.pricing_model,
            "features": tool.features,
            "integrations": tool.integrations,
            "supported_platforms": tool.supported_platforms,
            "languages": tool.languages,
            "company": tool.company,
        }
        
        prompt = f"""
        You are a senior cloud engineer and DevOps expert writing a comprehensive review for CloudEngineered, 
        a platform that helps technical professionals evaluate cloud engineering tools.

        Write a detailed, technical review for the following tool:
        {json.dumps(tool_info, indent=2)}

        The review should include:

        1. **Executive Summary** (2-3 sentences)
        2. **What is {tool.name}?** (150-200 words)
        3. **Key Features** (bullet points with explanations)
        4. **Strengths** (3-5 points with technical details)
        5. **Weaknesses** (2-4 honest limitations)
        6. **Use Cases** (3-4 scenarios with examples)
        7. **Integration Capabilities** (how it works with other tools)
        8. **Pricing Analysis** (value proposition)
        9. **Alternatives** (2-3 competing tools)
        10. **Final Verdict** (recommendation with rating 1-5)

        Write in a professional, technical tone for an audience of cloud engineers, DevOps professionals, 
        and technical decision-makers. Be honest, unbiased, and provide practical insights.
        
        Focus on technical implementation details, real-world performance, and practical considerations.
        Include specific examples and scenarios where relevant.
        """
        
        return prompt
    
    def _build_comparison_prompt(self, tools: List[Tool], criteria: List[str]) -> str:
        """Build prompt for tool comparison generation."""
        
        tools_data = []
        for tool in tools:
            tools_data.append({
                "name": tool.name,
                "description": tool.description,
                "features": tool.features,
                "pricing_model": tool.pricing_model,
                "supported_platforms": tool.supported_platforms,
                "integrations": tool.integrations,
                "github_stars": tool.github_stars,
            })
        
        criteria_text = ", ".join(criteria) if criteria else "features, pricing, ease of use, scalability, integration capabilities"
        
        prompt = f"""
        You are a senior cloud engineer writing a detailed comparison for CloudEngineered platform.
        
        Compare the following tools:
        {json.dumps(tools_data, indent=2)}
        
        Create a comprehensive comparison focusing on: {criteria_text}
        
        Structure the comparison as:
        
        1. **Introduction** (what tools we're comparing and why)
        2. **Quick Comparison Table** (side-by-side key metrics)
        3. **Detailed Analysis** by criteria:
           - Features and Capabilities
           - Pricing and Value
           - Ease of Use and Learning Curve
           - Integration and Ecosystem
           - Performance and Scalability
           - Community and Support
        4. **Use Case Scenarios** (when to choose each tool)
        5. **Decision Framework** (how to choose)
        6. **Final Recommendations**
        
        Be objective, technical, and provide specific examples.
        Include pros and cons for each tool.
        """
        
        return prompt
    
    def _build_trend_analysis_prompt(self, category: str, tools: List[Tool]) -> str:
        """Build prompt for trend analysis generation."""
        
        tools_data = [{
            "name": tool.name,
            "github_stars": tool.github_stars,
            "created_at": tool.created_at.isoformat(),
            "status": tool.status,
            "company": tool.company,
            "pricing_model": tool.pricing_model,
        } for tool in tools]
        
        prompt = f"""
        You are a cloud engineering analyst writing a trend analysis for the {category} category.
        
        Analyze trends in the {category} space based on these tools:
        {json.dumps(tools_data, indent=2)}
        
        Create a comprehensive trend analysis including:
        
        1. **Market Overview** (current state of {category} tools)
        2. **Key Trends** (emerging patterns and developments)
        3. **Technology Evolution** (how the space is advancing)
        4. **Market Leaders** (dominant players and why)
        5. **Emerging Tools** (new entrants to watch)
        6. **Future Predictions** (where the market is heading)
        7. **Recommendations** (advice for teams choosing tools)
        
        Focus on technical innovation, market adoption patterns, and practical implications for engineering teams.
        """
        
        return prompt
    
    def _build_how_to_prompt(self, tool: Tool, use_case: str) -> str:
        """Build prompt for how-to guide generation."""
        
        prompt = f"""
        You are a senior DevOps engineer writing a practical how-to guide for CloudEngineered.
        
        Create a step-by-step guide for: "How to use {tool.name} for {use_case}"
        
        Tool details:
        - Name: {tool.name}
        - Description: {tool.description}
        - Website: {tool.website_url}
        - Documentation: {tool.documentation_url}
        - Features: {tool.features}
        - Supported platforms: {tool.supported_platforms}
        
        Structure the guide as:
        
        1. **Introduction** (what we'll accomplish)
        2. **Prerequisites** (what you need before starting)
        3. **Step-by-Step Instructions** (detailed implementation)
        4. **Configuration Examples** (code snippets and configs)
        5. **Best Practices** (optimization tips)
        6. **Troubleshooting** (common issues and solutions)
        7. **Next Steps** (advanced usage and integrations)
        
        Include practical code examples, configuration snippets, and real-world tips.
        Write for experienced engineers who want actionable guidance.
        """
        
        return prompt
    
    def _generate_with_openai(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """Generate content using OpenAI GPT-4."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert cloud engineer and technical writer specializing in DevOps tools and infrastructure."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7,
            )
            
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "provider": "openai",
                "model": "gpt-4o",
                "content_type": content_type,
                "generated_at": timezone.now(),
                "tokens_used": response.usage.total_tokens,
                "success": True,
            }
            
        except Exception as e:
            return {
                "content": None,
                "provider": "openai",
                "model": "gpt-4o",
                "content_type": content_type,
                "generated_at": timezone.now(),
                "error": str(e),
                "success": False,
            }
    
    def _generate_with_anthropic(self, prompt: str, content_type: str) -> Dict[str, Any]:
        """Generate content using Anthropic Claude."""
        
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            return {
                "content": content,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "content_type": content_type,
                "generated_at": timezone.now(),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
                "success": True,
            }
            
        except Exception as e:
            return {
                "content": None,
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "content_type": content_type,
                "generated_at": timezone.now(),
                "error": str(e),
                "success": False,
            }
    
    def enhance_tool_data(self, tool: Tool) -> Dict[str, Any]:
        """
        Use AI to enhance tool data with better descriptions, features, etc.
        """
        
        prompt = f"""
        Analyze this cloud engineering tool and provide enhanced, structured data:
        
        Tool: {tool.name}
        Current description: {tool.description}
        Website: {tool.website_url}
        Category: {tool.category.name}
        
        Provide a JSON response with:
        {{
            "enhanced_description": "Better, more technical description (max 200 words)",
            "key_features": ["feature1", "feature2", ...],
            "use_cases": ["use_case1", "use_case2", ...],
            "target_audience": ["role1", "role2", ...],
            "integration_categories": ["category1", "category2", ...],
            "pros": ["pro1", "pro2", ...],
            "cons": ["con1", "con2", ...],
            "alternatives": ["alt1", "alt2", ...],
            "tags": ["tag1", "tag2", ...]
        }}
        
        Base your analysis on publicly available information about this tool.
        Be accurate and avoid speculation.
        """
        
        return self._generate_with_openai(prompt, "tool_enhancement")
