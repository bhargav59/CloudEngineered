"""
AI Content Generation Service for         return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="how_to_guide",
            preferred_provider=provider,
            max_tokens=2500,
            temperature=0.6
        )
    
    # Helper methods for building prompts and system promptsineered platform.
Uses flexible AI service manager with OpenRouter, OpenAI, and Anthropic support.
"""

import json
from typing import Dict, List, Any
from django.conf import settings
from django.utils import timezone
from apps.tools.models import Tool
from apps.ai.service_manager import AIServiceManager


class AIContentGenerator:
    """
    AI-powered content generation with flexible provider support.
    Supports OpenRouter, direct OpenAI, and direct Anthropic APIs.
    """
    
    def __init__(self):
        self.ai_service = AIServiceManager()
        
    def generate_tool_review(self, tool: Tool, provider: str = None) -> Dict[str, Any]:
        """
        Generate a comprehensive tool review using AI.
        
        Args:
            tool: Tool instance to generate review for
            provider: Specific provider to use ('openai_direct', 'anthropic_direct', 'openrouter')
                     If None, uses automatic provider selection
        
        Returns:
            Dictionary containing generated review content
        """
        
        system_prompt = self._build_tool_review_system_prompt()
        user_prompt = self._build_tool_review_prompt(tool)
        
        return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="tool_review",
            preferred_provider=provider,
            max_tokens=2000,
            temperature=0.7
        )
    
    def generate_tool_comparison(self, tools: List[Tool], criteria: List[str] = None, provider: str = None) -> Dict[str, Any]:
        """
        Generate a comparison between multiple tools.
        
        Args:
            tools: List of Tool instances to compare
            criteria: Specific criteria to focus comparison on
            provider: Specific provider to use
            
        Returns:
            Dictionary containing comparison content
        """
        
        system_prompt = self._build_comparison_system_prompt()
        user_prompt = self._build_comparison_prompt(tools, criteria)
        
        return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="comparison",
            preferred_provider=provider,
            max_tokens=3000,
            temperature=0.6
        )
    
    def generate_trend_analysis(self, category: str, tools: List[Tool], provider: str = None) -> Dict[str, Any]:
        """
        Generate trend analysis for a category of tools.
        
        Args:
            category: Category name for analysis
            tools: List of trending tools in the category
            provider: Specific provider to use
            
        Returns:
            Dictionary containing trend analysis content
        """
        
        system_prompt = self._build_trend_analysis_system_prompt()
        user_prompt = self._build_trend_analysis_prompt(category, tools)
        
        return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="trend_analysis",
            preferred_provider=provider,
            max_tokens=2500,
            temperature=0.7
        )
    
    def generate_how_to_guide(self, tool: Tool, use_case: str, provider: str = None) -> Dict[str, Any]:
        """
        Generate a how-to guide for a specific tool and use case.
        
        Args:
            tool: Tool instance
            use_case: Specific use case to focus on
            provider: Specific provider to use
        
        Returns:
            Dictionary containing how-to guide content
        """
        
        system_prompt = self._build_how_to_system_prompt()
        user_prompt = self._build_how_to_prompt(tool, use_case)
        
        return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="how_to_guide",
            preferred_provider=provider,
            max_tokens=2500,
            temperature=0.6
        )
    
    # Helper methods for building prompts and system prompts
    def _build_tool_review_system_prompt(self) -> str:
        """Build system prompt for tool reviews."""
        return """You are a senior cloud engineer and DevOps expert writing comprehensive reviews for CloudEngineered, 
        a platform that helps technical professionals evaluate cloud engineering tools.
        
        Your reviews are known for:
        - Technical depth and accuracy
        - Honest, unbiased assessments
        - Practical insights for decision-makers
        - Real-world use case scenarios
        - Clear pros and cons analysis
        
        Write for an audience of cloud engineers, DevOps professionals, and technical decision-makers."""
    
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
    
    def _build_comparison_system_prompt(self) -> str:
        """Build system prompt for tool comparison."""
        return """You are an expert technical writer specializing in software tool comparisons.
        
        Your role is to create comprehensive, balanced comparisons between software tools. Focus on:
        - Clear, objective analysis
        - Practical use cases and scenarios
        - Strengths and weaknesses of each tool
        - Performance and feature comparisons
        - User experience considerations
        - Pricing and value proposition
        
        Write in a professional, informative tone that helps readers make informed decisions."""
    
    def _build_trend_analysis_system_prompt(self) -> str:
        """Build system prompt for trend analysis."""
        return """You are a technology trend analyst specializing in software tools and digital solutions.
        
        Your expertise includes:
        - Identifying emerging patterns in tool adoption
        - Understanding market forces driving tool popularity
        - Analyzing user behavior and preferences
        - Predicting future developments in tool categories
        - Contextualizing trends within broader industry movements
        
        Provide insightful analysis that helps readers understand not just what's trending, but why it matters."""
    
    def _build_how_to_system_prompt(self) -> str:
        """Build system prompt for how-to guides."""
        return """You are an expert technical writer specializing in practical how-to guides for software tools.
        
        Your guides are known for:
        - Clear, step-by-step instructions
        - Practical examples and real-world scenarios
        - Troubleshooting common issues
        - Best practices and tips
        - Accessible explanations for different skill levels
        
        Create guides that are immediately actionable and help users achieve their goals efficiently."""
    
    def _build_comparison_prompt(self, tools: List[Tool], criteria: List[str] = None) -> str:
        """Build comparison prompt for multiple tools."""
        tool_details = []
        for tool in tools:
            details = f"""
            **{tool.name}**
            - Description: {tool.description}
            - Category: {tool.category.name if tool.category else 'Uncategorized'}
            - Website: {tool.website}
            """
            if hasattr(tool, 'pricing_model'):
                details += f"- Pricing: {tool.pricing_model}\n"
            if hasattr(tool, 'key_features'):
                details += f"- Key Features: {tool.key_features}\n"
            tool_details.append(details)
        
        prompt = f"""
        Compare the following tools and create a comprehensive comparison article:
        
        {chr(10).join(tool_details)}
        """
        
        if criteria:
            prompt += f"\nFocus particularly on these criteria: {', '.join(criteria)}"
        
        prompt += """
        
        Please provide:
        1. Executive summary of the comparison
        2. Feature-by-feature comparison
        3. Use case scenarios for each tool
        4. Pros and cons for each tool
        5. Final recommendations based on different user needs
        
        Make the comparison balanced, informative, and actionable for readers deciding between these tools.
        """
        
        return prompt
    
    def _build_trend_analysis_prompt(self, category: str, tools: List[Tool]) -> str:
        """Build trend analysis prompt."""
        tool_list = []
        for tool in tools:
            tool_info = f"- {tool.name}: {tool.description}"
            if hasattr(tool, 'github_stars'):
                tool_info += f" ({tool.github_stars} GitHub stars)"
            tool_list.append(tool_info)
        
        return f"""
        Analyze the current trends in the {category} category based on these popular tools:
        
        {chr(10).join(tool_list)}
        
        Please provide:
        1. Overview of current trends in the {category} space
        2. Analysis of why these particular tools are gaining popularity
        3. Common patterns and features driving adoption
        4. Emerging technologies or approaches in this category
        5. Predictions for future developments
        6. Implications for developers and businesses
        
        Focus on providing actionable insights that help readers understand the evolving landscape
        and make informed decisions about tool adoption.
        """
    
    def _build_how_to_prompt(self, tool: Tool, use_case: str) -> str:
        """Build how-to guide prompt."""
        return f"""
        Create a comprehensive how-to guide for using {tool.name} for {use_case}.
        
        Tool Information:
        - Name: {tool.name}
        - Description: {tool.description}
        - Website: {tool.website}
        - Category: {tool.category.name if tool.category else 'Uncategorized'}
        
        Please structure the guide with:
        1. Introduction and overview of the use case
        2. Prerequisites and setup requirements
        3. Step-by-step instructions with examples
        4. Common pitfalls and how to avoid them
        5. Advanced tips and best practices
        6. Troubleshooting section
        7. Conclusion with next steps
        
        Make the guide practical, detailed, and suitable for users with varying levels of experience.
        Include specific examples and code snippets where relevant.
        """
    
    def enhance_tool_data(self, tool: Tool) -> Dict[str, Any]:
        """
        Use AI to enhance tool data with better descriptions, features, etc.
        """
        
        system_prompt = """You are an expert cloud engineer and technical analyst specializing in DevOps tools and infrastructure.
        
        Your role is to analyze and enhance tool data with:
        - Accurate technical descriptions
        - Comprehensive feature lists
        - Practical use cases
        - Target audience identification
        - Integration possibilities
        - Balanced pros and cons analysis
        
        Provide structured, accurate information based on publicly available data."""
        
        user_prompt = f"""
        Analyze this cloud engineering tool and provide enhanced, structured data:
        
        Tool: {tool.name}
        Current description: {tool.description}
        Website: {tool.website}
        Category: {tool.category.name if tool.category else 'Uncategorized'}
        
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
        
        return self.ai_service.generate_content(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            content_type="tool_enhancement",
            max_tokens=2000,
            temperature=0.3
        )
