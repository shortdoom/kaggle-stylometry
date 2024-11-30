from collections import Counter
import json
from datetime import datetime
import statistics
from typing import Any, Dict, List, Tuple
from analyze_repository_structure import RELEVANT_EXTENSIONS
from pathlib import Path
from prompt_analyzer import create_handler
import subprocess
import os


def analyze_temporal_patterns(
    sources_data: Dict[str, Any], report_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyzes temporal patterns using both LLM and statistical analysis"""

    commits = report_data.get("commits", {})

    # Setup LLM Prompting
    handler = create_handler()
    combined_results = {}

    # Get commit timestamps for activity analysis
    commit_times = [
        datetime.fromisoformat(
            commit["commit"]["author"]["date"].replace("Z", "+00:00")
        )
        for repo_commits in commits.values()
        for commit in repo_commits
    ]

    # Get best targets and their commit contents
    temporal_best_targets = _select_best_targets(sources_data, commits)
    commit_contents = _get_commit_contents(temporal_best_targets, sources_data)

    # Save commit contents for inspection
    inspection_data = {
        "temporal_targets": temporal_best_targets,
        "commit_contents": commit_contents,
    }

    inspection_path = Path("out") / "temporal_analysis_contents.json"
    try:
        with open(inspection_path, "w", encoding="utf-8") as f:
            json.dump(inspection_data, f, indent=2)
        print(f"Saved temporal analysis data to {inspection_path}")
    except Exception as e:
        print(f"Error saving inspection data: {str(e)}")

    for repo_name, repo_data in sources_data.items():
        if repo_name not in temporal_best_targets:
            continue

        print(f"\nAnalyzing temporal patterns for repository: {repo_name}")

        # Get code changes for this repository
        repo_changes = commit_contents.get(repo_name, [])
        if not repo_changes:
            continue

        # Analyze code style evolution using LLM with actual code changes
        prompt = f"""
        
        TEMPORAL ANALYSIS
        
        Analyze the temporal evolution of this codebase with focus on developer behavior patterns and code evolution.
        
        Repository: {repo_name}
        
        Code Evolution Data:
        {json.dumps(repo_changes, indent=2)}

        Generate detailed temporal analysis JSON:
        {{
            "evolution_patterns": {{
                "code_quality": {{
                    "progression": string,
                    "refactoring_patterns": [
                        {{
                            "pattern": string,
                            "frequency": string,
                            "motivation": string
                        }}
                    ],
                    "complexity_trends": {{
                        "direction": string,
                        "significant_changes": [string],
                        "trigger_patterns": [string]
                    }}
                }},
                "development_cycles": {{
                    "commit_patterns": {{
                        "frequency": {{
                            "pattern": string,
                            "active_hours": [string],
                            "timezone_confidence": {{
                                "zone": string,
                                "confidence": number,
                                "evidence": [string]
                            }}
                        }},
                        "burst_patterns": [
                            {{
                                "pattern": string,
                                "typical_duration": string,
                                "characteristics": [string]
                            }}
                        ]
                    }},
                    "feature_development": {{
                        "typical_cycle": string,
                        "iteration_patterns": [string],
                        "testing_integration": string
                    }}
                }},
                "communication_patterns": {{
                    "pr_characteristics": {{
                        "detail_level": string,
                        "discussion_style": string,
                        "iteration_patterns": string
                    }},
                    "documentation_evolution": {{
                        "frequency": string,
                        "detail_trends": string,
                        "update_patterns": string
                    }}
                }}
            }},
            "architectural_evolution": {{
                "major_changes": [
                    {{
                        "change": string,
                        "motivation": string,
                        "impact": string
                    }}
                ],
                "improvement_patterns": {{
                    "refactoring_types": [string],
                    "optimization_focus": [string],
                    "maintenance_patterns": string
                }},
                "technical_debt": {{
                    "accumulation_patterns": [string],
                    "resolution_approaches": string,
                    "prevention_strategies": string
                }}
            }}
        }}

        Requirements:
        1. Focus on developer behavior patterns
        2. Track evolution of coding style
        3. Identify clear timezone patterns
        4. Detail burst activity characteristics
        5. Analyze code quality progression
        """


        try:
            result = handler.generate_json_response(prompt)
            if result:
                combined_results[repo_name] = result
        except Exception as e:
            print(f"Error analyze_temporal_patterns {repo_name}: {str(e)}")
            combined_results[repo_name] = {"error": str(e)}

    return {
        "commit_style_metrics": combined_results,
        "activity_patterns": _analyze_activity_patterns(commit_times),
    }


def _clean_diff(diff_output: str) -> str:
    """Clean up diff output to focus on actual changes"""
    lines = diff_output.split("\n")
    cleaned_lines = []
    skip_next = False

    for line in lines:
        # Skip git-specific headers
        if (
            line.startswith("diff --git")
            or line.startswith("index ")
            or line.startswith("new file mode ")
            or line.startswith("deleted file mode ")
        ):
            continue

        # Keep file markers but clean them up
        if line.startswith("--- ") or line.startswith("+++ "):
            # Convert /dev/null to clearer marker
            if "/dev/null" in line:
                continue
            # Keep just the filename
            cleaned_lines.append(line.split("/")[-1])
            continue

        # Keep actual diff content
        if (
            line.startswith("@@ ")
            or line.startswith("+")
            or line.startswith("-")
            or line.startswith(" ")
        ):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def _get_commit_contents(
    target_repos: List[str], sources_data: Dict[str, Any], max_diff_lines: int = 100
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves commit contents focusing on core files and limiting diff sizes.
    Now with cleaner diff output.
    """
    commit_contents = {}
    
    # Extract username from the first repository's path structure
    username = None
    for repo in sources_data.values():
        if repo.get('structure', {}).get('name', ''):
            # Extract username from the repository name (format: username_reponame.git)
            username = repo['structure']['name'].split('_')[0]
            break
            
    if not username:
        raise ValueError("Could not determine username from repository structure")

    for repo_name in target_repos:
        # Store the full repo path but don't overwrite repo_name
        repo_path_name = sources_data[repo_name]['structure'].get('name', '')
        
        if not repo_path_name:
            print(f"Warning: No path found for repository {repo_name}")
            continue
        
        # Construct correct path using extracted username
        repo_path = f"out/{username}/{repo_path_name}"

        # Get core files from sources_data using original repo_name
        core_files = sources_data[repo_name].get("samples", {}).get("core_files", {})
        if not core_files:
            continue

        try:
            commits = []
            for file_path, _ in core_files.items():
                try:
                    # Get commit history for this file
                    commit_history = subprocess.check_output(
                        [
                            "git",
                            "log",
                            "--format=%H %ad",
                            "--date=iso",
                            "--reverse",
                            "--",
                            file_path,
                        ],
                        cwd=repo_path,
                        text=True,
                    ).splitlines()

                    # Process key commits
                    commits_to_process = []
                    if len(commit_history) > 0:
                        commits_to_process.append(commit_history[0])  # First commit
                    if len(commit_history) > 4:
                        # Add some middle commits, evenly spaced
                        middle_idx = len(commit_history) // 2
                        commits_to_process.append(commit_history[middle_idx])
                    if len(commit_history) > 1:
                        commits_to_process.append(commit_history[-1])  # Last commit

                    prev_content = None
                    for commit_info in commits_to_process:
                        sha, date = commit_info.split(" ", 1)
                        try:
                            # Get the diff for this commit
                            diff_output = subprocess.check_output(
                                ["git", "show", "--format=", sha, "--", file_path],
                                cwd=repo_path,
                                text=True,
                                stderr=subprocess.PIPE,
                            )

                            # Skip if diff is too large
                            diff_lines = diff_output.splitlines()
                            if len(diff_lines) > max_diff_lines:
                                continue

                            # Clean up the diff
                            clean_diff = _clean_diff(diff_output)
                            if not clean_diff.strip():
                                continue

                            # Get actual file content at this commit for first and last commit only
                            if prev_content is None:  # First commit
                                file_content = subprocess.check_output(
                                    ["git", "show", f"{sha}:{file_path}"],
                                    cwd=repo_path,
                                    text=True,
                                    stderr=subprocess.PIPE,
                                )
                                prev_content = file_content
                            elif commit_info == commits_to_process[-1]:  # Last commit
                                file_content = subprocess.check_output(
                                    ["git", "show", f"{sha}:{file_path}"],
                                    cwd=repo_path,
                                    text=True,
                                    stderr=subprocess.PIPE,
                                )
                            else:
                                file_content = None

                            commit_data = {
                                "sha": sha,
                                "date": date,
                                "file": file_path,
                                "changes": clean_diff,
                            }

                            if file_content:
                                commit_data["content"] = file_content

                            commits.append(commit_data)

                        except subprocess.CalledProcessError:
                            continue

                except subprocess.CalledProcessError:
                    continue

            if commits:
                # Sort commits by date
                commits.sort(key=lambda x: x["date"])

                # Group commits by file for better analysis
                files_commits = {}
                for commit in commits:
                    file_path = commit["file"]
                    if file_path not in files_commits:
                        files_commits[file_path] = []
                    files_commits[file_path].append(commit)

                commit_contents[repo_name] = {
                    "core_files": list(core_files.keys()),
                    "evolution": {
                        "commit_count": len(commits),
                        "commits_by_file": files_commits,
                    },
                }

                print(f"Processed {len(commits)} commits for {repo_name} core files")

        except Exception as e:
            print(f"Error analyzing repository {repo_name}: {str(e)}")
            continue

    return commit_contents

def _select_best_targets(
    sources_data: Dict[str, Any], commits: Dict[str, Any]
) -> List[str]:
    """Selects repositories with sufficient history for analysis"""
    targets = []

    for repo_name, repo_data in sources_data.items():
        if (
            len(commits.get(repo_name, [])) < 5
            or repo_data["file_stats"]["file_count"] < 10
        ):
            continue
        targets.append(repo_name)

    return targets


def _analyze_activity_patterns(commit_times: List[datetime]) -> Dict[str, Any]:
    """Analyzes commit timing patterns"""
    if not commit_times:
        return {
            "frequency": {
                "commits_per_day": 0,
                "active_hours": [],
                "timezone_hint": "unknown",
            },
            "burst_patterns": {
                "intensity": "low",
                "average_duration": "n/a",
                "frequency": "sporadic",
            },
        }

    # Sort commit times
    commit_times.sort()

    # Calculate commits per day
    days_span = (commit_times[-1] - commit_times[0]).days or 1
    commits_per_day = round(len(commit_times) / days_span, 2)

    # Analyze active hours
    hours = Counter([t.hour for t in commit_times])
    active_hours = [
        f"{h:02d}-{(h+1):02d}"
        for h, c in hours.most_common(3)
        if c > len(commit_times) * 0.1
    ]

    # Estimate timezone from most active hours
    # NOTE: Unclear should show the closest timezone
    peak_hour = max(hours.items(), key=lambda x: x[1])[0]
    if 4 <= peak_hour <= 8:
        tz_hint = "UTC+8 to UTC+10"
    elif 8 <= peak_hour <= 12:
        tz_hint = "UTC+0 to UTC+2"
    elif 12 <= peak_hour <= 16:
        tz_hint = "UTC-6 to UTC-4"
    elif 16 <= peak_hour <= 20:
        tz_hint = "UTC-12 to UTC-8"
    else:
        tz_hint = "unclear"

    # Analyze burst patterns
    time_diffs = []
    for i in range(1, len(commit_times)):
        diff = (commit_times[i] - commit_times[i - 1]).total_seconds() / 3600
        time_diffs.append(diff)

    if time_diffs:
        avg_diff = statistics.mean(time_diffs)
        if avg_diff < 1:
            intensity = "high"
        elif avg_diff < 4:
            intensity = "moderate"
        else:
            intensity = "low"

        burst_duration = (
            "few hours"
            if avg_diff < 4
            else "day-length" if avg_diff < 24 else "multi-day"
        )
        burst_frequency = (
            "frequent"
            if commits_per_day > 3
            else "regular" if commits_per_day > 1 else "sporadic"
        )
    else:
        intensity = "low"
        burst_duration = "n/a"
        burst_frequency = "sporadic"

    return {
        "frequency": {
            "commits_per_day": commits_per_day,
            "active_hours": active_hours,
            "timezone_hint": tz_hint,
        },
        "burst_patterns": {
            "intensity": intensity,
            "average_duration": burst_duration,
            "frequency": burst_frequency,
        },
    }
