"""
GitHub monitoring service for discovering new cloud engineering tools.
"""

import requests
from github import Github
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from apps.tools.models import Tool, Category


class GitHubMonitor:
    """
    Service for monitoring GitHub repositories to discover new cloud engineering tools.
    """
    
    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN) if settings.GITHUB_TOKEN else None
        self.session = requests.Session()
    
    def scan_trending_repos(self, time_period: str = "week") -> List[Dict[str, Any]]:
        """
        Scan GitHub for trending repositories in cloud engineering categories.
        
        Args:
            time_period: "day", "week", or "month"
        
        Returns:
            List of repository data for potential tools
        """
        
        # Cloud engineering related topics and keywords
        search_queries = [
            "topic:devops topic:kubernetes",
            "topic:docker topic:containerization",
            "topic:terraform topic:infrastructure",
            "topic:monitoring topic:observability",
            "topic:ci-cd topic:deployment",
            "topic:aws topic:cloud",
            "topic:microservices topic:api-gateway",
            "topic:security topic:devsecops",
            "language:go topic:cli",
            "language:python topic:automation",
        ]
        
        discovered_repos = []
        
        for query in search_queries:
            try:
                repos = self._search_repositories(query, time_period)
                discovered_repos.extend(repos)
            except Exception as e:
                print(f"Error searching for '{query}': {e}")
                continue
        
        # Remove duplicates and filter
        unique_repos = self._deduplicate_repos(discovered_repos)
        filtered_repos = self._filter_relevant_repos(unique_repos)
        
        return filtered_repos
    
    def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze a specific GitHub repository for tool information.
        
        Args:
            repo_url: GitHub repository URL
        
        Returns:
            Dictionary with repository analysis
        """
        
        try:
            # Extract owner/repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return {"error": "Invalid repository URL"}
            
            owner, repo_name = parts[0], parts[1]
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Get repository details
            repo_data = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "topics": repo.get_topics(),
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "license": repo.license.name if repo.license else None,
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "open_issues": repo.open_issues_count,
                "size": repo.size,
                "default_branch": repo.default_branch,
            }
            
            # Analyze README for more details
            readme_analysis = self._analyze_readme(repo)
            repo_data.update(readme_analysis)
            
            # Categorize the tool
            category = self._categorize_repository(repo_data)
            repo_data["suggested_category"] = category
            
            return repo_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def update_tool_github_stats(self, tool: Tool) -> bool:
        """
        Update GitHub statistics for an existing tool.
        
        Args:
            tool: Tool instance to update
        
        Returns:
            Success status
        """
        
        if not tool.github_url:
            return False
        
        try:
            repo_data = self.analyze_repository(tool.github_url)
            
            if "error" not in repo_data:
                tool.github_stars = repo_data.get("stars", 0)
                tool.github_forks = repo_data.get("forks", 0)
                tool.github_issues = repo_data.get("open_issues", 0)
                tool.github_last_commit = repo_data.get("updated_at")
                tool.save(update_fields=[
                    'github_stars', 'github_forks', 'github_issues', 'github_last_commit'
                ])
                return True
                
        except Exception as e:
            print(f"Error updating GitHub stats for {tool.name}: {e}")
        
        return False
    
    def _search_repositories(self, query: str, time_period: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories with specific query."""
        
        # Calculate date range
        end_date = datetime.now()
        if time_period == "day":
            start_date = end_date - timedelta(days=1)
        elif time_period == "week":
            start_date = end_date - timedelta(weeks=1)
        else:  # month
            start_date = end_date - timedelta(days=30)
        
        # Add date range to query
        date_query = f"created:>{start_date.strftime('%Y-%m-%d')}"
        full_query = f"{query} {date_query} stars:>50"
        
        repositories = self.github.search_repositories(
            query=full_query,
            sort="stars",
            order="desc"
        )
        
        repos_data = []
        for repo in repositories[:20]:  # Limit to top 20 per query
            try:
                repo_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "topics": repo.get_topics(),
                    "created_at": repo.created_at,
                    "updated_at": repo.updated_at,
                    "license": repo.license.name if repo.license else None,
                }
                repos_data.append(repo_info)
            except Exception as e:
                print(f"Error processing repo {repo.name}: {e}")
                continue
        
        return repos_data
    
    def _analyze_readme(self, repo) -> Dict[str, Any]:
        """Analyze repository README for additional information."""
        
        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode('utf-8').lower()
            
            # Look for key indicators
            features = []
            use_cases = []
            integrations = []
            
            # Feature detection
            feature_keywords = [
                'monitoring', 'dashboard', 'metrics', 'logging', 'alerting',
                'deployment', 'ci/cd', 'automation', 'orchestration',
                'security', 'backup', 'scaling', 'load balancing',
                'api gateway', 'service mesh', 'configuration',
            ]
            
            for keyword in feature_keywords:
                if keyword in content:
                    features.append(keyword)
            
            # Integration detection
            integration_keywords = [
                'kubernetes', 'docker', 'aws', 'gcp', 'azure',
                'prometheus', 'grafana', 'jenkins', 'gitlab',
                'slack', 'webhook', 'rest api', 'grpc',
            ]
            
            for keyword in integration_keywords:
                if keyword in content:
                    integrations.append(keyword)
            
            return {
                "detected_features": features[:10],  # Limit to 10
                "detected_integrations": integrations[:10],
                "readme_length": len(content),
                "has_installation_guide": "installation" in content or "install" in content,
                "has_examples": "example" in content or "usage" in content,
            }
            
        except Exception:
            return {}
    
    def _categorize_repository(self, repo_data: Dict[str, Any]) -> Optional[str]:
        """Categorize repository based on its characteristics."""
        
        description = (repo_data.get("description") or "").lower()
        topics = [topic.lower() for topic in repo_data.get("topics", [])]
        features = repo_data.get("detected_features", [])
        
        # Category mapping based on keywords
        category_keywords = {
            "CI/CD": ["ci", "cd", "continuous", "integration", "deployment", "pipeline", "jenkins", "gitlab"],
            "Monitoring": ["monitoring", "metrics", "observability", "prometheus", "grafana", "alerting"],
            "Container": ["docker", "container", "kubernetes", "k8s", "orchestration", "pod"],
            "Infrastructure": ["terraform", "infrastructure", "iac", "provisioning", "cloud"],
            "Security": ["security", "vulnerability", "scanning", "devsecops", "compliance"],
            "API Management": ["api", "gateway", "proxy", "microservices", "service mesh"],
            "Database": ["database", "sql", "nosql", "redis", "postgres", "mongodb"],
            "Networking": ["network", "load balancer", "ingress", "service discovery"],
            "Development": ["development", "cli", "sdk", "framework", "tool"],
        }
        
        all_text = f"{description} {' '.join(topics)} {' '.join(features)}"
        
        for category, keywords in category_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                return category
        
        return "Development"  # Default category
    
    def _deduplicate_repos(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate repositories."""
        
        seen_urls = set()
        unique_repos = []
        
        for repo in repos:
            url = repo.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                unique_repos.append(repo)
        
        return unique_repos
    
    def _filter_relevant_repos(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter repositories to only include relevant cloud engineering tools."""
        
        filtered = []
        
        for repo in repos:
            # Skip if already exists in our database
            if Tool.objects.filter(github_url=repo.get("url")).exists():
                continue
            
            # Filter criteria
            if (
                repo.get("stars", 0) >= 100 and  # Minimum popularity
                repo.get("description") and  # Has description
                len(repo.get("description", "")) > 20 and  # Meaningful description
                repo.get("language") in ["Python", "Go", "JavaScript", "TypeScript", "Java", "Rust", "Shell", None] and  # Relevant languages
                not any(skip_word in repo.get("description", "").lower() for skip_word in ["game", "tutorial", "example", "demo", "test"])  # Skip non-tools
            ):
                filtered.append(repo)
        
        return sorted(filtered, key=lambda x: x.get("stars", 0), reverse=True)
