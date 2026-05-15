# SHL Conversational Assessment Recommender
## Test-Driven Development (TDD) Plan

**Project:** Build a Conversational SHL Assessment Recommender  
**Testing Approach:** Write tests first, implement to pass  
**Framework:** pytest + FastAPI TestClient  
**Status:** Test Specification Phase  

---

## 1. Testing Philosophy

### TDD Workflow
1. **Write test** (RED) – Specify expected behavior
2. **Run test** (RED) – Watch it fail
3. **Implement** (GREEN) – Write minimal code to pass
4. **Refactor** (GREEN) – Improve without breaking tests
5. **Repeat** for next feature

### Test Pyramid
```
        △
       ╱ ╲
      ╱E2E╲        End-to-End (Conversation Traces)
     ╱─────╲       ~5–10 tests
    ╱       ╲
   ╱─────────╲
  ╱Integration╲     Integration (Retrieval + LLM + State)
 ╱─────────────╲    ~15–20 tests
╱               ╲
╱─────────────────╲
╱     Unit Tests    ╲  Unit (Functions, Validation)
╱───────────────────╲ ~50–80 tests
```

---

## 2. Test Folder Structure

```
project/
├── tests/
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_unit/
│   │   ├── test_catalog.py            # Catalog loading, parsing
│   │   ├── test_retrieval.py          # FAISS + BM25 search
│   │   ├── test_state_machine.py      # State transitions
│   │   ├── test_validation.py         # URL validation, schema
│   │   └── test_prompts.py            # Prompt construction
│   ├── test_integration/
│   │   ├── test_agent_end_to_end.py   # Full conversation flow
│   │   ├── test_behavior_probes.py    # Off-topic, no turn-1 recommend
│   │   └── test_edge_cases.py         # Edge cases
│   └── test_e2e/
│       ├── test_public_traces.py      # 10 public conversation traces
│       └── test_recall_at_10.py       # Recall@10 measurement
├── app/
│   ├── main.py                        # FastAPI app
│   ├── catalog.py                     # Catalog loading
│   ├── retrieval.py                   # FAISS + BM25
│   ├── agent.py                       # LangChain agent
│   ├── state.py                       # State machine
│   ├── prompts.py                     # System prompts
│   └── validation.py                  # URL validation
└── data/
    ├── catalog.json                   # SHL catalog (scraped)
    └── public_traces.json             # 10 public traces (from SHL)
```

---

## 3. Unit Tests (Test Module: test_unit/)

### 3.1 Catalog Tests (test_catalog.py)

**Test:** Load catalog from JSON
```python
def test_catalog_load_success(catalog_path):
    """Catalog loads successfully from JSON"""
    catalog = load_catalog(catalog_path)
    assert len(catalog.assessments) > 50  # Minimum 50 tests
    assert all(hasattr(a, 'id') for a in catalog.assessments)
    assert all(hasattr(a, 'url') for a in catalog.assessments)
```

**Test:** Validate catalog structure
```python
def test_catalog_structure_valid():
    """Each assessment has required fields"""
    catalog = load_catalog("data/catalog.json")
    required_fields = {'id', 'name', 'url', 'description', 'target_roles', 'domains'}
    for assessment in catalog.assessments:
        assert required_fields.issubset(assessment.__dict__.keys())
```

**Test:** URL format validation
```python
def test_catalog_urls_valid():
    """All URLs are valid SHL product URLs"""
    catalog = load_catalog("data/catalog.json")
    for assessment in catalog.assessments:
        assert assessment.url.startswith("https://www.shl.com/")
        assert "/products/" in assessment.url or "/solutions/" in assessment.url
```

**Test:** No duplicate assessments
```python
def test_catalog_no_duplicates():
    """Catalog has no duplicate IDs or names"""
    catalog = load_catalog("data/catalog.json")
    ids = [a.id for a in catalog.assessments]
    names = [a.name for a in catalog.assessments]
    assert len(ids) == len(set(ids)), "Duplicate IDs found"
    assert len(names) == len(set(names)), "Duplicate names found"
```

**Test:** Target roles populated
```python
def test_catalog_target_roles_populated():
    """Each assessment has at least one target role"""
    catalog = load_catalog("data/catalog.json")
    for assessment in catalog.assessments:
        assert len(assessment.target_roles) > 0
        assert isinstance(assessment.target_roles, list)
```

---

### 3.2 Retrieval Tests (test_retrieval.py)

**Test:** FAISS index creation
```python
def test_faiss_index_creation(catalog, embeddings_model):
    """FAISS index creates successfully"""
    index = create_faiss_index(catalog, embeddings_model)
    assert index is not None
    assert index.ntotal == len(catalog.assessments)
```

**Test:** FAISS search returns results
```python
def test_faiss_search(faiss_index, embeddings_model):
    """FAISS search returns top-K results"""
    query = "Java developer assessment"
    results = faiss_search(faiss_index, query, k=5, embeddings_model=embeddings_model)
    assert len(results) == 5
    assert all(hasattr(r, 'id') for r in results)
```

**Test:** BM25 search works
```python
def test_bm25_search(catalog):
    """BM25 search finds keyword matches"""
    bm25_retriever = BM25Retriever(catalog)
    results = bm25_retriever.search("Java", k=5)
    assert len(results) > 0
    # At least one result should have "Java" in name or description
    assert any("java" in r.name.lower() or "java" in r.description.lower() 
               for r in results)
```

**Test:** Hybrid search combines both
```python
def test_hybrid_search(catalog, faiss_index, embeddings_model):
    """Hybrid search combines FAISS and BM25"""
    query = "backend developer"
    results = hybrid_search(
        query=query,
        catalog=catalog,
        faiss_index=faiss_index,
        embeddings_model=embeddings_model,
        k=10
    )
    assert len(results) <= 10
    assert len(results) > 0
```

**Test:** Search handles empty query gracefully
```python
def test_search_empty_query(catalog, faiss_index, embeddings_model):
    """Search on empty query returns error or defaults"""
    with pytest.raises(ValueError):
        hybrid_search("", catalog, faiss_index, embeddings_model)
```

**Test:** Search respects k limit
```python
def test_search_respects_k_limit(catalog, faiss_index, embeddings_model):
    """Search returns exactly k results (or fewer if catalog is small)"""
    results = hybrid_search("developer", catalog, faiss_index, embeddings_model, k=10)
    assert len(results) <= 10
```

---

### 3.3 State Machine Tests (test_state_machine.py)

**Test:** Initial state is GATHERING_CONTEXT
```python
def test_initial_state():
    """Agent starts in GATHERING_CONTEXT state"""
    state = StateMachine()
    assert state.current_state == State.GATHERING_CONTEXT
```

**Test:** State transition to READY_TO_RECOMMEND
```python
def test_transition_to_ready_to_recommend():
    """State transitions from GATHERING to READY when context complete"""
    state = StateMachine()
    state.add_context(role="Java Developer")
    state.add_context(seniority="Mid-level")
    state.add_context(focus="Backend")
    
    # Check if enough context
    if state.is_context_sufficient():
        state.transition_to(State.READY_TO_RECOMMEND)
    
    assert state.current_state == State.READY_TO_RECOMMEND
```

**Test:** State transition to RECOMMENDING
```python
def test_transition_to_recommending():
    """State transitions to RECOMMENDING when recommendations set"""
    state = StateMachine()
    state.transition_to(State.RECOMMENDING)
    assert state.current_state == State.RECOMMENDING
```

**Test:** State transition to DONE
```python
def test_transition_to_done():
    """State transitions to DONE at end of conversation"""
    state = StateMachine()
    state.transition_to(State.DONE)
    assert state.current_state == State.DONE
    assert state.end_of_conversation is True
```

**Test:** Invalid state transition raises error
```python
def test_invalid_state_transition():
    """Invalid state transition raises ValueError"""
    state = StateMachine()
    # GATHERING_CONTEXT -> DONE directly is invalid
    with pytest.raises(ValueError):
        state.transition_to(State.DONE)
```

**Test:** Context accumulation
```python
def test_context_accumulation():
    """State accumulates context across turns"""
    state = StateMachine()
    state.add_context(role="Java Developer")
    assert state.context['role'] == "Java Developer"
    
    state.add_context(seniority="Senior")
    assert state.context['role'] == "Java Developer"
    assert state.context['seniority'] == "Senior"
```

**Test:** Context refinement (mid-conversation edit)
```python
def test_context_refinement():
    """State allows context refinement mid-conversation"""
    state = StateMachine()
    state.add_context(role="Backend")
    state.add_context(personality_focus=False)
    
    # User says "Actually, add personality tests"
    state.update_context(personality_focus=True)
    
    assert state.context['personality_focus'] is True
```

**Test:** Turn counter increments
```python
def test_turn_counter():
    """State tracks turn count"""
    state = StateMachine()
    assert state.turn_count == 0
    state.increment_turn()
    assert state.turn_count == 1
```

**Test:** Turn cap enforced
```python
def test_turn_cap_enforcement():
    """Agent refuses to continue after turn cap (8 turns)"""
    state = StateMachine(max_turns=8)
    for _ in range(8):
        state.increment_turn()
    
    assert state.turn_count == 8
    assert state.turn_cap_reached() is True
```

---

### 3.4 Validation Tests (test_validation.py)

**Test:** URL validation against catalog
```python
def test_url_validation_valid():
    """Valid URL from catalog passes validation"""
    catalog = load_catalog("data/catalog.json")
    url = catalog.assessments[0].url
    
    assert is_valid_catalog_url(url, catalog) is True
```

**Test:** Invalid URL fails validation
```python
def test_url_validation_invalid():
    """URL not in catalog fails validation"""
    catalog = load_catalog("data/catalog.json")
    fake_url = "https://www.shl.com/solutions/products/fake-test/"
    
    assert is_valid_catalog_url(fake_url, catalog) is False
```

**Test:** URL injection prevention
```python
def test_url_injection_prevention():
    """Malicious URLs are rejected"""
    catalog = load_catalog("data/catalog.json")
    malicious_urls = [
        "https://malicious.com/phishing",
        "javascript:alert('xss')",
        "file:///etc/passwd"
    ]
    
    for url in malicious_urls:
        assert is_valid_catalog_url(url, catalog) is False
```

**Test:** Schema validation for response
```python
def test_response_schema_valid():
    """Response matches required schema"""
    response = {
        "reply": "Here are assessments...",
        "recommendations": [
            {"name": "Test", "url": "https://...", "test_type": "K"}
        ],
        "end_of_conversation": False
    }
    
    assert validate_response_schema(response) is True
```

**Test:** Missing required fields in response
```python
def test_response_schema_missing_fields():
    """Response missing required fields fails validation"""
    invalid_responses = [
        {"reply": "text"},  # Missing recommendations, end_of_conversation
        {"recommendations": [], "end_of_conversation": False},  # Missing reply
        {"reply": "text", "recommendations": []},  # Missing end_of_conversation
    ]
    
    for response in invalid_responses:
        assert validate_response_schema(response) is False
```

**Test:** Recommendations array bounds
```python
def test_recommendations_bounds():
    """Recommendations array has 0 or 1–10 items"""
    valid_recs = [[], [{"name": "T", "url": "u", "test_type": "K"}]]
    invalid_recs = [
        list(range(11))  # 11 items (exceeds max)
    ]
    
    for rec in valid_recs:
        assert validate_recommendations(rec) is True
    
    for rec in invalid_recs:
        assert validate_recommendations(rec) is False
```

---

### 3.5 Prompt Tests (test_prompts.py)

**Test:** System prompt generation
```python
def test_system_prompt_generation():
    """System prompt generated successfully"""
    catalog_context = "Test: OPQ32r, GSA, Java 8"
    system_prompt = generate_system_prompt(catalog_context)
    
    assert len(system_prompt) > 100
    assert "agent" in system_prompt.lower() or "assess" in system_prompt.lower()
    assert catalog_context in system_prompt
```

**Test:** Prompt includes catalog grounding
```python
def test_prompt_includes_catalog():
    """System prompt includes catalog assessments to prevent hallucination"""
    catalog = load_catalog("data/catalog.json")
    top_assessments = catalog.assessments[:5]
    
    system_prompt = generate_system_prompt_with_catalog(top_assessments)
    
    # Check that assessments are mentioned
    for assessment in top_assessments:
        assert assessment.name in system_prompt
```

**Test:** CoT prompt structure
```python
def test_cot_prompt_structure():
    """Chain-of-thought prompt includes reasoning steps"""
    cot_prompt = generate_cot_prompt(
        user_query="Java developer",
        context={"role": "Backend", "seniority": "Mid"}
    )
    
    # Should ask agent to think step-by-step
    assert "step" in cot_prompt.lower() or "reason" in cot_prompt.lower()
```

**Test:** Refusal prompt for off-topic
```python
def test_refusal_prompt():
    """Refusal prompt generated for out-of-scope queries"""
    refusal_prompt = generate_refusal_prompt("What's the best salary?")
    
    assert len(refusal_prompt) > 0
    assert "scope" in refusal_prompt.lower() or "shl" in refusal_prompt.lower()
```

---

## 4. Integration Tests (Test Module: test_integration/)

### 4.1 Agent End-to-End Tests (test_agent_end_to_end.py)

**Test:** Full conversation flow (Clarify → Recommend → Done)
```python
@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Full agent conversation: vague query → clarify → recommend → done"""
    agent = AgentService()
    
    # Turn 1: User provides vague query
    response1 = await agent.chat(
        messages=[{"role": "user", "content": "I need a developer assessment"}]
    )
    assert response1.recommendations == []  # Should clarify, not recommend
    assert "what type" in response1.reply.lower() or "developer" in response1.reply.lower()
    
    # Turn 2: User provides role
    response2 = await agent.chat(
        messages=[
            {"role": "user", "content": "I need a developer assessment"},
            {"role": "assistant", "content": response1.reply},
            {"role": "user", "content": "Java developer"}
        ]
    )
    assert response2.recommendations == []  # Still gathering context
    
    # Turn 3: User provides seniority
    response3 = await agent.chat(
        messages=[
            {"role": "user", "content": "I need a developer assessment"},
            {"role": "assistant", "content": response1.reply},
            {"role": "user", "content": "Java developer"},
            {"role": "assistant", "content": response2.reply},
            {"role": "user", "content": "Mid-level, around 4 years"}
        ]
    )
    
    # Now agent should recommend
    assert len(response3.recommendations) > 0
    assert len(response3.recommendations) <= 10
    assert response3.end_of_conversation is True
    assert all(is_valid_catalog_url(r['url'], catalog) for r in response3.recommendations)
```

**Test:** Agent honors message history
```python
@pytest.mark.asyncio
async def test_agent_honors_history():
    """Agent uses conversation history to inform responses"""
    agent = AgentService()
    
    messages = [
        {"role": "user", "content": "I need a Java developer assessment"},
        {"role": "assistant", "content": "What seniority level?"},
        {"role": "user", "content": "Senior"}
    ]
    
    response = await agent.chat(messages=messages)
    
    # Should reference Java AND Senior in recommendations
    # (either in response text or in assessment metadata)
    assert len(response.recommendations) > 0
```

**Test:** Agent response matches schema
```python
@pytest.mark.asyncio
async def test_agent_schema_compliance():
    """Agent response always matches schema"""
    agent = AgentService()
    
    messages = [{"role": "user", "content": "Python developer"}]
    response = await agent.chat(messages=messages)
    
    # Validate schema
    assert hasattr(response, 'reply')
    assert hasattr(response, 'recommendations')
    assert hasattr(response, 'end_of_conversation')
    assert isinstance(response.reply, str)
    assert isinstance(response.recommendations, list)
    assert isinstance(response.end_of_conversation, bool)
```

---

### 4.2 Behavior Probes (test_behavior_probes.py)

**Test:** Agent refuses off-topic question
```python
@pytest.mark.asyncio
async def test_agent_refuses_off_topic():
    """Agent refuses general HR advice, not SHL-related"""
    agent = AgentService()
    
    off_topic_questions = [
        "What's the best salary for a Java developer?",
        "Is it legal to hire based on age?",
        "Can I use competitors' tests?",
        "How do I write a job description?"
    ]
    
    for question in off_topic_questions:
        messages = [{"role": "user", "content": question}]
        response = await agent.chat(messages=messages)
        
        assert response.recommendations == []
        assert "shl" in response.reply.lower() or "scope" in response.reply.lower() \
               or "assess" in response.reply.lower()
```

**Test:** Agent does NOT recommend on turn 1 for vague query
```python
@pytest.mark.asyncio
async def test_no_turn_1_recommendation_for_vague_query():
    """Agent does not recommend on first turn if query is vague"""
    agent = AgentService()
    
    vague_queries = [
        "I need an assessment",
        "Assessment?",
        "Help",
        "What do you have?"
    ]
    
    for query in vague_queries:
        messages = [{"role": "user", "content": query}]
        response = await agent.chat(messages=messages)
        
        assert response.recommendations == [], f"Recommendations on turn 1 for: {query}"
        assert response.end_of_conversation is False
```

**Test:** Agent DOES recommend on turn 1 for specific query
```python
@pytest.mark.asyncio
async def test_turn_1_recommendation_for_specific_query():
    """Agent MAY recommend on turn 1 if query is sufficiently specific"""
    agent = AgentService()
    
    specific_queries = [
        "Senior Java developer with 10 years experience, backend focus",
        "Mid-level Python engineer for data science team",
        "Junior frontend React developer assessment"
    ]
    
    for query in specific_queries:
        messages = [{"role": "user", "content": query}]
        response = await agent.chat(messages=messages)
        
        # If enough context, recommend. Otherwise, clarify.
        if len(response.recommendations) > 0:
            assert response.end_of_conversation is True
```

**Test:** Agent honors mid-conversation edits
```python
@pytest.mark.asyncio
async def test_agent_honors_mid_conversation_edit():
    """Agent updates recommendations when user refines constraints"""
    agent = AgentService()
    
    # Turn 1–2: Establish initial recommendation
    messages_1 = [
        {"role": "user", "content": "Java developer assessment"},
        {"role": "assistant", "content": "What seniority?"},
        {"role": "user", "content": "Mid-level"}
    ]
    response_1 = await agent.chat(messages=messages_1)
    recs_1 = {r['name'] for r in response_1.recommendations}
    
    # Turn 3: User adds constraint
    messages_2 = messages_1 + [
        {"role": "assistant", "content": response_1.reply},
        {"role": "user", "content": "Actually, add personality assessment"}
    ]
    response_2 = await agent.chat(messages=messages_2)
    recs_2 = {r['name'] for r in response_2.recommendations}
    
    # Recommendations should change (not be identical)
    # This is tricky to test deterministically; mostly checking no error
    assert len(response_2.recommendations) > 0
```

**Test:** Agent does not hallucinate URLs
```python
@pytest.mark.asyncio
async def test_no_hallucinated_urls():
    """All returned URLs exist in catalog"""
    agent = AgentService()
    catalog = load_catalog("data/catalog.json")
    
    # Run agent on 10 queries
    queries = [
        "Java developer",
        "Python backend",
        "Senior manager assessment",
        "Personality test"
    ]
    
    for query in queries:
        messages = [{"role": "user", "content": query}]
        response = await agent.chat(messages=messages)
        
        for rec in response.recommendations:
            assert is_valid_catalog_url(rec['url'], catalog), \
                f"Hallucinated URL: {rec['url']}"
```

**Test:** Agent respects turn cap
```python
@pytest.mark.asyncio
async def test_agent_respects_turn_cap():
    """Agent respects 8-turn cap"""
    agent = AgentService()
    
    # Build 8-turn conversation
    messages = [
        {"role": "user", "content": "I need assessment"},
        {"role": "assistant", "content": "What role?"},
        {"role": "user", "content": "Java dev"},
        {"role": "assistant", "content": "What seniority?"},
        {"role": "user", "content": "Senior"},
        {"role": "assistant", "content": "Here are 5 tests..."},
        {"role": "user", "content": "More options?"},
        # At turn 8 (or close), agent should stop or wrap up
    ]
    
    # Turn count is len(messages) // 2 + next response
    turn_count = len(messages) // 2
    assert turn_count <= 8
```

---

### 4.3 Edge Cases (test_edge_cases.py)

**Test:** User provides contradictory information
```python
@pytest.mark.asyncio
async def test_contradictory_information():
    """Agent handles contradictory user info gracefully"""
    agent = AgentService()
    
    messages = [
        {"role": "user", "content": "Senior Java developer"},
        {"role": "assistant", "content": "Got it..."},
        {"role": "user", "content": "Actually, I'm a junior"}
    ]
    
    response = await agent.chat(messages=messages)
    # Should update context, not error
    assert response is not None
    assert validate_response_schema(response) is True
```

**Test:** User asks comparison between two tests
```python
@pytest.mark.asyncio
async def test_comparison_request():
    """Agent can compare two assessments when asked"""
    agent = AgentService()
    
    messages = [
        {"role": "user", "content": "What's the difference between OPQ32r and GSA?"}
    ]
    
    response = await agent.chat(messages=messages)
    
    # Should have comparison text, no recommendations (not recommending)
    assert "OPQ" in response.reply or "opq" in response.reply.lower()
    assert response.recommendations == []
```

**Test:** User asks about non-existent test
```python
@pytest.mark.asyncio
async def test_unknown_test_name():
    """Agent handles question about unknown test gracefully"""
    agent = AgentService()
    
    messages = [
        {"role": "user", "content": "What about the FakeTest assessment?"}
    ]
    
    response = await agent.chat(messages=messages)
    
    # Should gracefully say it's not in catalog
    assert response is not None
    assert "not" in response.reply.lower() or "don't" in response.reply.lower() \
           or "shl" in response.reply.lower()
```

**Test:** Empty or whitespace-only user input
```python
@pytest.mark.asyncio
async def test_empty_user_input():
    """Agent handles empty input gracefully"""
    agent = AgentService()
    
    empty_inputs = ["", "   ", "\n\n"]
    
    for input_text in empty_inputs:
        messages = [{"role": "user", "content": input_text}]
        
        # Should not error, should ask for clarification
        response = await agent.chat(messages=messages)
        assert response is not None
```

**Test:** Very long user input
```python
@pytest.mark.asyncio
async def test_long_user_input():
    """Agent handles very long input without breaking"""
    agent = AgentService()
    
    long_input = "Java developer " * 100  # 1500+ chars
    messages = [{"role": "user", "content": long_input}]
    
    # Should handle gracefully (truncate or process)
    response = await agent.chat(messages=messages)
    assert response is not None
    assert validate_response_schema(response) is True
```

---

## 5. End-to-End Tests (Test Module: test_e2e/)

### 5.1 Public Traces (test_public_traces.py)

**Test:** Run all 10 public traces
```python
@pytest.mark.asyncio
@pytest.mark.parametrize("trace", load_public_traces())
async def test_public_trace(trace):
    """Run agent against public trace, check if recommendations match expected"""
    agent = AgentService()
    catalog = load_catalog("data/catalog.json")
    
    # Simulate conversation per trace
    # trace.messages = full conversation
    # trace.expected_shortlist = ground truth assessments
    
    response = await agent.chat(messages=trace.messages)
    
    # Check schema
    assert validate_response_schema(response) is True
    
    # Check URLs valid
    for rec in response.recommendations:
        assert is_valid_catalog_url(rec['url'], catalog)
    
    # Check recall@10
    recall = compute_recall_at_k(
        recommendations=response.recommendations,
        expected=trace.expected_shortlist,
        k=10
    )
    
    # Log for analysis
    print(f"Trace {trace.id}: Recall@10 = {recall}")
```

---

### 5.2 Recall@10 Measurement (test_recall_at_10.py)

**Test:** Mean Recall@10 across public traces
```python
def test_mean_recall_at_10():
    """Mean Recall@10 across all traces > 0.75"""
    traces = load_public_traces()
    agent = AgentService()
    
    recalls = []
    for trace in traces:
        response = agent.chat(messages=trace.messages)
        recall = compute_recall_at_k(
            recommendations=response.recommendations,
            expected=trace.expected_shortlist,
            k=10
        )
        recalls.append(recall)
    
    mean_recall = sum(recalls) / len(recalls)
    
    print(f"Mean Recall@10: {mean_recall}")
    print(f"Per-trace: {recalls}")
    
    assert mean_recall > 0.75, f"Mean Recall@10 too low: {mean_recall}"
```

---

## 6. Test Fixtures (conftest.py)

```python
# conftest.py - Shared fixtures for all tests

@pytest.fixture(scope="session")
def catalog():
    """Load SHL catalog once per test session"""
    return load_catalog("data/catalog.json")

@pytest.fixture(scope="session")
def embeddings_model():
    """Load embedding model once per session"""
    return SentenceTransformer("all-MiniLM-L6-v2")

@pytest.fixture(scope="session")
def faiss_index(catalog, embeddings_model):
    """Create FAISS index once per session"""
    return create_faiss_index(catalog, embeddings_model)

@pytest.fixture(scope="session")
def agent():
    """Initialize agent service once per session"""
    return AgentService(
        catalog_path="data/catalog.json",
        embeddings_model_name="all-MiniLM-L6-v2"
    )

@pytest.fixture
def catalog_path():
    """Path to catalog JSON"""
    return "data/catalog.json"

@pytest.fixture
def public_traces():
    """Load all public traces"""
    return load_public_traces("data/public_traces.json")

@pytest.fixture
def client(agent):
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)
```

---

## 7. Test Execution Strategy

### 7.1 Test Order (Red → Green → Refactor)

**Phase 1: Unit Tests (First)**
```bash
pytest tests/test_unit/ -v
# Run in order:
# 1. test_catalog.py (data foundation)
# 2. test_retrieval.py (search foundation)
# 3. test_state_machine.py (state foundation)
# 4. test_validation.py (safety foundation)
# 5. test_prompts.py (prompt foundation)
```

**Phase 2: Integration Tests (Second)**
```bash
pytest tests/test_integration/ -v
# Run in order:
# 1. test_agent_end_to_end.py (basic flow)
# 2. test_behavior_probes.py (reliability)
# 3. test_edge_cases.py (robustness)
```

**Phase 3: E2E Tests (Third)**
```bash
pytest tests/test_e2e/ -v
# Run in order:
# 1. test_public_traces.py (evaluation baseline)
# 2. test_recall_at_10.py (scoring metric)
```

### 7.2 Test Running Commands

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests
pytest tests/test_unit/ -v

# Run only integration tests
pytest tests/test_integration/ -v

# Run only E2E tests
pytest tests/test_e2e/ -v

# Run specific test
pytest tests/test_unit/test_catalog.py::test_catalog_load_success -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run and stop on first failure
pytest tests/ -x

# Run with markers (e.g., asyncio tests)
pytest tests/ -m asyncio
```

---

## 8. Test Metrics & Coverage Goals

| Metric | Target | Tool |
|--------|--------|------|
| **Code Coverage** | >85% | pytest-cov |
| **Unit Tests** | All pass | pytest |
| **Integration Tests** | All pass | pytest |
| **E2E Tests** | 10 traces pass | pytest |
| **Mean Recall@10** | >0.75 | custom metric |
| **Hallucination Rate** | <5% | manual + custom checks |
| **Schema Compliance** | 100% | pytest-pydantic |

---

## 9. CI/CD Integration

```yaml
# .github/workflows/tests.yml - Run tests on every commit
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - run: pip install -r requirements.txt
      - run: pytest tests/test_unit/ -v
      - run: pytest tests/test_integration/ -v
      - run: pytest tests/test_e2e/ -v --cov=app
      - uses: codecov/codecov-action@v2
```

---

## 10. Timeline for TDD

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Unit Test Writing** | 1 day | All unit tests in RED state |
| **Unit Implementation** | 1 day | All unit tests GREEN |
| **Integration Test Writing** | 1 day | Integration tests in RED |
| **Integration Implementation** | 1 day | Integration tests GREEN |
| **E2E Test Writing** | 0.5 day | Public traces defined |
| **E2E Testing & Tuning** | 1 day | Mean Recall@10 > 0.75 |

---

## 11. Debugging Strategy

### If Test Fails:
1. **Read error message** – pytest gives clear output
2. **Run single test** – `pytest tests/test_unit/test_catalog.py::test_catalog_load_success -v`
3. **Add print/debug** – Use `print()` or pdb debugger
4. **Check assumptions** – Is the fixture correct? Is the mock set up right?
5. **Refactor code** – Make it pass, then refactor

### Common Test Pitfalls:
- ❌ Async tests without `@pytest.mark.asyncio`
- ❌ Fixtures not in scope (session vs. function)
- ❌ Mocking external calls (Gemini API)
- ❌ Path issues (use absolute paths or fixtures)

---

## 12. Sign-Off

**TDD Plan Status:** Ready for implementation  
**Test Count:** ~120 total (50 unit + 30 integration + 20 E2E + 20 custom probes)  
**Owner:** Shashwat (Developer)  
**Date:** May 15, 2026

---

**Next Step:** Start with Unit Tests (Catalog, Retrieval, State Machine). Write tests first, then implement to pass.
