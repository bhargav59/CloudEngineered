"""
GitHub Statistics Service
Fetches and updates GitHub repository statistics for tools.
"""
import requests
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class GitHubStatsService:
    """
    Service to fetch and update GitHub repository statistics.
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub Stats Service.
        
        Args:
            github_token: GitHub Personal Access Token for higher rate limits
        """
        self.token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CloudTools-Platform'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    def extract_repo_info(self, github_url: str) -> Optional[Dict[str, str]]:
        """
        Extract owner and repo name from GitHub URL.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Dict with 'owner' and 'repo' keys, or None if invalid
        """
        if not github_url:
            return None
        
        try:
            # Remove trailing slash and split
            parts = github_url.rstrip('/').split('/')
            
            # Handle different GitHub URL formats
            if 'github.com' in github_url:
                # Find github.com in parts
                github_index = None
                for i, part in enumerate(parts):
                    if 'github.com' in part:
                        github_index = i
                        break
                
                if github_index is not None and len(parts) > github_index + 2:
                    owner = parts[github_index + 1]
                    repo = parts[github_index + 2]
                    
                    # Remove .git suffix if present
                    if repo.endswith('.git'):
                        repo = repo[:-4]
                    
                    return {'owner': owner, 'repo': repo}
            
            return None
        except Exception as e:
            logger.error(f"Error extracting repo info from {github_url}: {str(e)}")
            return None
    
    def fetch_repo_stats(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Fetch repository statistics from GitHub API.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary with repository statistics or None if failed
        """
        try:
            # Fetch main repo data
            repo_url = f"{self.BASE_URL}/repos/{owner}/{repo}"
            response = requests.get(repo_url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                logger.warning(f"Repository not found: {owner}/{repo}")
                return None
            elif response.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return None
            elif response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code}")
                return None
            
            repo_data = response.json()
            
            # Fetch contributors count
            contributors_url = f"{self.BASE_URL}/repos/{owner}/{repo}/contributors"
            contributors_response = requests.get(
                contributors_url, 
                headers=self.headers, 
                timeout=10,
                params={'per_page': 1, 'anon': 'true'}
            )
            
            contributors_count = 0
            if contributors_response.status_code == 200:
                # GitHub returns total count in Link header
                link_header = contributors_response.headers.get('Link', '')
                if 'rel="last"' in link_header:
                    # Extract page number from last link
                    try:
                        last_page = link_header.split('page=')[1].split('>')[0].split('&')[0]
                        contributors_count = int(last_page)
                    except:
                        contributors_count = len(contributors_response.json())
                else:
                    contributors_count = len(contributors_response.json())
            
            # Fetch latest release
            releases_url = f"{self.BASE_URL}/repos/{owner}/{repo}/releases/latest"
            releases_response = requests.get(releases_url, headers=self.headers, timeout=10)
            
            latest_release = None
            latest_release_date = None
            release_count = 0
            
            if releases_response.status_code == 200:
                release_data = releases_response.json()
                latest_release = release_data.get('tag_name', '')
                latest_release_date = release_data.get('published_at')
                
                # Get total release count
                all_releases_url = f"{self.BASE_URL}/repos/{owner}/{repo}/releases"
                all_releases_response = requests.get(
                    all_releases_url,
                    headers=self.headers,
                    timeout=10,
                    params={'per_page': 1}
                )
                if all_releases_response.status_code == 200:
                    link_header = all_releases_response.headers.get('Link', '')
                    if 'rel="last"' in link_header:
                        try:
                            last_page = link_header.split('page=')[1].split('>')[0].split('&')[0]
                            release_count = int(last_page)
                        except:
                            release_count = 1
                    else:
                        release_count = len(all_releases_response.json())
            
            # Parse dates
            created_at = None
            updated_at = None
            last_commit = None
            
            if repo_data.get('created_at'):
                created_at = datetime.strptime(
                    repo_data['created_at'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            
            if repo_data.get('updated_at'):
                updated_at = datetime.strptime(
                    repo_data['updated_at'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            
            if repo_data.get('pushed_at'):
                last_commit = datetime.strptime(
                    repo_data['pushed_at'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            
            if latest_release_date:
                latest_release_date = datetime.strptime(
                    latest_release_date, 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
            
            # Compile statistics
            stats = {
                'github_stars': repo_data.get('stargazers_count', 0),
                'github_forks': repo_data.get('forks_count', 0),
                'github_watchers': repo_data.get('watchers_count', 0),
                'github_issues': repo_data.get('open_issues_count', 0),
                'github_open_issues': repo_data.get('open_issues_count', 0),
                'github_contributors': contributors_count,
                'github_latest_release': latest_release or '',
                'github_latest_release_date': latest_release_date,
                'github_release_count': release_count,
                'github_created_at': created_at,
                'github_updated_at': updated_at,
                'github_last_commit': last_commit,
                'github_stats_last_updated': timezone.now(),
            }
            
            logger.info(f"Successfully fetched stats for {owner}/{repo}")
            return stats
            
        except requests.RequestException as e:
            logger.error(f"Request error fetching stats for {owner}/{repo}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching stats for {owner}/{repo}: {str(e)}")
            return None
    
    def update_tool_stats(self, tool) -> bool:
        """
        Update GitHub statistics for a tool.
        
        Args:
            tool: Tool model instance
            
        Returns:
            True if update successful, False otherwise
        """
        if not tool.github_url:
            logger.debug(f"Tool {tool.name} has no GitHub URL")
            return False
        
        # Check if we should update (don't update more than once per day)
        if tool.github_stats_last_updated:
            time_since_update = timezone.now() - tool.github_stats_last_updated
            if time_since_update < timedelta(days=1):
                logger.debug(f"Tool {tool.name} was recently updated, skipping")
                return False
        
        repo_info = self.extract_repo_info(tool.github_url)
        if not repo_info:
            logger.warning(f"Could not extract repo info from {tool.github_url}")
            return False
        
        stats = self.fetch_repo_stats(repo_info['owner'], repo_info['repo'])
        if not stats:
            return False
        
        # Update tool with new stats
        for field, value in stats.items():
            setattr(tool, field, value)
        
        tool.save(update_fields=list(stats.keys()))
        logger.info(f"Updated GitHub stats for {tool.name}")
        return True
    
    def batch_update_tools(self, tools_queryset, max_updates: int = 100) -> Dict[str, int]:
        """
        Update GitHub statistics for multiple tools.
        
        Args:
            tools_queryset: QuerySet of Tool instances
            max_updates: Maximum number of tools to update in one batch
            
        Returns:
            Dictionary with update statistics
        """
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        tools = tools_queryset.filter(github_url__isnull=False)[:max_updates]
        stats['total'] = len(tools)
        
        for tool in tools:
            try:
                if self.update_tool_stats(tool):
                    stats['success'] += 1
                else:
                    stats['skipped'] += 1
            except Exception as e:
                logger.error(f"Error updating tool {tool.name}: {str(e)}")
                stats['failed'] += 1
        
        logger.info(f"Batch update complete: {stats}")
        return stats
    
    def discover_trending_repos(self, 
                                language: Optional[str] = None,
                                since: str = 'daily',
                                limit: int = 10) -> List[Dict]:
        """
        Discover trending repositories on GitHub.
        
        Args:
            language: Programming language filter (e.g., 'python', 'javascript')
            since: Time period ('daily', 'weekly', 'monthly')
            limit: Maximum number of repositories to return
            
        Returns:
            List of trending repository information
        """
        try:
            # Calculate date range based on 'since' parameter
            date_map = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            days = date_map.get(since, 7)
            date_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            # Build search query
            query = f"created:>{date_from}"
            if language:
                query += f" language:{language}"
            
            # Search repositories
            search_url = f"{self.BASE_URL}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            response = requests.get(
                search_url, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub API error: {response.status_code}")
                return []
            
            data = response.json()
            repos = []
            
            for item in data.get('items', []):
                repos.append({
                    'name': item.get('full_name'),
                    'owner': item.get('owner', {}).get('login'),
                    'repo': item.get('name'),
                    'description': item.get('description', ''),
                    'url': item.get('html_url'),
                    'stars': item.get('stargazers_count', 0),
                    'forks': item.get('forks_count', 0),
                    'language': item.get('language', ''),
                    'topics': item.get('topics', []),
                })
            
            logger.info(f"Discovered {len(repos)} trending repositories")
            return repos
            
        except Exception as e:
            logger.error(f"Error discovering trending repos: {str(e)}")
            return []
