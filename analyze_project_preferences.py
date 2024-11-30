import json
from typing import Dict, Any
from prompt_analyzer import create_handler

def analyze_project_preferences(sources_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyzes project preferences and technology choices using LLM"""
    
    handler = create_handler()
    combined_results = {}
    
    for repo_name, repo_data in sources_data.items():
        print(f"\nAnalyzing project preferences for repository: {repo_name}")
        
        # Create repository-specific prompt
        prompt = f"""
        
        PROJECT PREFERENCES ANALYSIS
        
        You are an expert in developer profiling and technical background analysis. Study this repository to build a comprehensive profile of the developer's technical preferences and knowledge domains.

        Repository: {repo_name}
        Languages: {repo_data.get('languages', 'Unknown')}
        
        Project Structure:
        {json.dumps(repo_data.get('structure', {}), indent=2)}
        
        Configuration Files:
        {json.dumps(repo_data.get('config_files', []), indent=2)}
        
        Core Files:
        {json.dumps(repo_data.get('samples', {}).get('core_files', {}), indent=2)}
        
        Dependencies:
        {json.dumps(repo_data.get('samples', {}).get('package_files', {}), indent=2)}

        Analyze deeply to infer:
        1. Technical background and expertise level
        2. Problem-solving approaches and mathematical foundations
        3. Security awareness and defensive programming practices
        4. Development environment preferences

        Generate detailed JSON analysis:
        {{
            "developer_profile": {{
                "expertise_domains": [
                    {{
                        "domain": string,  // e.g. "security", "data_science", "web_development"
                        "confidence": number,  // 0-100
                        "evidence": [string]
                    }}
                ],
                "knowledge_patterns": {{
                    "mathematical_foundations": [
                        {{
                            "area": string,  // e.g. "graph_theory", "linear_algebra"
                            "usage_examples": [string],
                            "proficiency_level": string  // "basic", "intermediate", "advanced"
                        }}
                    ],
                    "algorithmic_preferences": {{
                        "common_approaches": [string],
                        "complexity_awareness": string,
                        "optimization_patterns": [string]
                    }},
                    "security_awareness": {{
                        "level": string,  // "low", "medium", "high"
                        "defensive_patterns": [string],
                        "security_considerations": [string]
                    }}
                }}
            }},
            "technical_choices": {{
                "primary_languages": [
                    {{
                        "language": string,
                        "proficiency_indicators": [string],
                        "usage_patterns": [string]
                    }}
                ],
                "frameworks": [
                    {{
                        "name": string,
                        "purpose": string,
                        "usage_patterns": [string],
                        "implementation_depth": string  // "basic", "intermediate", "advanced"
                    }}
                ],
                "development_environment": {{
                    "likely_editor": string,
                    "confidence": number,
                    "tooling_preferences": [string],
                    "evidence": [string]
                }},
                "testing_approach": {{
                    "methodology": string,
                    "frameworks": [string],
                    "coverage_patterns": string
                }}
            }},
            "project_organization": {{
                "architecture_style": {{
                    "pattern": string,
                    "consistency": number,
                    "key_characteristics": [string]
                }},
                "code_quality": {{
                    "standards_adherence": string,
                    "documentation_level": string,
                    "maintainability_indicators": [string]
                }},
                "deployment_patterns": {{
                    "infrastructure_preferences": [string],
                    "containerization_approach": string,
                    "ci_cd_sophistication": string
                }}
            }}
        }}

        Important:
        1. Base all inferences on concrete evidence in the code
        2. Indicate confidence levels where uncertain
        3. Provide specific examples supporting each conclusion
        4. Focus on unique/distinctive patterns
        """


        try:
            result = handler.generate_json_response(prompt)
            if result:
                combined_results[repo_name] = result
        except Exception as e:
            print(f"Error analyzing {repo_name}: {str(e)}")
            combined_results[repo_name] = {"error": str(e)}

    
    return combined_results
