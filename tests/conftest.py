"""Pytest fixtures for all tests."""

import pytest
import json
import tempfile
from pathlib import Path
from app.catalog import Catalog, Assessment


@pytest.fixture
def sample_assessment():
    """Return a sample assessment."""
    return Assessment(
        id="test_java",
        name="Java Test",
        url="https://www.shl.com/solutions/products/java/",
        description="Test Java knowledge",
        test_type="K",
        target_roles=["Developer"],
        domains=["Technical"],
    )


@pytest.fixture
def sample_catalog():
    """Return a sample catalog with test assessments."""
    assessments = [
        Assessment(
            id="java_test",
            name="Java Assessment",
            url="https://www.shl.com/solutions/products/java/",
            description="Tests Java programming skills",
            test_type="K",
            target_roles=["Backend Developer", "Java Developer"],
            domains=["Technical", "Programming"],
        ),
        Assessment(
            id="opq32r",
            name="OPQ32r",
            url="https://www.shl.com/solutions/products/opq32r/",
            description="Personality assessment",
            test_type="P",
            target_roles=["Manager", "Leader"],
            domains=["Behavioral"],
        ),
        Assessment(
            id="gsa",
            name="GSA",
            url="https://www.shl.com/solutions/products/gsa/",
            description="General ability assessment",
            test_type="C",
            target_roles=["Professional"],
            domains=["Cognitive"],
        ),
    ]
    return Catalog(assessments=assessments)


@pytest.fixture
def catalog_json_file(sample_catalog):
    """Create a temporary catalog JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "assessments": [a.dict() for a in sample_catalog.assessments],
            "metadata": {"version": "1.0"}
        }, f)
        path = f.name

    yield path

    # Cleanup
    Path(path).unlink()


@pytest.fixture
def real_catalog_path():
    """Return path to the real catalog file."""
    return "data/catalog.json"
