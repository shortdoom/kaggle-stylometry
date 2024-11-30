import json
from typing import Dict, Any
from prompt_analyzer import create_handler
from statistics import mean
from collections import Counter


def calculate_identity_confidence(
    sources_data: Dict[str, Any],
    code_style_results: Dict[str, Any],
    project_preferences: Dict[str, Any],
    temporal_patterns: Dict[str, Any]
) -> Dict[str, Any]:
    """Synthesizes all analysis results into a comprehensive developer identity profile"""

    handler = create_handler()

    # Create consolidated analysis data for the prompt
    analysis_data = {
        "repositories": sources_data,
        "code_style_analysis": code_style_results,
        "project_preferences": project_preferences,
        "temporal_patterns": temporal_patterns
    }
    

    prompt = f"""
    
    IDENTITY CONFIDENCE CALCULATION
    
    You are an expert in developer profiling and behavioral analysis. Synthesize all provided analysis data to create a comprehensive profile of the developer's identity, expertise, and behavioral patterns.

    Analysis Data:
    {json.dumps(analysis_data, indent=2)}

    Based on all provided repository data and previous analyses, create a detailed developer profile focusing on:
    1. Technical expertise and knowledge domains
    2. Problem-solving patterns and approaches
    3. Development philosophy and practices
    4. Unique identifiers and consistent traits

    Generate a single comprehensive identity profile JSON:
    
    {{
        "developer_profile": {{
            "expertise": {{
                "primary_domains": [
                    {{
                        "domain": string,
                        "proficiency_level": string,  // "beginner", "intermediate", "expert"
                        "evidence": [string],
                        "confidence": number  // 0-100
                    }}
                ],
                "technical_depth": {{
                    "languages": [
                        {{
                            "name": string,
                            "mastery_level": string,
                            "usage_patterns": [string],
                            "notable_practices": [string]
                        }}
                    ],
                    "frameworks": [
                        {{
                            "name": string,
                            "usage_sophistication": string,
                            "implementation_patterns": [string]
                        }}
                    ],
                    "specialized_knowledge": [
                        {{
                            "area": string,  // e.g. "cryptography", "distributed systems"
                            "depth": string,
                            "application_examples": [string]
                        }}
                    ]
                }}
            }},
            "work_patterns": {{
                "development_style": {{
                    "code_organization": string,
                    "problem_solving_approach": string,
                    "quality_focus": string,
                    "distinctive_habits": [string]
                }},
                "workflow_characteristics": {{
                    "development_cycle": string,
                    "testing_approach": string,
                    "refactoring_patterns": string,
                    "documentation_style": string
                }},
                "communication_style": {{
                    "code_commenting": string,
                    "commit_messages": string,
                    "documentation_quality": string
                }}
            }},
            "behavioral_traits": {{
                "strengths": [
                    {{
                        "trait": string,
                        "evidence": [string],
                        "consistency": number  // 0-100
                    }}
                ],
                "areas_for_improvement": [
                    {{
                        "area": string,
                        "indicators": [string]
                    }}
                ],
                "unique_characteristics": [
                    {{
                        "trait": string,
                        "significance": string,
                        "supporting_patterns": [string]
                    }}
                ]
            }},
            "knowledge_breadth": {{
                "technical_stack": {{
                    "preferred_technologies": [string],
                    "experience_indicators": [string],
                    "adoption_patterns": string
                }},
                "domain_knowledge": {{
                    "primary_domains": [string],
                    "depth_indicators": [string],
                    "application_examples": [string]
                }},
                "architectural_understanding": {{
                    "preferred_patterns": [string],
                    "complexity_handling": string,
                    "scalability_awareness": string
                }}
            }},
            "identity_confidence": {{
                "overall_score": number,  // 0-100
                "distinguishing_factors": [
                    {{
                        "factor": string,
                        "significance": string,
                        "supporting_evidence": [string]
                    }}
                ],
                "consistency_metrics": {{
                    "coding_style": number,  // 0-100
                    "problem_solving": number,  // 0-100
                    "quality_standards": number  // 0-100
                }},
                "pattern_reliability": {{
                    "stable_patterns": [string],
                    "variable_patterns": [string],
                    "context_dependencies": [string]
                }}
            }}
        }}
    }}

    Critical Analysis Requirements:
    1. Base all conclusions on concrete evidence from the provided data
    2. Focus on patterns that appear consistently across repositories
    3. Highlight unique traits that distinguish this developer
    4. Note any evolution in skills or practices
    5. Indicate confidence levels for all major conclusions
    6. Consider both technical and behavioral aspects
    7. Identify any potential biases or limitations in the analysis
    """
    
    try:
        result = handler.generate_json_response(prompt)
    except Exception as e:
        print(f"Error analyzing: {str(e)}")
    
    return result

