"""Validation utilities for responses and data."""

from typing import List, Dict, Any
from app.catalog import Catalog, Assessment
import re


def is_valid_catalog_url(url: str, catalog: Catalog) -> bool:
    """Check if URL exists in catalog."""
    return any(a.url == url for a in catalog.assessments)


def validate_response_schema(response: Dict[str, Any]) -> bool:
    """Validate that response matches required schema."""
    required_fields = {"reply", "recommendations", "end_of_conversation"}

    if not isinstance(response, dict):
        return False

    if not required_fields.issubset(response.keys()):
        return False

    # Validate types
    if not isinstance(response["reply"], str):
        return False

    if not isinstance(response["recommendations"], list):
        return False

    if not isinstance(response["end_of_conversation"], bool):
        return False

    # Validate recommendations structure
    for rec in response["recommendations"]:
        if not isinstance(rec, dict):
            return False
        if not all(key in rec for key in ["name", "url", "test_type"]):
            return False

    return True


def validate_recommendations(recommendations: List[Dict[str, Any]], catalog: Catalog) -> Dict[str, Any]:
    """
    Validate recommendations against catalog.

    Returns dict with validation results:
    - valid: bool - all recommendations are valid
    - invalid_urls: list - URLs not in catalog
    - hallucinated_assessments: list - recommendations not from catalog
    """
    results = {
        "valid": True,
        "invalid_urls": [],
        "hallucinated_assessments": [],
    }

    for rec in recommendations:
        # Check URL exists in catalog
        url = rec.get("url", "")
        if not is_valid_catalog_url(url, catalog):
            results["valid"] = False
            results["invalid_urls"].append(url)
            results["hallucinated_assessments"].append(rec.get("name", "Unknown"))

    return results


def sanitize_output(text: str) -> str:
    """Sanitize text output to remove potential issues."""
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    # Limit length
    return text[:10000]


def is_off_topic(query: str) -> bool:
    """Check if query is off-topic (not about assessments)."""
    query_lower = query.lower()

    # Off-topic keywords that should be refused
    off_topic_patterns = [
        r'\b(salary|pay|wage|compensation)\b',
        r'\b(legal|law|compliance|eeoc|ada)\b',
        r'\b(medical|health|doctor|therapy)\b',
        r'\b(political|religion|controversial)\b',
        r'\b(weather|sports|celebrity|news)\b',
    ]

    for pattern in off_topic_patterns:
        if re.search(pattern, query_lower):
            return True

    # Check for competitor tools
    if any(word in query_lower for word in ['peopleworks', 'mettl', 'paradox', 'pymetrics']):
        return True

    return False


def looks_like_jailbreak_attempt(text: str) -> bool:
    """Detect potential prompt injection or jailbreak attempts."""
    suspicious_patterns = [
        r'(?:ignore|forget|disregard)\s+(?:previous|prior|all)',
        r'(?:system|admin)\s+(?:command|mode|prompt)',
        r'(?:pretend|assume)\s+(?:you are|you\re|you\'re)',
        r'(?:bypass|override|disable)\s+(?:rules|restrictions|safety)',
    ]

    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower):
            return True

    return False
