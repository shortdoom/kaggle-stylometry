from typing import Dict, Any, List, Tuple, Iterator
import json
from prompt_analyzer import create_handler


def analyze_code_style(sources_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes developer's coding style patterns for stylometric analysis"""

    handler = create_handler()
    combined_results = {}

    for repo_name, repo_data in sources_data.items():
        print(f"\nAnalyzing repository: {repo_name}")

        prompt = f"""
        
        CODE STYLE ANALYSIS
        
        You are an expert in code stylometry and developer behavior analysis. Analyze this repository to create a detailed profile of the developer's coding patterns, preferences, and habits.

        Repository: {repo_name}

        Code samples and structure:
        {json.dumps(repo_data, indent=2)}

        Focus on identifying unique, individual coding patterns that could distinguish this developer's style. Analyze how they:
        - Structure their code and control flow
        - Handle data and state
        - Approach problem-solving
        - Maintain code quality
        - Handle edge cases and errors

        IMPORTANT CONSTRAINTS:
        - Maximum 10 patterns per list category
        - No repeating similar patterns
        - Use "Unknown" if pattern cannot be determined
        - Focus on distinctive, personal coding traits
        
        Generate a JSON profile with this EXACT structure:

        {{
            "code_organization": {{
                "file_structure": {{
                    "preferred_file_size": number,  // Average lines per file
                    "module_organization": string,  // e.g. "feature-based", "layer-based", "domain-based"
                    "separation_patterns": [string]  // Common ways they separate concerns
                }},
                "code_layout": {{
                    "indentation": {{ "type": string, "width": number }},
                    "line_length": {{ "average": number, "max_observed": number }},
                    "spacing_style": {{
                        "around_operators": string,
                        "after_commas": boolean,
                        "around_blocks": string
                    }}
                }}
            }},
            "naming_patterns": {{
                "variables": {{
                    "primary_style": string,  // e.g. "snake_case", "camelCase"
                    "consistency_score": number,  // 0-100
                    "length_preference": {{ "average": number, "range": [number, number] }},
                    "semantic_patterns": [string]  // How they choose names, e.g. "verb_noun_pairs", "hungarian_notation"
                }},
                "functions": {{
                    "primary_style": string,
                    "common_prefixes": [string],
                    "common_patterns": [string],
                    "length_preference": {{ "average": number, "range": [number, number] }}
                }}
            }},
            "coding_patterns": {{
                "control_flow": {{
                    "preferred_loop_type": string,  // e.g. "for", "while", "comprehension"
                    "nesting_depth": {{ "average": number, "max_observed": number }},
                    "branching_patterns": [string],  // e.g. "early returns", "guard clauses"
                    "condition_complexity": {{ "average": number, "max_observed": number }}
                }},
                "data_handling": {{
                    "preferred_structures": [string],  // Favorite data structures
                    "mutation_patterns": {{
                        "prefers_immutable": boolean,
                        "common_patterns": [string]
                    }},
                    "state_management": {{
                        "approach": string,  // e.g. "functional", "stateful", "mixed"
                        "patterns": [string]
                    }}
                }}
            }},
            "error_handling": {{
                "strategy": string,  // e.g. "defensive", "fail-fast", "hybrid"
                "patterns": [string],  // Common error handling patterns
                "error_checking": {{
                    "input_validation": boolean,
                    "null_checking": boolean,
                    "type_checking": boolean
                }}
            }},
            "code_quality": {{
                "documentation": {{
                    "style": string,  // e.g. "detailed", "minimal", "moderate"
                    "coverage_ratio": number,  // 0-100
                    "preferred_formats": [string]
                }},
                "testing": {{
                    "approach": string,  // e.g. "unit-heavy", "integration-focused", "minimal"
                    "patterns": [string]
                }},
                "complexity_metrics": {{
                    "cyclomatic_complexity": {{ "average": number, "max_observed": number }},
                    "cognitive_complexity": {{ "average": number, "max_observed": number }}
                }}
            }},
            "distinctive_traits": {{
                "unique_patterns": [string],  // Highly individual coding patterns
                "favored_techniques": [string],  // Preferred coding approaches
                "consistent_habits": [string]  // Reliable behavioral patterns
            }}
        }}

        Critical requirements:
        1. OUTPUT ONLY VALID JSON
        2. NO markdown, NO comments, NO explanations
        3. Use EXACT key names shown
        4. All arrays MAXIMUM 10 items
        5. Use numbers for metrics where specified
        6. Use "Unknown" for undeterminable values
        """

        try:
            result = handler.generate_json_response(prompt)
            if result:
                combined_results[repo_name] = result                    
        except Exception as e:
            print(f"Error analyzing {repo_name}: {str(e)}")
            combined_results[repo_name] = {"error": str(e)}

    return combined_results