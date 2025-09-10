"""
Advanced GitHub Repository Monitor for CloudEngineered Platform

This module provides comprehensive GitHub integration for discovering new tools,
monitoring trends, and gathering repository statistics.
"""

import requests
import logging
import time
try:
    from github import Github
except ImportError:
    Github = None
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from decouple import config

logger = logging.getLogger(__name__)

class GitHubMonitor:
    """
    Advanced GitHub monitoring service for discovering and tracking cloud engineering tools.
    """
    
    def __init__(self):
        self.github_token = config('GITHUB_TOKEN', default=None)
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CloudEngineered-Bot/1.0'
        }
        
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
            
        # Rate limiting
        self.requests_count = 0
        self.requests_reset_time = time.time() + 3600  # Reset every hour
        self.max_requests_per_hour = 5000 if self.github_token else 60
        
        # Keywords for different tool categories
        self.category_keywords = {
            'CI/CD': [
                'ci', 'cd', 'continuous-integration', 'continuous-deployment', 
                'pipeline', 'jenkins', 'github-actions', 'gitlab-ci', 'travis',
                'circleci', 'build', 'deploy', 'automation'
            ],
            'Cloud Platforms': [
                'aws', 'azure', 'gcp', 'google-cloud', 'cloud', 'serverless',
                'lambda', 'functions', 'kubernetes', 'docker', 'containers'
            ],
            'Monitoring': [
                'monitoring', 'observability', 'metrics', 'logs', 'tracing',
                'prometheus', 'grafana', 'elk', 'datadog', 'newrelic',
                'alerting', 'dashboard', 'apm'
            ],
            'DevOps Tools': [
                'devops', 'infrastructure', 'iac', 'terraform', 'ansible',
                'puppet', 'chef', 'vagrant', 'packer', 'consul', 'vault'
            ],
            'Security': [
                'security', 'vulnerability', 'scanning', 'sast', 'dast',
                'secrets', 'encryption', 'compliance', 'policy', 'rbac'
            ],
            'Database': [
                'database', 'db', 'sql', 'nosql', 'postgres', 'mysql',
                'mongodb', 'redis', 'elasticsearch', 'migration'
            ],
            'Networking': [
                'network', 'proxy', 'load-balancer', 'ingress', 'service-mesh',
                'istio', 'envoy', 'nginx', 'haproxy', 'dns'
            ],
            'Testing': [
                'testing', 'test', 'qa', 'automation', 'selenium', 'cypress',
                'unit-test', 'integration-test', 'performance-test'
            ]
        }
    
    def scan_trending_repositories(self, language: str = None, time_range: str = 'daily') -> List[Dict[str, Any]]:
        """
        Scan GitHub for trending repositories that could be cloud engineering tools.
        
        Args:
            language: Programming language filter (optional)
            time_range: Time range for trending ('daily', 'weekly', 'monthly')
            
        Returns:
            List of repository data dictionaries
        """
        try:
            trending_repos = []
            
            # Search for trending repositories with cloud/DevOps keywords
            search_queries = [
                'devops stars:>100 created:>2024-01-01',
                'kubernetes stars:>50 created:>2024-01-01',
                'docker stars:>50 created:>2024-01-01',
                'terraform stars:>50 created:>2024-01-01',
                'monitoring stars:>50 created:>2024-01-01',
                'ci-cd stars:>50 created:>2024-01-01',
                'cloud-native stars:>50 created:>2024-01-01',
                'infrastructure stars:>50 created:>2024-01-01'
            ]
            
            for query in search_queries:
                if not self._can_make_request():
                    logger.warning("GitHub API rate limit approaching, stopping scan")
                    break
                
                repos = self._search_repositories(query, language=language)
                if repos:
                    # Filter and enrich repository data
                    for repo in repos:
                        if self._is_relevant_tool(repo):
                            enriched_repo = self._enrich_repository_data(repo)
                            if enriched_repo:
                                trending_repos.append(enriched_repo)
                
                # Rate limiting
                time.sleep(1)  # Be nice to GitHub API
            
            # Remove duplicates and sort by stars
            unique_repos = {}
            for repo in trending_repos:
                if repo['full_name'] not in unique_repos:
                    unique_repos[repo['full_name']] = repo
            
            sorted_repos = sorted(
                unique_repos.values(), 
                key=lambda x: x.get('stargazers_count', 0), 
                reverse=True
            )
            
            logger.info(f"Found {len(sorted_repos)} trending repositories")
            return sorted_repos[:50]  # Return top 50
            
        except Exception as e:
            logger.error(f"Error scanning trending repositories: {str(e)}")
            return []
    
    def get_repository_data(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for a specific repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository data dictionary or None if not found
        """
        try:
            if not self._can_make_request():
                logger.warning("GitHub API rate limit reached")
                return None
            
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = requests.get(url, headers=self.headers, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                repo_data = response.json()
                
                # Get additional data
                repo_data['topics'] = self._get_repository_topics(owner, repo)
                repo_data['languages'] = self._get_repository_languages(owner, repo)
                repo_data['contributors_count'] = self._get_contributors_count(owner, repo)
                repo_data['releases'] = self._get_latest_releases(owner, repo)
                
                return repo_data
            else:
                logger.warning(f"Repository {owner}/{repo} not found or inaccessible")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching repository data for {owner}/{repo}: {str(e)}")
            return None
    
    def categorize_repository(self, repo_data: Dict[str, Any]) -> Optional['Category']:
        """
        Automatically categorize a repository based on its metadata.
        
        Args:
            repo_data: Repository data from GitHub API
            
        Returns:
            Category instance or None
        """
        try:
            from apps.tools.models import Category
            
            # Analyze repository metadata
            text_to_analyze = ' '.join([
                repo_data.get('name', ''),
                repo_data.get('description', ''),
                ' '.join(repo_data.get('topics', [])),
                ' '.join(repo_data.get('languages', {}).keys())
            ]).lower()
            
            # Score each category
            category_scores = {}
            for category_name, keywords in self.category_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text_to_analyze:
                        score += 1
                
                if score > 0:
                    category_scores[category_name] = score
            
            # Return the highest scoring category
            if category_scores:
                best_category_name = max(category_scores, key=category_scores.get)
                category, created = Category.objects.get_or_create(
                    name=best_category_name,
                    defaults={'description': f'Tools and technologies for {best_category_name.lower()}'}
                )
                return category
            
            # Default category
            default_category, created = Category.objects.get_or_create(
                name='DevOps Tools',
                defaults={'description': 'General DevOps and cloud engineering tools'}
            )
            return default_category
            
        except Exception as e:
            logger.error(f"Error categorizing repository: {str(e)}")
            return None
    
    def extract_repo_info(self, github_url: str) -> Optional[Dict[str, str]]:
        """
        Extract owner and repository name from GitHub URL.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Dictionary with 'owner' and 'repo' keys or None
        """
        try:
            if 'github.com' not in github_url:
                return None
            
            # Handle different URL formats
            github_url = github_url.rstrip('/')
            parts = github_url.split('/')
            
            if len(parts) >= 2:
                owner = parts[-2]
                repo = parts[-1]
                
                # Remove .git suffix if present
                if repo.endswith('.git'):
                    repo = repo[:-4]
                
                return {'owner': owner, 'repo': repo}
            
        except Exception as e:
            logger.error(f"Error extracting repo info from {github_url}: {str(e)}")
        
        return None
    
    def monitor_tool_updates(self, tool: 'Tool') -> Dict[str, Any]:
        """
        Monitor a specific tool for updates and changes.
        
        Args:
            tool: Tool instance to monitor
            
        Returns:
            Dictionary with update information
        """
        try:
            if not tool.github_url:
                return {'error': 'No GitHub URL provided'}
            
            repo_info = self.extract_repo_info(tool.github_url)
            if not repo_info:
                return {'error': 'Invalid GitHub URL'}
            
            repo_data = self.get_repository_data(repo_info['owner'], repo_info['repo'])
            if not repo_data:
                return {'error': 'Repository not accessible'}
            
            # Detect significant changes
            changes = []
            
            # Check for star count changes
            if tool.github_stars and repo_data['stargazers_count'] != tool.github_stars:
                star_change = repo_data['stargazers_count'] - tool.github_stars
                changes.append({
                    'type': 'stars',
                    'change': star_change,
                    'new_value': repo_data['stargazers_count']
                })
            
            # Check for new releases
            latest_releases = repo_data.get('releases', [])
            if latest_releases and tool.last_updated:
                for release in latest_releases:
                    release_date = datetime.fromisoformat(
                        release['published_at'].replace('Z', '+00:00')
                    )
                    if release_date > tool.last_updated:
                        changes.append({
                            'type': 'release',
                            'version': release['tag_name'],
                            'date': release_date.isoformat()
                        })
            
            return {
                'success': True,
                'changes': changes,
                'current_data': repo_data
            }
            
        except Exception as e:
            logger.error(f"Error monitoring tool {tool.name}: {str(e)}")
            return {'error': str(e)}
    
    # Private helper methods
    
    def _can_make_request(self) -> bool:
        """Check if we can make another API request without hitting rate limits."""
        current_time = time.time()
        
        # Reset counter if hour has passed
        if current_time > self.requests_reset_time:
            self.requests_count = 0
            self.requests_reset_time = current_time + 3600
        
        return self.requests_count < (self.max_requests_per_hour - 10)  # Buffer of 10 requests
    
    def _search_repositories(self, query: str, language: str = None, per_page: int = 30) -> List[Dict[str, Any]]:
        """Search repositories using GitHub Search API."""
        try:
            search_query = query
            if language:
                search_query += f' language:{language}'
            
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': search_query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                logger.warning(f"GitHub search failed with status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching repositories: {str(e)}")
            return []
    
    def _is_relevant_tool(self, repo_data: Dict[str, Any]) -> bool:
        """Check if repository is relevant as a cloud engineering tool."""
        try:
            # Minimum criteria
            if repo_data.get('stargazers_count', 0) < 10:
                return False
            
            # Skip archived repositories
            if repo_data.get('archived', False):
                return False
            
            # Skip forks (we want original tools)
            if repo_data.get('fork', False):
                return False
            
            # Check for relevant content
            description = repo_data.get('description', '').lower()
            name = repo_data.get('name', '').lower()
            
            # Look for DevOps/Cloud keywords
            relevant_keywords = [
                'devops', 'cloud', 'kubernetes', 'docker', 'terraform',
                'ansible', 'monitoring', 'ci/cd', 'deployment', 'infrastructure',
                'serverless', 'microservices', 'automation', 'pipeline'
            ]
            
            text_to_check = f"{name} {description}"
            return any(keyword in text_to_check for keyword in relevant_keywords)
            
        except Exception as e:
            logger.error(f"Error checking repository relevance: {str(e)}")
            return False
    
    def _enrich_repository_data(self, repo_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enrich repository data with additional information."""
        try:
            owner = repo_data['owner']['login']
            repo = repo_data['name']
            
            # Get topics
            repo_data['topics'] = self._get_repository_topics(owner, repo)
            
            # Get languages
            repo_data['languages'] = self._get_repository_languages(owner, repo)
            
            # Get latest release
            repo_data['latest_release'] = self._get_latest_release(owner, repo)
            
            return repo_data
            
        except Exception as e:
            logger.error(f"Error enriching repository data: {str(e)}")
            return repo_data
    
    def _get_repository_topics(self, owner: str, repo: str) -> List[str]:
        """Get repository topics."""
        try:
            if not self._can_make_request():
                return []
            
            url = f"{self.base_url}/repos/{owner}/{repo}/topics"
            headers = {**self.headers, 'Accept': 'application/vnd.github.mercy-preview+json'}
            
            response = requests.get(url, headers=headers, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                return response.json().get('names', [])
            
        except Exception as e:
            logger.error(f"Error fetching topics for {owner}/{repo}: {str(e)}")
        
        return []
    
    def _get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get repository programming languages."""
        try:
            if not self._can_make_request():
                return {}
            
            url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            response = requests.get(url, headers=self.headers, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching languages for {owner}/{repo}: {str(e)}")
        
        return {}
    
    def _get_contributors_count(self, owner: str, repo: str) -> int:
        """Get number of contributors."""
        try:
            if not self._can_make_request():
                return 0
            
            url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
            response = requests.get(url, headers=self.headers, params={'per_page': 1}, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                # Get total count from Link header
                link_header = response.headers.get('Link', '')
                if 'last' in link_header:
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))
                
                # Fallback: count returned contributors
                return len(response.json())
            
        except Exception as e:
            logger.error(f"Error fetching contributors for {owner}/{repo}: {str(e)}")
        
        return 0
    
    def _get_latest_releases(self, owner: str, repo: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get latest releases."""
        try:
            if not self._can_make_request():
                return []
            
            url = f"{self.base_url}/repos/{owner}/{repo}/releases"
            response = requests.get(url, headers=self.headers, params={'per_page': limit}, timeout=10)
            self.requests_count += 1
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching releases for {owner}/{repo}: {str(e)}")
        
        return []
    
    def _get_latest_release(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get the latest release."""
        releases = self._get_latest_releases(owner, repo, limit=1)
        return releases[0] if releases else None

import requests
try:
    from github import Github
except ImportError:
    Github = None
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


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
    
    def update_tool_github_stats(self, tool: 'Tool') -> bool:
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
