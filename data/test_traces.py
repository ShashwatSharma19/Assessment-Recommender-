"""Synthetic test traces for E2E evaluation."""

import json
from typing import List, Dict, Any

def create_test_traces() -> List[Dict[str, Any]]:
    """Create 10 synthetic test traces covering key scenarios."""
    return [
        {
            "id": "trace_001",
            "scenario": "Java Developer - Mid-level",
            "persona": "Hiring manager looking for mid-level Java backend developer",
            "facts": {
                "role": "Java developer",
                "seniority": "mid-level",
                "years_experience": 4,
                "focus": "backend",
            },
            "conversation": [
                {"role": "user", "content": "I'm hiring a Java developer"},
                {"role": "assistant", "content": "What seniority level?"},
                {"role": "user", "content": "Mid-level, around 4 years"},
            ],
            "expected_shortlist": ["java_8_new", "opq32r", "gsa"],
            "expected_test_types": ["K", "P", "C"],
        },
        {
            "id": "trace_002",
            "scenario": "Personality Assessment - Managers",
            "persona": "HR looking for personality test for manager hiring",
            "facts": {
                "role": "manager",
                "test_type": "personality",
                "focus": "leadership",
            },
            "conversation": [
                {"role": "user", "content": "Need personality assessment for manager candidates"},
                {"role": "assistant", "content": "What seniority level?"},
                {"role": "user", "content": "Senior managers"},
            ],
            "expected_shortlist": ["opq32r", "opq_pro", "emotional_intelligence"],
            "expected_test_types": ["P"],
        },
        {
            "id": "trace_003",
            "scenario": "Cognitive Ability - Analysts",
            "persona": "Recruiter for analyst positions",
            "facts": {
                "role": "analyst",
                "test_type": "cognitive",
                "domains": ["numerical", "logical"],
            },
            "conversation": [
                {"role": "user", "content": "Analyst role - need cognitive reasoning tests"},
                {"role": "assistant", "content": "What type of analysis will they do?"},
                {"role": "user", "content": "Data analysis with reporting"},
            ],
            "expected_shortlist": ["mq_numerical", "mq_logical", "data_analytics"],
            "expected_test_types": ["C", "K"],
        },
        {
            "id": "trace_004",
            "scenario": "Python Developer - Junior",
            "persona": "Tech lead hiring junior Python developers",
            "facts": {
                "role": "Python developer",
                "seniority": "junior",
                "years_experience": 0,
            },
            "conversation": [
                {"role": "user", "content": "Python developer junior level"},
            ],
            "expected_shortlist": ["python_new", "mq_logical", "gsa"],
            "expected_test_types": ["K", "C"],
        },
        {
            "id": "trace_005",
            "scenario": "Full-Stack Developer - Senior",
            "persona": "CTO hiring senior full-stack engineers",
            "facts": {
                "role": "full-stack developer",
                "seniority": "senior",
                "years_experience": 8,
                "skills": ["javascript", "react", "backend"],
            },
            "conversation": [
                {"role": "user", "content": "Senior full-stack developer"},
                {"role": "assistant", "content": "What's their backend focus?"},
                {"role": "user", "content": "Node.js and JavaScript ecosystem"},
            ],
            "expected_shortlist": ["javascript_new", "react_new", "opq32r"],
            "expected_test_types": ["K", "P"],
        },
        {
            "id": "trace_006",
            "scenario": "Vague Query - Clarification Needed",
            "persona": "General HR person, unsure what they need",
            "facts": {
                "initial_query": "vague",
                "eventually_clarifies": True,
            },
            "conversation": [
                {"role": "user", "content": "I need an assessment"},
                {"role": "assistant", "content": "I'd like to help you find the right assessment. What role or position are you hiring for?"},
                {"role": "user", "content": "Sales representative"},
                {"role": "assistant", "content": "What seniority level?"},
                {"role": "user", "content": "Entry level"},
            ],
            "expected_shortlist": ["gsa", "sjt_customer_service", "opq32r"],
            "expected_test_types": ["C", "P"],
        },
        {
            "id": "trace_007",
            "scenario": "DevOps Engineer - Cloud Focus",
            "persona": "Infrastructure team hiring DevOps engineer",
            "facts": {
                "role": "DevOps engineer",
                "focus": "cloud infrastructure",
                "technologies": ["AWS", "Docker", "Kubernetes"],
            },
            "conversation": [
                {"role": "user", "content": "DevOps engineer with AWS and Docker experience"},
            ],
            "expected_shortlist": ["aws_solutions_architect", "docker_kubernetes"],
            "expected_test_types": ["K"],
        },
        {
            "id": "trace_008",
            "scenario": "Data Scientist - ML Focus",
            "persona": "Data team hiring data scientist",
            "facts": {
                "role": "data scientist",
                "focus": "machine learning",
                "skills": ["Python", "SQL", "statistical analysis"],
            },
            "conversation": [
                {"role": "user", "content": "Data scientist Python SQL machine learning"},
            ],
            "expected_shortlist": ["python_new", "sql_new", "data_analytics"],
            "expected_test_types": ["K"],
        },
        {
            "id": "trace_009",
            "scenario": "Refinement - Add Personality Test",
            "persona": "Hiring manager initially focused on technical, adds personality",
            "facts": {
                "role": "engineer",
                "initial_focus": "technical",
                "refinement": "add personality assessment",
            },
            "conversation": [
                {"role": "user", "content": "Engineer technical assessment"},
                {"role": "assistant", "content": "What type of engineering?"},
                {"role": "user", "content": "Actually, also add personality tests"},
            ],
            "expected_shortlist": ["opq32r", "emotional_intelligence"],
            "expected_test_types": ["P"],
        },
        {
            "id": "trace_010",
            "scenario": "C# Developer - .NET Stack",
            "persona": "Windows/.NET team hiring C# developer",
            "facts": {
                "role": "C# developer",
                "stack": ".NET",
                "seniority": "mid-level",
            },
            "conversation": [
                {"role": "user", "content": "C# developer mid-level .NET"},
            ],
            "expected_shortlist": ["csharp_new", "opq32r"],
            "expected_test_types": ["K", "P"],
        },
    ]


def save_test_traces(output_path: str = "data/test_traces.json"):
    """Save test traces to JSON file."""
    traces = create_test_traces()
    with open(output_path, 'w') as f:
        json.dump({"traces": traces}, f, indent=2)
    print(f"Saved {len(traces)} test traces to {output_path}")
    return traces


if __name__ == "__main__":
    save_test_traces()
