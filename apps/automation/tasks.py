"""
Celery tasks for automation workflows in CloudEngineered platform.
"""

try:
    from celery import shared_task
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
except ImportError:
    # Mock shared_task decorator when celery is not available
    def shared_task(*args, **kwargs):
        """Mock decorator for when celery is not available"""
        def decorator(func):
            def wrapper(*func_args, **func_kwargs):
                print(f"Mock task execution: {func.__name__}")
                return func(*func_args, **func_kwargs)
            return wrapper
        
        # Handle both @shared_task and @shared_task() syntax
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return decorator
    
    import logging
    logger = logging.getLogger(__name__)

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from typing import List, Dict, Any
import json

from apps.tools.models import Tool, Category
from apps.content.models import Article

try:
    from .ai_content_generator import AIContentGenerator
    from .github_monitor import GitHubMonitor
except ImportError as e:
    logger.warning(f"Some automation modules unavailable: {e}")
    AIContentGenerator = None
    GitHubMonitor = None


@shared_task(bind=True, max_retries=3)
def scan_github_for_tools(self):
    """
    Celery task to scan GitHub for new trending cloud engineering tools.
    """
    try:
        logger.info("Starting GitHub scan for new tools")
        
        monitor = GitHubMonitor()
        discovered_repos = monitor.scan_trending_repos()
        
        new_tools_created = 0
        
        for repo_data in discovered_repos:
            try:
                # Check if tool already exists
                if Tool.objects.filter(github_url=repo_data.get("url")).exists():
                    continue
                
                # Find or create category
                category_name = repo_data.get("suggested_category", "Development")
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        "description": f"Tools for {category_name.lower()}",
                        "slug": category_name.lower().replace(" ", "-").replace("/", "-")
                    }
                )
                
                # Create new tool
                tool = Tool.objects.create(
                    name=repo_data.get("name", ""),
                    description=repo_data.get("description", "")[:500],  # Limit description
                    category=category,
                    website_url=repo_data.get("url", ""),
                    github_url=repo_data.get("url", ""),
                    github_stars=repo_data.get("stars", 0),
                    github_forks=repo_data.get("forks", 0),
                    github_issues=repo_data.get("open_issues", 0),
                    github_last_commit=repo_data.get("updated_at"),
                    tags=repo_data.get("topics", [])[:10],  # Limit tags
                    features=repo_data.get("detected_features", []),
                    integrations=repo_data.get("detected_integrations", []),
                    is_published=False,  # Require manual review before publishing
                    status='active'
                )
                
                new_tools_created += 1
                logger.info(f"Created new tool: {tool.name}")
                
                # Schedule AI content generation for new tool
                generate_tool_content.delay(tool.id)
                
            except Exception as e:
                logger.error(f"Error creating tool from repo {repo_data.get('name', 'unknown')}: {e}")
                continue
        
        logger.info(f"GitHub scan completed. Created {new_tools_created} new tools.")
        return {
            "success": True,
            "new_tools_created": new_tools_created,
            "total_repos_analyzed": len(discovered_repos)
        }
        
    except Exception as exc:
        logger.error(f"GitHub scan failed: {exc}")
        raise self.retry(countdown=300)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=2)
def generate_tool_content(self, tool_id: int, content_types: List[str] = None):
    """
    Generate AI content for a tool.
    
    Args:
        tool_id: ID of the tool to generate content for
        content_types: List of content types to generate (default: ["review"])
    """
    
    if content_types is None:
        content_types = ["review"]
    
    try:
        tool = Tool.objects.get(id=tool_id)
        logger.info(f"Generating AI content for tool: {tool.name}")
        
        generator = AIContentGenerator()
        
        for content_type in content_types:
            try:
                if content_type == "review":
                    result = generator.generate_tool_review(tool)
                    
                    if result.get("success"):
                        # Create article from generated content
                        article = Article.objects.create(
                            title=f"{tool.name} Review: Comprehensive Analysis",
                            content=result["content"],
                            article_type="review",
                            related_tools=[tool.id],
                            ai_generated=True,
                            ai_provider=result["provider"],
                            ai_model=result["model"],
                            is_published=False,  # Require manual review
                            meta_title=f"{tool.name} Review - CloudEngineered",
                            meta_description=f"Comprehensive review of {tool.name}, a {tool.category.name.lower()} tool. Features, pros, cons, and alternatives.",
                        )
                        
                        # Update tool with AI summary
                        summary_lines = result["content"].split('\n')[:3]
                        tool.ai_summary = ' '.join(summary_lines)
                        tool.ai_review_generated = True
                        tool.ai_last_updated = timezone.now()
                        tool.save(update_fields=['ai_summary', 'ai_review_generated', 'ai_last_updated'])
                        
                        logger.info(f"Generated review article for {tool.name}")
                    
                elif content_type == "enhancement":
                    result = generator.enhance_tool_data(tool)
                    
                    if result.get("success"):
                        try:
                            enhanced_data = json.loads(result["content"])
                            
                            # Update tool with enhanced data
                            if enhanced_data.get("enhanced_description"):
                                tool.description = enhanced_data["enhanced_description"]
                            
                            if enhanced_data.get("key_features"):
                                tool.features = enhanced_data["key_features"]
                            
                            if enhanced_data.get("use_cases"):
                                tool.use_cases = enhanced_data["use_cases"]
                            
                            if enhanced_data.get("pros"):
                                tool.pros = enhanced_data["pros"]
                            
                            if enhanced_data.get("cons"):
                                tool.cons = enhanced_data["cons"]
                            
                            if enhanced_data.get("tags"):
                                tool.tags = enhanced_data["tags"][:10]  # Limit tags
                            
                            tool.ai_last_updated = timezone.now()
                            tool.save()
                            
                            logger.info(f"Enhanced tool data for {tool.name}")
                            
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse enhanced data for {tool.name}")
                
            except Exception as e:
                logger.error(f"Error generating {content_type} for {tool.name}: {e}")
                continue
        
        return {"success": True, "tool_id": tool_id}
        
    except Tool.DoesNotExist:
        logger.error(f"Tool with ID {tool_id} not found")
        return {"success": False, "error": "Tool not found"}
    
    except Exception as exc:
        logger.error(f"Content generation failed for tool {tool_id}: {exc}")
        raise self.retry(countdown=600)  # Retry after 10 minutes


@shared_task
def generate_trending_content():
    """
    Generate trending content and analyses.
    """
    try:
        logger.info("Generating trending content")
        
        generator = AIContentGenerator()
        
        # Get trending tools by category
        categories = Category.objects.filter(tools__is_published=True).distinct()
        
        for category in categories:
            trending_tools = Tool.objects.filter(
                category=category,
                is_published=True,
                is_trending=True
            ).order_by('-github_stars')[:5]
            
            if len(trending_tools) >= 3:
                try:
                    result = generator.generate_trend_analysis(category.name, list(trending_tools))
                    
                    if result.get("success"):
                        article = Article.objects.create(
                            title=f"{category.name} Tools Trend Analysis - {timezone.now().strftime('%B %Y')}",
                            content=result["content"],
                            article_type="analysis",
                            category=category,
                            ai_generated=True,
                            ai_provider=result["provider"],
                            ai_model=result["model"],
                            is_published=False,
                            meta_title=f"{category.name} Tools Trends - CloudEngineered",
                            meta_description=f"Latest trends and analysis in {category.name.lower()} tools. Market overview and recommendations.",
                        )
                        
                        logger.info(f"Generated trend analysis for {category.name}")
                
                except Exception as e:
                    logger.error(f"Error generating trend analysis for {category.name}: {e}")
                    continue
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Trending content generation failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def update_tool_github_stats():
    """
    Update GitHub statistics for all tools with GitHub URLs.
    """
    try:
        logger.info("Updating GitHub stats for all tools")
        
        monitor = GitHubMonitor()
        tools_with_github = Tool.objects.filter(
            github_url__isnull=False,
            is_published=True
        )
        
        updated_count = 0
        
        for tool in tools_with_github:
            try:
                if monitor.update_tool_github_stats(tool):
                    updated_count += 1
                    logger.info(f"Updated GitHub stats for {tool.name}")
            except Exception as e:
                logger.error(f"Error updating GitHub stats for {tool.name}: {e}")
                continue
        
        logger.info(f"Updated GitHub stats for {updated_count} tools")
        return {"success": True, "updated_count": updated_count}
        
    except Exception as e:
        logger.error(f"GitHub stats update failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def generate_tool_comparison(tool_ids: List[int], comparison_title: str = None):
    """
    Generate a comparison between multiple tools.
    
    Args:
        tool_ids: List of tool IDs to compare
        comparison_title: Optional custom title for the comparison
    """
    try:
        tools = Tool.objects.filter(id__in=tool_ids, is_published=True)
        
        if len(tools) < 2:
            return {"success": False, "error": "At least 2 tools required"}
        
        logger.info(f"Generating comparison for {len(tools)} tools")
        
        generator = AIContentGenerator()
        result = generator.generate_tool_comparison(list(tools))
        
        if result.get("success"):
            tool_names = [tool.name for tool in tools]
            title = comparison_title or f"{' vs '.join(tool_names[:3])} Comparison"
            
            from apps.tools.models import ToolComparison
            comparison = ToolComparison.objects.create(
                title=title,
                description=f"Comprehensive comparison of {', '.join(tool_names)}",
                introduction=result["content"],
                ai_generated=True,
                ai_last_updated=timezone.now(),
                is_published=False,
                meta_title=f"{title} - CloudEngineered",
                meta_description=f"Compare {', '.join(tool_names[:2])} and other {tools[0].category.name.lower()} tools.",
            )
            
            # Add tools to comparison
            comparison.tools.set(tools)
            
            logger.info(f"Generated comparison: {title}")
            return {"success": True, "comparison_id": comparison.id}
        
        return {"success": False, "error": "Content generation failed"}
        
    except Exception as e:
        logger.error(f"Tool comparison generation failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task
def cleanup_old_ai_generations():
    """
    Clean up old AI generation logs and temporary data.
    """
    try:
        # Clean up old, unpublished AI-generated content
        old_articles = Article.objects.filter(
            ai_generated=True,
            is_published=False,
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        )
        
        deleted_count = old_articles.count()
        old_articles.delete()
        
        logger.info(f"Cleaned up {deleted_count} old AI-generated articles")
        return {"success": True, "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"success": False, "error": str(e)}
