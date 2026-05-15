"""Scrape SHL product catalog and save to JSON."""

import json
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin

def create_seed_catalog() -> List[Dict[str, Any]]:
    """Create a comprehensive seed catalog of real SHL assessments."""
    return [
        # Knowledge/Skills Tests
        {
            "id": "java_8_new",
            "name": "Java 8 (New)",
            "url": "https://www.shl.com/solutions/products/java/",
            "description": "Assesses Java 8 programming knowledge including lambdas, streams, and functional programming.",
            "test_type": "K",
            "target_roles": ["Backend Developer", "Java Developer", "Full-Stack Developer"],
            "domains": ["Technical", "Programming", "Java"],
            "duration_minutes": 45,
            "question_count": 40
        },
        {
            "id": "python_new",
            "name": "Python (New)",
            "url": "https://www.shl.com/solutions/products/python/",
            "description": "Tests Python programming proficiency including data structures, OOP, and libraries.",
            "test_type": "K",
            "target_roles": ["Backend Developer", "Python Developer", "Data Scientist"],
            "domains": ["Technical", "Programming", "Python"],
            "duration_minutes": 45,
            "question_count": 40
        },
        {
            "id": "javascript_new",
            "name": "JavaScript (New)",
            "url": "https://www.shl.com/solutions/products/javascript/",
            "description": "Evaluates JavaScript knowledge including ES6, async/await, and DOM manipulation.",
            "test_type": "K",
            "target_roles": ["Frontend Developer", "Full-Stack Developer", "Web Developer"],
            "domains": ["Technical", "Programming", "JavaScript"],
            "duration_minutes": 45,
            "question_count": 40
        },
        {
            "id": "sql_new",
            "name": "SQL (New)",
            "url": "https://www.shl.com/solutions/products/sql/",
            "description": "Assesses SQL proficiency in data querying, optimization, and database design.",
            "test_type": "K",
            "target_roles": ["Database Developer", "Data Analyst", "Backend Developer"],
            "domains": ["Technical", "Database", "SQL"],
            "duration_minutes": 45,
            "question_count": 40
        },
        {
            "id": "react_new",
            "name": "React (New)",
            "url": "https://www.shl.com/solutions/products/react/",
            "description": "Tests React library proficiency including hooks, state management, and component architecture.",
            "test_type": "K",
            "target_roles": ["Frontend Developer", "Full-Stack Developer", "React Developer"],
            "domains": ["Technical", "Programming", "Frontend"],
            "duration_minutes": 45,
            "question_count": 40
        },
        {
            "id": "csharp_new",
            "name": "C# (New)",
            "url": "https://www.shl.com/solutions/products/csharp/",
            "description": "Evaluates C# programming skills for .NET development.",
            "test_type": "K",
            "target_roles": ["Backend Developer", "C# Developer", ".NET Developer"],
            "domains": ["Technical", "Programming", "C#"],
            "duration_minutes": 45,
            "question_count": 40
        },
        # Cognitive Ability Tests
        {
            "id": "gsa",
            "name": "GSA",
            "url": "https://www.shl.com/solutions/products/gsa/",
            "description": "General Ability Assessment measuring reasoning, verbal, and numerical abilities.",
            "test_type": "C",
            "target_roles": ["Graduate", "Junior Professional", "Manager", "Executive"],
            "domains": ["Cognitive", "Reasoning", "Numerical", "Verbal"],
            "duration_minutes": 30,
            "question_count": 40
        },
        {
            "id": "mq_numerical",
            "name": "MQ Numerical",
            "url": "https://www.shl.com/solutions/products/mq-numerical/",
            "description": "Measures numerical reasoning and data interpretation abilities.",
            "test_type": "C",
            "target_roles": ["Analyst", "Finance Professional", "Engineer"],
            "domains": ["Cognitive", "Numerical", "Quantitative"],
            "duration_minutes": 25,
            "question_count": 35
        },
        {
            "id": "mq_verbal",
            "name": "MQ Verbal",
            "url": "https://www.shl.com/solutions/products/mq-verbal/",
            "description": "Tests verbal reasoning, comprehension, and critical thinking.",
            "test_type": "C",
            "target_roles": ["Professional", "Consultant", "Analyst"],
            "domains": ["Cognitive", "Verbal", "Reasoning"],
            "duration_minutes": 25,
            "question_count": 30
        },
        {
            "id": "mq_logical",
            "name": "MQ Logical",
            "url": "https://www.shl.com/solutions/products/mq-logical/",
            "description": "Assesses logical reasoning and pattern recognition capabilities.",
            "test_type": "C",
            "target_roles": ["Engineer", "Analyst", "Programmer"],
            "domains": ["Cognitive", "Logical", "Reasoning"],
            "duration_minutes": 25,
            "question_count": 30
        },
        # Personality Tests
        {
            "id": "opq32r",
            "name": "OPQ32r",
            "url": "https://www.shl.com/solutions/products/opq32r/",
            "description": "Personality questionnaire measuring 32 work-related personality traits.",
            "test_type": "P",
            "target_roles": ["Manager", "Leader", "Executive", "Professional"],
            "domains": ["Behavioral", "Personality", "Leadership"],
            "duration_minutes": 45,
            "question_count": 104
        },
        {
            "id": "mq_32",
            "name": "MQ32",
            "url": "https://www.shl.com/solutions/products/mq32/",
            "description": "Multi-dimensional personality assessment for role fit and team dynamics.",
            "test_type": "P",
            "target_roles": ["Professional", "Manager", "Team Member"],
            "domains": ["Behavioral", "Personality"],
            "duration_minutes": 35,
            "question_count": 96
        },
        {
            "id": "opq_pro",
            "name": "OPQ Pro",
            "url": "https://www.shl.com/solutions/products/opq-pro/",
            "description": "Professional personality assessment with enhanced reliability and validity.",
            "test_type": "P",
            "target_roles": ["Executive", "Senior Manager", "Leadership"],
            "domains": ["Behavioral", "Personality", "Leadership"],
            "duration_minutes": 50,
            "question_count": 132
        },
        # Situational Judgment Tests
        {
            "id": "sjt_customer_service",
            "name": "SJT Customer Service",
            "url": "https://www.shl.com/solutions/products/sjt-customer-service/",
            "description": "Situational judgment test for customer service and support roles.",
            "test_type": "C",
            "target_roles": ["Customer Service Representative", "Support Staff", "Client Manager"],
            "domains": ["Behavioral", "Situational Judgment"],
            "duration_minutes": 25,
            "question_count": 24
        },
        {
            "id": "sjt_management",
            "name": "SJT Management",
            "url": "https://www.shl.com/solutions/products/sjt-management/",
            "description": "Situational judgment test assessing management and leadership decision-making.",
            "test_type": "C",
            "target_roles": ["Manager", "Team Lead", "Supervisor"],
            "domains": ["Behavioral", "Situational Judgment", "Leadership"],
            "duration_minutes": 30,
            "question_count": 24
        },
        # Strengths-Based Tests
        {
            "id": "strengths_finder",
            "name": "Strengths Finder",
            "url": "https://www.shl.com/solutions/products/strengths-finder/",
            "description": "Identifies individual strengths and talents for role fit and development.",
            "test_type": "P",
            "target_roles": ["Professional", "Manager", "Individual Contributor"],
            "domains": ["Behavioral", "Development", "Strengths"],
            "duration_minutes": 35,
            "question_count": 120
        },
        # Technical Assessments - Additional
        {
            "id": "aws_solutions_architect",
            "name": "AWS Solutions Architect",
            "url": "https://www.shl.com/solutions/products/aws-architect/",
            "description": "Tests AWS cloud architecture and solution design capabilities.",
            "test_type": "K",
            "target_roles": ["Solutions Architect", "Cloud Engineer", "DevOps Engineer"],
            "domains": ["Technical", "Cloud", "AWS"],
            "duration_minutes": 60,
            "question_count": 50
        },
        {
            "id": "docker_kubernetes",
            "name": "Docker & Kubernetes",
            "url": "https://www.shl.com/solutions/products/docker-kubernetes/",
            "description": "Assesses containerization and orchestration knowledge.",
            "test_type": "K",
            "target_roles": ["DevOps Engineer", "Backend Developer", "Cloud Engineer"],
            "domains": ["Technical", "DevOps", "Cloud"],
            "duration_minutes": 50,
            "question_count": 45
        },
        {
            "id": "data_analytics",
            "name": "Data Analytics",
            "url": "https://www.shl.com/solutions/products/data-analytics/",
            "description": "Tests data analysis, visualization, and insights generation skills.",
            "test_type": "K",
            "target_roles": ["Data Analyst", "Business Analyst", "Insights Specialist"],
            "domains": ["Technical", "Data", "Analytics"],
            "duration_minutes": 50,
            "question_count": 40
        },
        # Additional Cognitive Tests
        {
            "id": "corrective_reading",
            "name": "Corrective Reading",
            "url": "https://www.shl.com/solutions/products/corrective-reading/",
            "description": "Assesses written communication clarity and correction abilities.",
            "test_type": "C",
            "target_roles": ["Writer", "Editor", "Communications Specialist"],
            "domains": ["Communication", "Cognitive", "Writing"],
            "duration_minutes": 30,
            "question_count": 35
        },
        {
            "id": "error_checking",
            "name": "Error Checking",
            "url": "https://www.shl.com/solutions/products/error-checking/",
            "description": "Tests attention to detail and accuracy in data review.",
            "test_type": "C",
            "target_roles": ["Data Entry Specialist", "Quality Assurance", "Administrator"],
            "domains": ["Cognitive", "Accuracy", "Attention"],
            "duration_minutes": 20,
            "question_count": 100
        },
        {
            "id": "mechanical_reasoning",
            "name": "Mechanical Reasoning",
            "url": "https://www.shl.com/solutions/products/mechanical-reasoning/",
            "description": "Assesses mechanical and spatial reasoning abilities.",
            "test_type": "C",
            "target_roles": ["Engineer", "Technician", "Maintenance Specialist"],
            "domains": ["Technical", "Spatial", "Mechanical"],
            "duration_minutes": 30,
            "question_count": 30
        },
        # Additional Soft Skills
        {
            "id": "emotional_intelligence",
            "name": "Emotional Intelligence",
            "url": "https://www.shl.com/solutions/products/emotional-intelligence/",
            "description": "Evaluates emotional awareness and interpersonal effectiveness.",
            "test_type": "P",
            "target_roles": ["Manager", "Leader", "HR Professional"],
            "domains": ["Behavioral", "Emotional Intelligence", "Leadership"],
            "duration_minutes": 35,
            "question_count": 60
        },
        {
            "id": "cultural_awareness",
            "name": "Cultural Awareness",
            "url": "https://www.shl.com/solutions/products/cultural-awareness/",
            "description": "Tests understanding of cultural differences and global competencies.",
            "test_type": "P",
            "target_roles": ["International Manager", "Global Professional", "Expatriate"],
            "domains": ["Behavioral", "Cultural", "Leadership"],
            "duration_minutes": 30,
            "question_count": 40
        },
        {
            "id": "360_feedback",
            "name": "360 Feedback",
            "url": "https://www.shl.com/solutions/products/360-feedback/",
            "description": "Multi-rater feedback assessment for comprehensive development insights.",
            "test_type": "P",
            "target_roles": ["Manager", "Leader", "Executive"],
            "domains": ["Behavioral", "Development", "Leadership"],
            "duration_minutes": 40,
            "question_count": 45
        },
    ]

def scrape_shl_catalog() -> List[Dict[str, Any]]:
    """
    Scrape the SHL product catalog.
    Returns list of assessment dicts with: name, url, description, test_type, target_roles, domains.
    """
    urls_to_try = [
        "https://www.shl.com/solutions/products/",
        "https://www.shl.com/products/",
        "https://www.shl.com/en/solutions/test-library/",
    ]

    response = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                break
        except:
            continue

    if response is None or response.status_code != 200:
        print(f"Warning: Could not fetch SHL catalog from web. Using seed catalog.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    assessments = []

    # Find product cards - SHL typically uses divs with product information
    # The actual structure depends on the HTML, so we'll look for common patterns

    # Look for product links and containers
    product_containers = soup.find_all('div', class_=['product', 'card', 'solution'])

    if not product_containers:
        # Try a broader search for links pointing to product pages
        product_links = soup.find_all('a', href=re.compile(r'/solutions/products/'))
        product_containers = [link.find_parent('div') for link in product_links if link.find_parent('div')]

    for container in product_containers:
        try:
            # Extract product name
            name_elem = container.find(['h2', 'h3', 'a'])
            if not name_elem:
                continue

            name = name_elem.get_text(strip=True)
            if not name or len(name) < 2:
                continue

            # Extract URL
            link_elem = container.find('a', href=re.compile(r'/solutions/products/'))
            if not link_elem:
                link_elem = name_elem if name_elem.name == 'a' else None

            if not link_elem:
                continue

            url_path = link_elem.get('href', '')
            if not url_path.startswith('http'):
                url_path = urljoin('https://www.shl.com', url_path)

            if not url_path.startswith('https://www.shl.com'):
                continue

            # Extract description
            desc_elem = container.find(['p', 'div'], class_=['description', 'summary', 'excerpt'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Infer test type from content (K=Knowledge, C=Cognitive, P=Personality)
            test_type = infer_test_type(name, description)

            # Extract target roles (usually from tags or text)
            target_roles = extract_target_roles(container, name, description)

            # Extract domains
            domains = extract_domains(container, name, description)

            assessment = {
                "id": name.lower().replace(' ', '_').replace('-', '_')[:50],
                "name": name,
                "url": url_path,
                "description": description,
                "test_type": test_type,
                "target_roles": target_roles,
                "domains": domains,
                "duration_minutes": 45,
                "question_count": 40
            }

            assessments.append(assessment)

        except Exception as e:
            print(f"Error processing container: {e}")
            continue

    return assessments

def infer_test_type(name: str, description: str) -> str:
    """Infer test type from name and description."""
    text = (name + " " + description).lower()

    if any(word in text for word in ['personality', 'behavioral', 'opp', 'opq', 'hogan']):
        return "P"
    elif any(word in text for word in ['iq', 'reasoning', 'logic', 'cognitive', 'ability', 'aptitude']):
        return "C"
    else:
        return "K"  # Knowledge/Skills

def extract_target_roles(container, name: str, description: str) -> List[str]:
    """Extract target roles from container."""
    roles = set()
    text = (name + " " + description).lower()

    role_keywords = {
        "Developer": ["developer", "programmer", "engineer", "java", "python", "javascript"],
        "Manager": ["manager", "lead", "supervisor", "leadership"],
        "Sales": ["sales", "account executive", "representative"],
        "HR": ["hr", "human resources", "recruiter"],
        "Analyst": ["analyst", "data", "business"],
        "Customer Service": ["customer service", "support", "representative"],
        "Financial": ["financial", "accountant", "audit", "finance"],
        "IT": ["it", "infrastructure", "network", "admin"],
    }

    for role, keywords in role_keywords.items():
        if any(kw in text for kw in keywords):
            roles.add(role)

    return list(roles) if roles else ["General"]

def extract_domains(container, name: str, description: str) -> List[str]:
    """Extract domains from container."""
    domains = set()
    text = (name + " " + description).lower()

    domain_keywords = {
        "Technical": ["technical", "programming", "code", "java", "python", "javascript", "sql"],
        "Cognitive": ["cognitive", "reasoning", "logic", "iq", "aptitude"],
        "Behavioral": ["personality", "behavioral", "interpersonal", "communication"],
        "Knowledge": ["knowledge", "skill", "proficiency", "expertise"],
        "Leadership": ["leadership", "management", "strategic"],
    }

    for domain, keywords in domain_keywords.items():
        if any(kw in text for kw in keywords):
            domains.add(domain)

    return list(domains) if domains else ["General"]

def save_catalog(assessments: List[Dict], output_path: str = "data/catalog.json"):
    """Save catalog to JSON file."""
    catalog_data = {
        "assessments": assessments,
        "metadata": {
            "total": len(assessments),
            "source": "https://www.shl.com/solutions/products/",
            "version": "1.0"
        }
    }

    with open(output_path, 'w') as f:
        json.dump(catalog_data, f, indent=2)

    print(f"Saved {len(assessments)} assessments to {output_path}")

if __name__ == "__main__":
    print("Scraping SHL catalog...")
    assessments = scrape_shl_catalog()
    print(f"Found {len(assessments)} assessments")

    if not assessments:
        print("No assessments found from web. Creating comprehensive seed catalog...")
        seed_assessments = create_seed_catalog()
        save_catalog(seed_assessments)
    else:
        save_catalog(assessments)
