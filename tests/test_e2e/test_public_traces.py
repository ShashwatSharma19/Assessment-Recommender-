"""E2E tests using synthetic test traces - Phase 3 Evaluation."""

import json
import pytest
from app.main import app
from app.catalog import load_catalog
from fastapi.testclient import TestClient


@pytest.fixture
def test_traces():
    """Load test traces."""
    with open("data/test_traces.json", "r") as f:
        data = json.load(f)
    return data["traces"]


@pytest.fixture
def catalog():
    """Load catalog."""
    return load_catalog("data/catalog.json")


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestPublicTraces:
    """Test against 10 synthetic public traces."""

    def test_trace_001_java_mid_level(self, client):
        """Trace 001: Java Developer - Mid-level."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "I'm hiring a Java developer"},
                {'role': 'assistant', 'content': "What seniority level?"},
                {'role': 'user', 'content': "Mid-level, around 4 years"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0
        assert any(r['test_type'] == 'K' for r in data['recommendations'])

    def test_trace_002_personality_managers(self, client):
        """Trace 002: Personality Assessment - Managers."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Need personality assessment for manager candidates"},
                {'role': 'assistant', 'content': "What seniority level?"},
                {'role': 'user', 'content': "Senior managers"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0
        # Should have personality tests
        assert any(r['test_type'] == 'P' for r in data['recommendations'])

    def test_trace_003_cognitive_analysts(self, client):
        """Trace 003: Cognitive Ability - Analysts."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Analyst role - need cognitive reasoning tests"},
                {'role': 'assistant', 'content': "What type of analysis will they do?"},
                {'role': 'user', 'content': "Data analysis with reporting"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0

    def test_trace_004_python_junior(self, client):
        """Trace 004: Python Developer - Junior."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Python developer junior level"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0

    def test_trace_005_fullstack_senior(self, client):
        """Trace 005: Full-Stack Developer - Senior."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Senior full-stack developer"},
                {'role': 'assistant', 'content': "What's their backend focus?"},
                {'role': 'user', 'content': "Node.js and JavaScript ecosystem"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0

    def test_trace_006_vague_clarification(self, client):
        """Trace 006: Vague Query - Clarification Needed."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "I need an assessment"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        # Should NOT have recommendations on vague query
        assert len(data['recommendations']) == 0

        # Now clarify
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "I need an assessment"},
                {'role': 'assistant', 'content': "What role?"},
                {'role': 'user', 'content': "Sales representative"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        # Now should have recommendations
        assert len(data['recommendations']) > 0

    def test_trace_007_devops(self, client):
        """Trace 007: DevOps Engineer - Cloud Focus."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "DevOps engineer with AWS and Docker experience"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0

    def test_trace_008_data_scientist(self, client):
        """Trace 008: Data Scientist - ML Focus."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Data scientist Python SQL machine learning"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0

    def test_trace_009_refinement(self, client):
        """Trace 009: Refinement - Add Personality Test."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "Engineer technical assessment"},
                {'role': 'assistant', 'content': "What type of engineering?"},
                {'role': 'user', 'content': "Actually, also add personality tests"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0
        # Should include personality tests
        assert any(r['test_type'] == 'P' for r in data['recommendations'])

    def test_trace_010_csharp(self, client):
        """Trace 010: C# Developer - .NET Stack."""
        response = client.post('/chat', json={
            'messages': [
                {'role': 'user', 'content': "C# developer mid-level .NET"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data['recommendations']) > 0


class TestRecallAt10:
    """Measure Recall@10 across all traces."""

    def compute_recall_at_k(self, recommended_ids: list, relevant_ids: list, k: int = 10) -> float:
        """
        Compute Recall@K.

        Recall@K = (Number of relevant items in top K) / (Total relevant items)
        """
        if not relevant_ids:
            return 1.0  # All relevant if no relevant items specified

        top_k = recommended_ids[:k]
        relevant_in_top_k = len([id for id in top_k if id in relevant_ids])
        total_relevant = len(relevant_ids)

        return relevant_in_top_k / total_relevant if total_relevant > 0 else 0.0

    def get_assessment_ids(self, recommendations: list, catalog) -> list:
        """Extract assessment IDs from recommendations using catalog lookup."""
        ids = []
        for r in recommendations:
            # Find matching assessment in catalog by name
            assessment = catalog.get_by_name(r['name'])
            if assessment:
                ids.append(assessment.id)
        return ids

    def test_recall_at_10_across_all_traces(self, test_traces, client, catalog):
        """Measure and report Recall@10 for all traces."""
        recalls = []
        trace_results = []

        for trace in test_traces:
            # Run the conversation
            response = client.post('/chat', json={
                'messages': trace['conversation']
            })

            assert response.status_code == 200
            data = response.json()

            # Extract recommended assessment IDs
            recommended_ids = self.get_assessment_ids(data['recommendations'], catalog)

            # Get expected relevant assessments
            relevant_ids = trace.get('expected_shortlist', [])

            # Compute Recall@10
            recall = self.compute_recall_at_k(recommended_ids, relevant_ids, k=10)
            recalls.append(recall)

            trace_results.append({
                'trace_id': trace['id'],
                'scenario': trace['scenario'],
                'recall_at_10': recall,
                'recommended_count': len(data['recommendations']),
                'expected_count': len(relevant_ids),
                'matched': len([id for id in recommended_ids if id in relevant_ids]),
            })

            print(f"\nTrace {trace['id']}: {trace['scenario']}")
            print(f"  Recall@10: {recall:.2%}")
            print(f"  Recommendations: {len(data['recommendations'])}")
            print(f"  Expected: {len(relevant_ids)}")

        # Compute mean recall
        mean_recall = sum(recalls) / len(recalls) if recalls else 0.0

        print("\n" + "="*60)
        print(f"MEAN RECALL@10: {mean_recall:.2%}")
        print("="*60)

        # Print detailed results
        print("\nDetailed Results:")
        for result in trace_results:
            print(f"\n{result['trace_id']}: {result['scenario']}")
            print(f"  Recall@10: {result['recall_at_10']:.2%}")
            print(f"  Recommendations: {result['recommended_count']} " +
                  f"(matched: {result['matched']}/{result['expected_count']})")

        # Assert minimum recall threshold
        assert mean_recall >= 0.55, f"Mean Recall@10 too low: {mean_recall:.2%} (target: ≥55%)"

        return {
            'mean_recall': mean_recall,
            'recalls': recalls,
            'trace_results': trace_results,
        }


class TestHallucination:
    """Test that no hallucinated URLs are returned."""

    def test_no_hallucinated_urls(self, test_traces, client, catalog):
        """Verify all returned URLs are from catalog."""
        catalog_urls = {a.url for a in catalog.assessments}

        for trace in test_traces:
            response = client.post('/chat', json={
                'messages': trace['conversation']
            })

            assert response.status_code == 200
            data = response.json()

            # Check all URLs are in catalog
            for rec in data['recommendations']:
                assert rec['url'] in catalog_urls, \
                    f"Hallucinated URL in trace {trace['id']}: {rec['url']}"

    def test_all_urls_start_with_shl(self, test_traces, client):
        """Verify all URLs point to SHL domain."""
        for trace in test_traces:
            response = client.post('/chat', json={
                'messages': trace['conversation']
            })

            assert response.status_code == 200
            data = response.json()

            for rec in data['recommendations']:
                assert rec['url'].startswith('https://www.shl.com/'), \
                    f"Non-SHL URL in trace {trace['id']}: {rec['url']}"
