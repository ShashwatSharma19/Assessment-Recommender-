"""Local testing script for SHL Assessment Recommender endpoints."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test /health endpoint."""
    print("\n[TEST 1] Health Endpoint")
    print("-" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data['status'] == 'ok', f"Expected status='ok', got {data['status']}"
        print("[PASS] Health endpoint working correctly")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_vague_query():
    """Test vague query (should ask for clarification, no recommendations)."""
    print("\n[TEST 2] Vague Query (should clarify)")
    print("-" * 50)
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "I need an assessment"}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Reply: {data.get('reply', 'N/A')[:100]}...")
        print(f"Recommendations: {len(data.get('recommendations', []))} items")
        print(f"End of conversation: {data.get('end_of_conversation', False)}")

        assert response.status_code == 200
        assert len(data.get('recommendations', [])) == 0, "Vague query should not have recommendations"
        assert not data.get('end_of_conversation', False), "Should not end conversation on vague query"
        print("[PASS] Vague query handled correctly (no recommendations)")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_specific_query():
    """Test specific query (should return recommendations)."""
    print("\n[TEST 3] Specific Query (Java developer mid-level)")
    print("-" * 50)
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "I'm hiring a Java developer"},
                {"role": "assistant", "content": "What seniority level?"},
                {"role": "user", "content": "Mid-level, around 4 years"},
            ]
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Reply: {data.get('reply', 'N/A')[:100]}...")
        recs = data.get('recommendations', [])
        print(f"Recommendations: {len(recs)} items")

        if recs:
            print("First 3 recommendations:")
            for i, rec in enumerate(recs[:3], 1):
                print(f"  {i}. {rec['name']} ({rec['test_type']}) - {rec['url'][:60]}...")

        assert response.status_code == 200
        assert len(recs) > 0, "Specific query should return recommendations"
        assert data.get('end_of_conversation', False), "Should end conversation with recommendations"

        # Verify all URLs are SHL URLs
        for rec in recs:
            assert rec['url'].startswith('https://www.shl.com/'), f"Invalid URL: {rec['url']}"

        print(f"[PASS] Specific query returned {len(recs)} recommendations")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_off_topic_query():
    """Test off-topic query (should refuse)."""
    print("\n[TEST 4] Off-Topic Query (salary question)")
    print("-" * 50)
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "What salary should I pay a Java developer?"}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Reply: {data.get('reply', 'N/A')[:100]}...")
        print(f"Recommendations: {len(data.get('recommendations', []))} items")

        assert response.status_code == 200
        assert len(data.get('recommendations', [])) == 0, "Off-topic query should have no recommendations"
        print("[PASS] Off-topic query refused correctly")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def test_python_developer():
    """Test Python developer query."""
    print("\n[TEST 5] Python Developer - Junior Level")
    print("-" * 50)
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "Python developer junior level"}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Reply: {data.get('reply', 'N/A')[:100]}...")
        recs = data.get('recommendations', [])
        print(f"Recommendations: {len(recs)} items")

        if recs:
            print("Recommended assessments:")
            for i, rec in enumerate(recs[:5], 1):
                print(f"  {i}. {rec['name']} ({rec['test_type']})")

        assert response.status_code == 200
        assert len(recs) > 0, "Python developer query should return recommendations"
        print(f"[PASS] Python developer query returned {len(recs)} recommendations")
        return True
    except Exception as e:
        print(f"[FAIL] {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("SHL ASSESSMENT RECOMMENDER - LOCAL TESTING")
    print("=" * 50)

    # Check if server is running
    print("\nChecking if server is running...")
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("Server is online!")
    except Exception as e:
        print(f"ERROR: Server not responding at {BASE_URL}")
        print(f"Make sure to run: uvicorn app.main:app --reload")
        return

    # Run tests
    results = []
    results.append(("Health Endpoint", test_health()))
    results.append(("Vague Query", test_vague_query()))
    results.append(("Specific Query (Java)", test_specific_query()))
    results.append(("Off-Topic Query", test_off_topic_query()))
    results.append(("Python Developer", test_python_developer()))

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    if passed == total:
        print("\nAll tests PASSED! Ready for deployment.")
    else:
        print(f"\n{total - passed} tests FAILED. Check errors above.")


if __name__ == "__main__":
    main()
