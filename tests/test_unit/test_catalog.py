"""Unit tests for catalog module."""

import pytest
from app.catalog import Assessment, Catalog, load_catalog, validate_catalog_file


class TestAssessment:
    """Tests for Assessment model."""

    def test_assessment_creation(self, sample_assessment):
        """Test that assessment can be created with valid data."""
        assert sample_assessment.name == "Java Test"
        assert sample_assessment.test_type == "K"
        assert sample_assessment.url.startswith("https://www.shl.com/")

    def test_assessment_invalid_url(self):
        """Test that assessment rejects invalid URLs."""
        with pytest.raises(ValueError):
            Assessment(
                id="test",
                name="Test",
                url="https://google.com/",  # Invalid domain
                description="Test",
                test_type="K",
            )

    def test_assessment_invalid_test_type(self, sample_assessment):
        """Test that assessment rejects invalid test types."""
        with pytest.raises(ValueError):
            Assessment(
                id="test",
                name="Test",
                url="https://www.shl.com/test/",
                description="Test",
                test_type="X",  # Invalid type
            )


class TestCatalog:
    """Tests for Catalog model."""

    def test_catalog_loading(self, sample_catalog):
        """Test that catalog can be created."""
        assert len(sample_catalog.assessments) == 3
        assert all(isinstance(a, Assessment) for a in sample_catalog.assessments)

    def test_get_by_name_exact_match(self, sample_catalog):
        """Test getting assessment by exact name."""
        assessment = sample_catalog.get_by_name("Java Assessment")
        assert assessment is not None
        assert assessment.id == "java_test"

    def test_get_by_name_case_insensitive(self, sample_catalog):
        """Test that name lookup is case insensitive."""
        assessment = sample_catalog.get_by_name("java assessment")
        assert assessment is not None
        assert assessment.id == "java_test"

    def test_get_by_name_not_found(self, sample_catalog):
        """Test that get_by_name returns None for missing assessment."""
        assessment = sample_catalog.get_by_name("Nonexistent")
        assert assessment is None

    def test_get_by_id(self, sample_catalog):
        """Test getting assessment by ID."""
        assessment = sample_catalog.get_by_id("opq32r")
        assert assessment is not None
        assert assessment.name == "OPQ32r"

    def test_get_by_url(self, sample_catalog):
        """Test getting assessment by URL."""
        url = "https://www.shl.com/solutions/products/gsa/"
        assessment = sample_catalog.get_by_url(url)
        assert assessment is not None
        assert assessment.id == "gsa"

    def test_search_by_name(self, sample_catalog):
        """Test searching assessments by name substring."""
        results = sample_catalog.search_by_name("Java")
        assert len(results) == 1
        assert results[0].id == "java_test"

    def test_filter_by_test_type(self, sample_catalog):
        """Test filtering assessments by test type."""
        knowledge_tests = sample_catalog.filter_by_test_type("K")
        assert len(knowledge_tests) == 1
        assert knowledge_tests[0].id == "java_test"

        personality_tests = sample_catalog.filter_by_test_type("P")
        assert len(personality_tests) == 1
        assert personality_tests[0].id == "opq32r"

        cognitive_tests = sample_catalog.filter_by_test_type("C")
        assert len(cognitive_tests) == 1
        assert cognitive_tests[0].id == "gsa"

    def test_filter_by_role(self, sample_catalog):
        """Test filtering assessments by target role."""
        developer_tests = sample_catalog.filter_by_role("Backend Developer")
        assert len(developer_tests) == 1
        assert developer_tests[0].id == "java_test"

        manager_tests = sample_catalog.filter_by_role("Manager")
        assert len(manager_tests) == 1
        assert manager_tests[0].id == "opq32r"

    def test_filter_by_domain(self, sample_catalog):
        """Test filtering assessments by domain."""
        technical = sample_catalog.filter_by_domain("Technical")
        assert len(technical) == 1
        assert technical[0].id == "java_test"

        behavioral = sample_catalog.filter_by_domain("Behavioral")
        assert len(behavioral) == 1
        assert behavioral[0].id == "opq32r"

    def test_validate_urls(self, sample_catalog):
        """Test URL validation."""
        invalid = sample_catalog.validate_urls()
        assert len(invalid) == 0  # All URLs should be valid


class TestLoadCatalog:
    """Tests for catalog loading."""

    def test_load_catalog_from_file(self, catalog_json_file):
        """Test loading catalog from JSON file."""
        catalog = load_catalog(catalog_json_file)
        assert len(catalog.assessments) == 3
        assert catalog.assessments[0].name == "Java Assessment"

    def test_load_real_catalog(self, real_catalog_path):
        """Test loading the actual catalog file."""
        catalog = load_catalog(real_catalog_path)
        assert len(catalog.assessments) >= 25  # We created at least 25 in seed
        assert all(isinstance(a, Assessment) for a in catalog.assessments)
        assert all(a.url.startswith("https://www.shl.com/") for a in catalog.assessments)

    def test_validate_catalog_file(self, catalog_json_file):
        """Test catalog validation results."""
        results = validate_catalog_file(catalog_json_file)
        assert results["total_assessments"] == 3
        assert results["invalid_urls"] == []
        assert results["has_duplicates"] is False
        assert len(results["test_type_distribution"]) == 3

    def test_validate_real_catalog(self, real_catalog_path):
        """Test validation of real catalog."""
        results = validate_catalog_file(real_catalog_path)
        assert results["total_assessments"] >= 25
        assert results["invalid_urls"] == []  # All URLs should be valid
        assert results["has_duplicates"] is False
        assert sum(results["test_type_distribution"].values()) == results["total_assessments"]
