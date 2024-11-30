from typing import Dict, List, Any
from pathlib import Path
from collections import defaultdict
import subprocess
from datetime import datetime
from analyze_repository_structure import RELEVANT_EXTENSIONS

class RepositorySelector:
    """Handles intelligent repository selection and authorship analysis"""

    def __init__(self, base_path: str, username: str):
        self.base_path = Path(base_path)
        self.username = username
        self.user_path = self.base_path / username
        
    def select_repositories(self, report_data: Dict) -> List[str]:
        """
        Main entry point for repository selection.
        Returns a list of repository names to analyze, including both best-scored repos
        and single-contributor repos.
        """
        # Store report data for use in other methods
        self.report_data = report_data
        
        # Get repositories with activity scores
        repositories = self._analyze_repositories(report_data)
        print(f"Found {len(repositories)} repositories with activity")
        
        # Get best scored repositories
        selected_repos = self._select_best_repositories(repositories)
        selected_repo_names = {repo["name"] for repo in selected_repos}
        
        # Get single-contributor repositories
        single_contributor_repos = self._get_only_owner_sources()
        
        # Combine both sets of repositories without duplicates
        all_repo_names = selected_repo_names.union(single_contributor_repos)
        
        print(f"Added {len(all_repo_names) - len(selected_repo_names)} single-contributor repositories")
        print(f"Total repositories to analyze: {len(all_repo_names)}")
        
        # Update metadata for all repositories
        self.repo_metadata = {}
        for repo in selected_repos:
            self.repo_metadata[repo["name"]] = {
                "contribution_files": repo["contribution_files"],
                "stats": repo["stats"]
            }
        
        # Add metadata for additional single-contributor repos if they weren't in selected_repos
        for repo_name in single_contributor_repos:
            if repo_name not in self.repo_metadata:
                repo_path = self.user_path / f"{self.username}_{repo_name}.git"
                if repo_path.exists():
                    stats = self._get_repository_stats(repo_path, report_data.get("commits", {}).get(repo_name, []))
                    contribution_files = self._analyze_contribution_files(repo_path)
                    self.repo_metadata[repo_name] = {
                        "contribution_files": contribution_files,
                        "stats": stats or {}
                    }
        
        return list(all_repo_names)

    def _get_only_owner_sources(self) -> List[str]:
        """Gets list of repositories to analyze. Only single-contributor repos are considered"""
        return [
            obj["repo"]
            for obj in self.report_data.get("contributors", [])
            if obj["contributors"][0] == self.username and len(obj["contributors"]) == 1
        ]

    # [Rest of the class methods remain unchanged...]
    def _analyze_repositories(self, report_data: Dict) -> List[Dict[str, Any]]:
        """Analyzes all repositories the user has contributed to"""
        repositories = []
        
        # Get repos from contributors data
        contributed_repos = [
            obj["repo"] for obj in report_data.get("contributors", [])
            if self.username in obj["contributors"]
        ]
        
        # Also get repos from commits data
        commit_repos = list(report_data.get("commits", {}).keys())
        
        # Combine and deduplicate
        all_repos = list(set(contributed_repos + commit_repos))
        
        print(f"Analyzing {len(all_repos)} repositories...")
        
        for repo_name in all_repos:
            repo_path = self.user_path / f"{self.username}_{repo_name}.git"
            if not repo_path.exists():
                continue
                
            repo_stats = self._get_repository_stats(repo_path, report_data.get("commits", {}).get(repo_name, []))
            if not repo_stats:
                continue
                
            contribution_files = self._analyze_contribution_files(repo_path)
            
            # Include repository if it has either commits or contribution files
            if repo_stats["commit_count"] > 0 or contribution_files:
                repositories.append({
                    "name": repo_name,
                    "stats": repo_stats,
                    "contribution_files": contribution_files
                })
        
        return repositories

    def _analyze_contribution_files(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Identifies files with user contributions, with more flexible criteria"""
        contribution_files = []
        
        # List all files in repository
        for file_path in repo_path.rglob('*'):
            relative_path = str(file_path.relative_to(repo_path))
            
            # Skip excluded paths and non-source files
            if not self._is_analyzable_file(relative_path):
                continue
                
            try:
                # Get authorship statistics
                author_stats = self._get_file_author_stats(repo_path, relative_path)
                
                # Include files where user has any meaningful contribution (>20%)
                if self.username in author_stats and author_stats[self.username] >= 20:
                    contribution_files.append({
                        "path": relative_path,
                        "contribution_percentage": author_stats[self.username]
                    })
                    
            except Exception as e:
                print(f"Error analyzing {relative_path}: {str(e)}")
                continue
                
        return contribution_files

    def _get_repository_stats(self, repo_path: Path, repo_commits: List = None) -> Dict[str, Any]:
        """Analyzes repository activity metrics with both git log and commits data"""
        try:
            # Get commit timestamps from git log
            result = subprocess.run(
                'git log --format=%at',
                cwd=repo_path,
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {}
                
            timestamps = [int(ts) for ts in result.stdout.strip().split('\n') if ts]
            
            # Also consider commits from report data
            if repo_commits:
                for commit in repo_commits:
                    commit_date = datetime.fromisoformat(
                        commit["commit"]["author"]["date"].replace("Z", "+00:00")
                    )
                    timestamps.append(int(commit_date.timestamp()))
            
            if not timestamps:
                return {}
                
            first_commit = datetime.fromtimestamp(min(timestamps))
            last_commit = datetime.fromtimestamp(max(timestamps))
            commit_count = len(timestamps)
            time_period = (last_commit - first_commit).days + 1
            
            return {
                "first_commit": first_commit.isoformat(),
                "last_commit": last_commit.isoformat(),
                "commit_count": commit_count,
                "commits_per_day": commit_count / max(time_period, 1),
                "active_days": time_period
            }
            
        except Exception as e:
            print(f"Error analyzing repository stats: {str(e)}")
            return {}

    def _get_file_author_stats(self, repo_path: Path, file_path: str) -> Dict[str, float]:
        """Analyzes file authorship percentages"""
        try:
            result = subprocess.run(
                ['git', 'blame', '--porcelain', file_path],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {}
                
            author_lines = defaultdict(int)
            total_lines = 0
            
            for line in result.stdout.split('\n'):
                if line.startswith('author '):
                    author = line.replace('author ', '', 1)
                    author_lines[author] += 1
                    total_lines += 1
            
            if total_lines == 0:
                return {}
                
            return {
                author: (count / total_lines * 100)
                for author, count in author_lines.items()
            }
            
        except Exception as e:
            print(f"Error getting authorship stats for {file_path}: {str(e)}")
            return {}

    def _select_best_repositories(self, repositories: List[Dict[str, Any]], 
                                max_repos: int = 15) -> List[Dict[str, Any]]:
        """Selects optimal repositories using more balanced scoring"""
        if not repositories:
            return []
            
        for repo in repositories:
            score = 0
            stats = repo["stats"]
            
            # Recency score (max 35 points)
            last_commit = datetime.fromisoformat(stats["last_commit"])
            days_since_last_commit = (datetime.now() - last_commit).days
            score += max(0, 35 - (days_since_last_commit / 30))
            
            # Activity score (max 35 points)
            commit_score = min(35, (stats["commit_count"] * 2) + (stats["commits_per_day"] * 10))
            score += commit_score
            
            # Contribution score (max 30 points)
            # Consider both number and quality of contributions
            contribution_files = repo["contribution_files"]
            if contribution_files:
                file_count = len(contribution_files)
                avg_contribution = sum(f["contribution_percentage"] for f in contribution_files) / file_count
                score += min(30, (file_count * 2) + (avg_contribution / 5))
            else:
                # Still give some points for commits if no files detected
                score += min(15, stats["commit_count"] / 2)
            
            repo["analysis_score"] = score
        
        # Sort by score and return top repositories
        repositories.sort(key=lambda x: x["analysis_score"], reverse=True)
        selected = repositories[:max_repos]
        
        print(f"\nSelected {len(selected)} repositories:")
        for repo in selected:
            print(f"- {repo['name']} (score: {repo['analysis_score']:.2f})")
            
        return selected

    def _is_analyzable_file(self, file_path: str) -> bool:
        """Determines if a file should be included in analysis"""
        path = Path(file_path)
        
        # Skip excluded directories
        excluded_paths = {
            'node_modules', '__pycache__', 'build', 'dist', '.git',
            'vendor', 'third_party', 'external'
        }
        
        if any(part in excluded_paths for part in path.parts):
            return False
            
        # Get file extension (lowercase)
        ext = path.suffix.lower()
        if not ext:
            return False
            
        return ext in RELEVANT_EXTENSIONS