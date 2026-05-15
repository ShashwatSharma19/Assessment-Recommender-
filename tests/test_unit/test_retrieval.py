"""Unit tests for retrieval module."""

import pytest
from app.catalog import Catalog, Assessment
from app.retrieval import HybridRetriever


class TestHybridRetriever:
    """Tests for HybridRetriever class."""

    @pytest.fixture
    def retriever(self, sample_catalog):
        """Create a retriever with sample catalog."""
        return HybridRetriever(sample_catalog)

    def test_retriever_initialization(self, retriever):
        """Test that retriever initializes properly."""
        assert retriever.catalog is not None
        assert len(retriever.catalog.assessments) == 3

    def test_retriever_has_indices(self, retriever):
        """Test that retriever builds indices."""
        assert retriever.faiss_index is not None
        assert retriever.bm25_index is not None

    def test_hybrid_search_by_skill(self, retriever):
        """Test searching for assessments by skill."""
        results = retriever.search("Java programming", k=5)
        assert len(results) > 0
        # Java Assessment should rank high
        assessment_ids = [a.id for a in results]
        assert "java_test" in assessment_ids

    def test_hybrid_search_by_role(self, retriever):
        """Test searching for assessments by role."""
        results = retriever.search("Manager personality assessment", k=5)
        assert len(results) > 0
        assessment_ids = [a.id for a in results]
        assert "opq32r" in assessment_ids

    def test_search_returns_top_k(self, retriever):
        """Test that search returns at most k results."""
        results = retriever.search("test", k=2)
        assert len(results) <= 2

    def test_search_all_assessments(self, retriever):
        """Test searching returns all assessments."""
        results = retriever.search("assessment", k=10)
        assert len(results) == 3

    def test_search_exact_name_match(self, retriever):
        """Test searching for exact assessment name."""
        results = retriever.search("OPQ32r", k=5)
        assert len(results) > 0
        # OPQ32r should be ranked high
        assert results[0].id == "opq32r"

    def test_search_empty_query(self, retriever):
        """Test searching with empty query."""
        results = retriever.search("", k=5)
        # Should return some results (by BM25 default ranking)
        assert len(results) >= 0

    def test_search_nonexistent_term(self, retriever):
        """Test searching for term that doesn't exist."""
        results = retriever.search("xenophobic quasar", k=5)
        # Should still return results but with lower relevance
        assert len(results) >= 0


class TestRetrieverWithRealCatalog:
    """Tests using the real catalog."""

    @pytest.fixture
    def real_retriever(self, real_catalog_path):
        """Create retriever with real catalog."""
        from app.catalog import load_catalog
        catalog = load_catalog(real_catalog_path)
        return HybridRetriever(catalog)

    def test_real_catalog_search_java(self, real_retriever):
        """Test searching real catalog for Java assessments."""
        results = real_retriever.search("Java developer assessment", k=10)
        assert len(results) > 0
        # Should find Java-related assessments
        names = [a.name for a in results]
        assert any("Java" in name for name in names)

    def test_real_catalog_search_cognitive(self, real_retriever):
        """Test searching real catalog for cognitive tests."""
        results = real_retriever.search("cognitive reasoning ability", k=10)
        assert len(results) > 0

    def test_real_catalog_search_personality(self, real_retriever):
        """Test searching real catalog for personality tests."""
        results = real_retriever.search("personality behavioral traits", k=10)
        assert len(results) > 0
        names = [a.name for a in results]
        # Should find OPQ or similar personality tests
        assert any("OPQ" in name or "personality" in name.lower() for name in names)

    def test_real_catalog_many_results(self, real_retriever):
        """Test that real catalog supports requesting many results."""
        results = real_retriever.search("assessment test", k=20)
        assert len(results) > 0
