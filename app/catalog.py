"""Load and manage the SHL assessment catalog."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class Assessment(BaseModel):
    """Single assessment in the catalog."""
    id: str
    name: str
    url: str
    description: str
    test_type: str  # K = Knowledge, C = Cognitive, P = Personality
    target_roles: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    duration_minutes: int = 45
    question_count: int = 40

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith('https://www.shl.com/'):
            raise ValueError('URL must start with https://www.shl.com/')
        return v

    @validator('test_type')
    def validate_test_type(cls, v):
        if v not in ['K', 'C', 'P']:
            raise ValueError('test_type must be K, C, or P')
        return v


class Catalog(BaseModel):
    """Complete assessment catalog."""
    assessments: List[Assessment]
    metadata: Optional[Dict[str, Any]] = None

    def get_by_name(self, name: str) -> Optional[Assessment]:
        """Get assessment by exact name match."""
        for assessment in self.assessments:
            if assessment.name.lower() == name.lower():
                return assessment
        return None

    def get_by_id(self, assessment_id: str) -> Optional[Assessment]:
        """Get assessment by ID."""
        for assessment in self.assessments:
            if assessment.id == assessment_id:
                return assessment
        return None

    def get_by_url(self, url: str) -> Optional[Assessment]:
        """Get assessment by URL."""
        for assessment in self.assessments:
            if assessment.url == url:
                return assessment
        return None

    def search_by_name(self, query: str) -> List[Assessment]:
        """Search for assessments by name substring."""
        query = query.lower()
        return [a for a in self.assessments if query in a.name.lower()]

    def filter_by_test_type(self, test_type: str) -> List[Assessment]:
        """Filter assessments by test type."""
        return [a for a in self.assessments if a.test_type == test_type]

    def filter_by_role(self, role: str) -> List[Assessment]:
        """Filter assessments by target role."""
        role_lower = role.lower()
        return [a for a in self.assessments if any(r.lower() == role_lower for r in a.target_roles)]

    def filter_by_domain(self, domain: str) -> List[Assessment]:
        """Filter assessments by domain."""
        domain_lower = domain.lower()
        return [a for a in self.assessments if any(d.lower() == domain_lower for d in a.domains)]

    def validate_urls(self) -> List[str]:
        """Validate all URLs in catalog. Returns list of invalid URLs."""
        invalid = []
        for assessment in self.assessments:
            if not assessment.url.startswith('https://www.shl.com/'):
                invalid.append(assessment.url)
        return invalid


def load_catalog(path: str) -> Catalog:
    """Load catalog from JSON file."""
    with open(path, 'r') as f:
        data = json.load(f)

    return Catalog(**data)


def validate_catalog_file(path: str) -> Dict[str, Any]:
    """Validate a catalog file and return validation results."""
    catalog = load_catalog(path)

    results = {
        "total_assessments": len(catalog.assessments),
        "invalid_urls": catalog.validate_urls(),
        "test_type_distribution": {
            "K": len(catalog.filter_by_test_type("K")),
            "C": len(catalog.filter_by_test_type("C")),
            "P": len(catalog.filter_by_test_type("P")),
        },
        "has_duplicates": False,
        "duplicate_ids": [],
        "duplicate_names": [],
    }

    # Check for duplicates
    ids = [a.id for a in catalog.assessments]
    names = [a.name for a in catalog.assessments]

    if len(ids) != len(set(ids)):
        results["has_duplicates"] = True
        results["duplicate_ids"] = [x for x in ids if ids.count(x) > 1]

    if len(names) != len(set(names)):
        results["has_duplicates"] = True
        results["duplicate_names"] = [x for x in names if names.count(x) > 1]

    return results
