from typing import Dict, List, Any
from pathlib import Path
import json
import time
import argparse
from analyze_repository_structure import analyze_repository_structure
from analyze_code_style import analyze_code_style
from analyze_temportal_patterns import analyze_temporal_patterns
from analyze_project_preferences import analyze_project_preferences
from calculate_identity_confidence import calculate_identity_confidence
from repository_selector import RepositorySelector


class StyleAnalyzer:
    """Handles repository analysis and stylometric profiling"""

    def __init__(self, base_path: str, username: str, selector: str = "repo_selector"):
        self.base_path = Path(base_path)
        self.username = username
        self.user_path = self.base_path / username
        self.report_path = self.user_path / "report.json"
        self.output_data = {}
        self.start_time = time.time()

        self.code_style = {}
        self.temporal_patterns = {}
        self.project_preferences = {}
        self.identity_confidence = {}

        print(f"\n{'='*60}")
        print(f"Starting analysis for user: {username}")
        print(f"{'='*60}\n")

        try:
            print("Loading report data...")
            self.report_data = self._load_report()
            print("✓ Report data loaded successfully")
        except Exception as e:
            raise ValueError(f"Error loading report data: {str(e)}")

        try:
            print("\nIdentifying repositories to analyze...")
            
            if selector == "repo_selector":
                # Use the RepositorySelector class to select repositories for analysis
                print("Using RepositorySelector for repository selection")
                self.repo_selector = RepositorySelector(base_path, username)
                self.sources_to_analyze = self.repo_selector.select_repositories(self.report_data)
            else:
                # Only single-contributor (owner) repos are considered
                print("Using default repository selection method")
                self.sources_to_analyze = self._get_sources_to_analyze()
            
            print(f"✓ Found {len(self.sources_to_analyze)} repositories to analyze")
            for repo in self.sources_to_analyze:
                print(f"  - {repo}")
        except Exception as e:
            raise ValueError(f"Error getting sources to analyze: {str(e)}")

        try:
            print("\nAnalyzing repository structure...")
            self.sources_data = analyze_repository_structure(
                self.sources_to_analyze, self.user_path
            )

            output_path = self.user_path / "stylometry_repo_structure.json"
            with open(output_path, "w") as f:
                json.dump({"stylometry_repo_structure": self.sources_data}, f, indent=2)
            print("✓ Repository structure analysis complete")
        except Exception as e:
            raise ValueError(f"Error processing source code: {str(e)}")

    def _load_report(self) -> Dict:
        """Loads the report.json file"""
        with open(self.report_path) as f:
            return json.load(f)
        
    def _get_sources_to_analyze(self) -> List[str]:
        """Gets list of repositories to analyze. Only single-contributor repos are considered"""
        return [
            obj["repo"]
            for obj in self.report_data.get("contributors", [])
            if obj["contributors"][0] == self.username and len(obj["contributors"]) == 1
        ]
        
    def analyze(self) -> Dict[str, Any]:
        """Performs complete stylometric analysis"""

        if not self.sources_data:
            return {
                "error": "self.sources_data input required for stylometric analysis."
            }

        print("\nStarting comprehensive analysis...")

        print("\nAnalyzing code style patterns...")
        self.code_style = self._analyze_code_style()
        print("✓ Code style analysis complete")

        print("\nAnalyzing temporal patterns...")
        self.temporal_patterns = self._analyze_temporal_patterns()
        print("✓ Temporal patterns analysis complete")

        print("\nAnalyzing project preferences...")
        self.project_preferences = self._analyze_project_preferences()
        print("✓ Project preferences analysis complete")

        print("\nCalculating identity confidence...")
        self.identity_confidence = self._calculate_identity_confidence()
        print("✓ Identity confidence calculation complete")

        return {
            "code_style_metrics": self.code_style,
            "temporal_patterns": self.temporal_patterns,
            "project_preferences": self.project_preferences,
            "identity_confidence": self.identity_confidence,
        }

    def _analyze_code_style(self) -> Dict[str, Any]:
        """Analyzes code style patterns using LLM"""
        return analyze_code_style(self.sources_data)

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyzes commit patterns and timing. No LLM usage."""
        return analyze_temporal_patterns(self.sources_data, self.report_data)

    def _analyze_project_preferences(self) -> Dict[str, Any]:
        """Analyzes technology choices and project patterns"""
        return analyze_project_preferences(self.sources_data)

    def _calculate_identity_confidence(self) -> Dict[str, Any]:
        """Calculates confidence scores for identity patterns"""
        return calculate_identity_confidence(
            self.sources_data,
            self.code_style,
            self.project_preferences,
            self.temporal_patterns,
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generates complete stylometric report"""
        analysis = self.analyze()
        output_path = self.user_path / "stylometry_profile.json"

        print("\nGenerating final report...")
        with open(output_path, "w") as f:
            json.dump({"stylometric_profile": analysis}, f, indent=2)
        print("✓ Report generated successfully")

        elapsed_time = time.time() - self.start_time
        print(f"\n{'='*60}")
        print(f"Analysis completed in {elapsed_time:.2f} seconds")
        print(f"{'='*60}")

        return analysis


def main():
    parser = argparse.ArgumentParser(
        description='Analyze coding style patterns for a given GitHub username'
    )
    parser.add_argument(
        'username',
        type=str,
        help='GitHub username to analyze'
    )
    parser.add_argument(
        '--base-path',
        type=str,
        default='out',
        help='Base path for analysis output (default: out)'
    )
    parser.add_argument(
        '--selector',
        type=str,
        default='repo_selector',
        choices=['repo_selector', 'default'],
        help='Repository selection method (default: repo_selector)'
    )

    args = parser.parse_args()
    
    analyzer = StyleAnalyzer(args.base_path, args.username, args.selector)
    analyzer.generate_report()
    print(f"Generated stylometric profile for {args.username}")


if __name__ == "__main__":
    main()