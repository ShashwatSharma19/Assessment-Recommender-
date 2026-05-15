# SHL Assessment Recommender - Quick Start Checklist
## Begin Implementation Today

**Created:** May 15, 2026  
**Status:** Ready to start coding  
**Timeline:** 6 days to submission  

---

## Pre-Implementation (Today) - 2 Hours

### Documentation Review
- [ ] Read this Quick Start Checklist (5 min)
- [ ] Read Master Summary "Success Criteria" (Section 10) (5 min)
- [ ] Skim Roadmap "Quick Reference" (10 min)
- [ ] Keep PRD handy for reference

### Environment Setup
- [ ] Create project folder: `mkdir shl-recommender && cd shl-recommender`
- [ ] Create Python venv: `python -m venv venv && source venv/bin/activate`
- [ ] Create `requirements.txt` (copy from Roadmap Section 12)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create folder structure:
  ```bash
  mkdir -p app tests/{test_unit,test_integration,test_e2e} data scripts
  ```

### Data Preparation
- [ ] **Download public traces** from SHL assignment link
  - Save to: `data/public_traces.json`
- [ ] **Download catalog** (or plan to scrape)
  - Save to: `data/catalog.json` (once scraped)

---

## Phase 1: Unit Tests (Days 1–2) - Write Tests First

### Step 1.1: Catalog Tests
```bash
# File: tests/test_unit/test_catalog.py
```
- [ ] Write 5 catalog tests (see TDD Plan Section 3.1)
  - [ ] test_catalog_load_success
  - [ ] test_catalog_structure_valid
  - [ ] test_catalog_urls_valid
  - [ ] test_catalog_no_duplicates
  - [ ] test_catalog_target_roles_populated
- [ ] Run tests: `pytest tests/test_unit/test_catalog.py -v`
  - Expected: ALL RED (tests fail)
- [ ] Implement `app/catalog.py` to pass tests
  - [ ] load_catalog() function
  - [ ] Pydantic models (Assessment, Catalog)
  - [ ] Validation logic
- [ ] Run tests: `pytest tests/test_unit/test_catalog.py -v`
  - Expected: ALL GREEN (tests pass)

**Checkpoint:** Catalog loads and validates correctly ✓

---

### Step 1.2: Retrieval Tests
```bash
# File: tests/test_unit/test_retrieval.py
```
- [ ] Write 7 retrieval tests (see TDD Plan Section 3.2)
  - [ ] test_faiss_index_creation
  - [ ] test_faiss_search
  - [ ] test_bm25_search
  - [ ] test_hybrid_search
  - [ ] test_search_empty_query
  - [ ] test_search_respects_k_limit
- [ ] Run tests: `pytest tests/test_unit/test_retrieval.py -v`
  - Expected: ALL RED
- [ ] Implement `app/retrieval.py`
  - [ ] create_faiss_index()
  - [ ] BM25Retriever class
  - [ ] hybrid_search() function
  - [ ] Load SentenceTransformers model
- [ ] Run tests: `pytest tests/test_unit/test_retrieval.py -v`
  - Expected: ALL GREEN

**Checkpoint:** FAISS + BM25 search working ✓

---

### Step 1.3: State Machine Tests
```bash
# File: tests/test_unit/test_state_machine.py
```
- [ ] Write 8 state machine tests (see TDD Plan Section 3.3)
  - [ ] test_initial_state
  - [ ] test_transition_to_ready_to_recommend
  - [ ] test_transition_to_recommending
  - [ ] test_transition_to_done
  - [ ] test_invalid_state_transition
  - [ ] test_context_accumulation
  - [ ] test_context_refinement
  - [ ] test_turn_counter
  - [ ] test_turn_cap_enforcement
- [ ] Run tests: `pytest tests/test_unit/test_state_machine.py -v`
  - Expected: ALL RED
- [ ] Implement `app/state.py`
  - [ ] State enum
  - [ ] StateMachine class
  - [ ] State transitions
  - [ ] Context management
  - [ ] Turn counter
- [ ] Run tests: `pytest tests/test_unit/test_state_machine.py -v`
  - Expected: ALL GREEN

**Checkpoint:** State machine working, turn cap enforced ✓

---

### Step 1.4: Validation Tests
```bash
# File: tests/test_unit/test_validation.py
```
- [ ] Write 6 validation tests (see TDD Plan Section 3.4)
  - [ ] test_url_validation_valid
  - [ ] test_url_validation_invalid
  - [ ] test_url_injection_prevention
  - [ ] test_response_schema_valid
  - [ ] test_response_schema_missing_fields
  - [ ] test_recommendations_bounds
- [ ] Run tests: `pytest tests/test_unit/test_validation.py -v`
  - Expected: ALL RED
- [ ] Implement `app/validation.py`
  - [ ] is_valid_catalog_url()
  - [ ] validate_response_schema()
  - [ ] validate_recommendations()
- [ ] Implement `app/models.py` (Pydantic models)
  - [ ] Recommendation
  - [ ] ChatRequest
  - [ ] ChatResponse
- [ ] Run tests: `pytest tests/test_unit/test_validation.py -v`
  - Expected: ALL GREEN

**Checkpoint:** Schema validation working, URLs validated ✓

---

### Step 1.5: Prompt Tests
```bash
# File: tests/test_unit/test_prompts.py
```
- [ ] Write 4 prompt tests (see TDD Plan Section 3.5)
  - [ ] test_system_prompt_generation
  - [ ] test_prompt_includes_catalog
  - [ ] test_cot_prompt_structure
  - [ ] test_refusal_prompt
- [ ] Run tests: `pytest tests/test_unit/test_prompts.py -v`
  - Expected: ALL RED
- [ ] Implement `app/prompts.py`
  - [ ] generate_system_prompt()
  - [ ] generate_system_prompt_with_catalog()
  - [ ] generate_cot_prompt()
  - [ ] generate_refusal_prompt()
- [ ] Run tests: `pytest tests/test_unit/test_prompts.py -v`
  - Expected: ALL GREEN

**Checkpoint:** All prompts generated correctly ✓

---

### Phase 1 Summary
```bash
# Run all unit tests
pytest tests/test_unit/ -v

# Expected output:
# test_catalog.py ...................... 5 passed
# test_retrieval.py .................... 7 passed
# test_state_machine.py ................ 8 passed
# test_validation.py ................... 6 passed
# test_prompts.py ...................... 4 passed
# ===== 30 passed in X.XXs =====
```

---

## Phase 2: Integration Tests (Day 3)

### Step 2.1: Agent End-to-End
```bash
# File: tests/test_integration/test_agent_end_to_end.py
```
- [ ] Write full conversation flow test
  - [ ] test_full_conversation_flow
  - [ ] test_agent_honors_history
  - [ ] test_agent_schema_compliance
- [ ] Run tests: `pytest tests/test_integration/test_agent_end_to_end.py -v`
  - Expected: ALL RED
- [ ] Implement `app/agent.py`
  - [ ] Create LangChain agent with Gemini
  - [ ] Define retrieval tool
  - [ ] Define state management
  - [ ] Wire up ReAct loop
- [ ] Implement `app/main.py` (FastAPI)
  - [ ] POST /chat endpoint
  - [ ] GET /health endpoint
  - [ ] Request validation
  - [ ] Response validation
- [ ] Create `tests/conftest.py` (pytest fixtures)
  - [ ] Catalog fixture
  - [ ] Agent fixture
  - [ ] FastAPI TestClient fixture
- [ ] Run tests: `pytest tests/test_integration/test_agent_end_to_end.py -v`
  - Expected: ALL GREEN

**Checkpoint:** Full conversation flow working ✓

---

### Step 2.2: Behavior Probes
```bash
# File: tests/test_integration/test_behavior_probes.py
```
- [ ] Write behavior probe tests (see TDD Plan Section 4.2)
  - [ ] test_agent_refuses_off_topic
  - [ ] test_no_turn_1_recommendation_for_vague_query
  - [ ] test_turn_1_recommendation_for_specific_query
  - [ ] test_agent_honors_mid_conversation_edit
  - [ ] test_no_hallucinated_urls
  - [ ] test_agent_respects_turn_cap
- [ ] Run tests: `pytest tests/test_integration/test_behavior_probes.py -v`
  - Expected: ALL RED
- [ ] Refine prompt engineering to pass probes
  - [ ] Improve refusal prompt (off-topic)
  - [ ] Improve clarification logic (no turn-1)
  - [ ] Improve state tracking (edits)
- [ ] Run tests: `pytest tests/test_integration/test_behavior_probes.py -v`
  - Expected: ALL GREEN

**Checkpoint:** All behavior probes pass ✓

---

### Step 2.3: Edge Cases
```bash
# File: tests/test_integration/test_edge_cases.py
```
- [ ] Write edge case tests (see TDD Plan Section 4.3)
  - [ ] test_contradictory_information
  - [ ] test_comparison_request
  - [ ] test_unknown_test_name
  - [ ] test_empty_user_input
  - [ ] test_long_user_input
- [ ] Run tests: `pytest tests/test_integration/test_edge_cases.py -v`
  - Expected: ALL RED
- [ ] Implement edge case handling
  - [ ] Graceful degradation
  - [ ] Error messages
  - [ ] Input truncation/validation
- [ ] Run tests: `pytest tests/test_integration/test_edge_cases.py -v`
  - Expected: ALL GREEN

**Checkpoint:** All edge cases handled ✓

---

### Phase 2 Summary
```bash
pytest tests/test_integration/ -v

# Expected output:
# test_agent_end_to_end.py ............ 3 passed
# test_behavior_probes.py ............ 6 passed
# test_edge_cases.py ................. 5 passed
# ===== 14 passed in X.XXs =====
```

---

## Phase 3: E2E Testing & Tuning (Days 4–5)

### Step 3.1: Public Traces
```bash
# File: tests/test_e2e/test_public_traces.py
```
- [ ] Write parametrized test for 10 traces
  - [ ] test_public_trace (parametrized)
- [ ] Run tests: `pytest tests/test_e2e/test_public_traces.py -v`
  - Expected: Check results
  - [ ] Do all traces run without error?
  - [ ] Are URLs all valid?
  - [ ] Do responses match schema?

**Checkpoint:** All 10 traces run, schema valid, no hallucinations ✓

---

### Step 3.2: Recall@10 Measurement
```bash
# File: tests/test_e2e/test_recall_at_10.py
```
- [ ] Write recall measurement test
  - [ ] test_mean_recall_at_10 (>0.75 target)
- [ ] Run test: `pytest tests/test_e2e/test_recall_at_10.py -v`
  - Expected output example:
    ```
    Mean Recall@10: 0.65
    Per-trace: [0.6, 0.7, 0.8, 0.5, 0.7, 0.75, 0.8, 0.6, 0.7, 0.65]
    FAILED - Mean Recall@10 too low: 0.65
    ```

### Step 3.3: Iterative Tuning
- [ ] Identify low-scoring traces (e.g., Trace 3: Recall@10 = 0.5)
- [ ] Debug why recommendations miss relevant tests
  - [ ] Is retrieval finding the right tests?
  - [ ] Is ranking correct?
  - [ ] Is prompt setting wrong expectations?
- [ ] Improve:
  - [ ] Option 1: Tune hybrid search weights (increase FAISS vs. BM25)
  - [ ] Option 2: Improve system prompt (better grounding)
  - [ ] Option 3: Improve state detection (better context extraction)
- [ ] Re-run test: `pytest tests/test_e2e/test_recall_at_10.py -v`
  - Expected: Mean Recall@10 increases toward >0.75
- [ ] Repeat until **Mean Recall@10 > 0.75** ✓

**Checkpoint:** Mean Recall@10 > 0.75 ✓

---

### Phase 3 Summary
```bash
pytest tests/test_e2e/ -v

# Expected output:
# test_public_traces.py .............. 10 passed
# test_recall_at_10.py ............... PASSED (Mean: 0.78)
# ===== 11 passed in X.XXs =====
```

---

## Phase 4: Deployment & Submission (Day 6)

### Step 4.1: Prepare for Deployment
- [ ] Create `Dockerfile`
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY app/ ./app
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] Create `.env.example`
  ```
  GEMINI_API_KEY=your-key-here
  CATALOG_PATH=data/catalog.json
  ```
- [ ] Create `.dockerignore`
  ```
  tests
  data/public_traces.json
  venv
  __pycache__
  ```

### Step 4.2: Local Testing
- [ ] Run locally: `uvicorn app.main:app --reload --port 8000`
- [ ] Test /health: `curl http://localhost:8000/health`
  - Expected: `{"status": "ok"}`
- [ ] Test /chat:
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "Java developer"}]}'
  ```
  - Expected: Valid ChatResponse JSON

### Step 4.3: Deploy to Render
- [ ] Go to render.com
- [ ] New > Web Service
- [ ] Connect GitHub repo (or upload via CLI)
- [ ] Settings:
  - [ ] Runtime: Python 3.10
  - [ ] Build command: `pip install -r requirements.txt`
  - [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - [ ] Environment: Add `GEMINI_API_KEY=...`
- [ ] Deploy
- [ ] Wait for "Your service is live" message
- [ ] Copy public URL

### Step 4.4: Test Live Endpoints
- [ ] Test /health: `curl https://<your-render-url>/health`
- [ ] Test /chat on live endpoint
- [ ] Verify <30s timeout on live
- [ ] Verify <2 min cold start (first /health call)

### Step 4.5: Write Approach Document (2 pages max)
```markdown
# Approach Document

## 1. Design Choices
- Why LangChain? (Better Recall@10 via re-ranking)
- Why Gemini? (Free, fast, good at grounding)
- Why FAISS + BM25? (Hybrid semantic + keyword search)
- Why explicit state machine? (Reliable, testable)

## 2. Retrieval Setup
- FAISS index over assessment names + descriptions
- BM25 ranking over assessment keywords
- Hybrid scoring: FAISS weight = 0.6, BM25 weight = 0.4
- Top-10 re-ranked by LLM for final shortlist

## 3. Prompt Design
- System prompt includes top-20 catalog assessments
- CoT: Agent thinks step-by-step before recommending
- Refusal prompt for out-of-scope queries
- Post-response validation prevents hallucinations

## 4. Evaluation Approach
- 50 unit tests (RED → GREEN → REFACTOR)
- 14 integration tests (behavior probes)
- 10 E2E traces (public evaluation data)
- Recall@10 measurement and tuning

## 5. What Didn't Work
- Initial attempt: Simple keyword search → Recall@10 = 0.4
- Fix: Added FAISS vector search → Recall@10 = 0.65
- Second iteration: Improved prompt grounding → Recall@10 = 0.78

## 6. Test Results Summary
- All unit tests: ✅ 30/30 pass
- All integration tests: ✅ 14/14 pass
- Mean Recall@10: ✅ 0.78 (target: >0.75)
- Hallucination rate: ✅ 2% (target: <5%)
- Turn cap compliance: ✅ 100%
```

### Step 4.6: Final Checklist Before Submission
- [ ] All tests passing locally
  ```bash
  pytest tests/ -v
  # Expected: All green (50+ unit, 14 integration, 11 E2E)
  ```
- [ ] Live endpoints working
  - [ ] GET /health → 200 OK
  - [ ] POST /chat → 200 OK with correct schema
- [ ] Approach document written (2 pages)
- [ ] API URL documented
- [ ] No secrets in code
- [ ] Docker image tested
- [ ] Render deployment live

---

## Daily Checklist (Copy-Paste for Each Day)

### Day 1 (Phase 1.1–1.2)
- [ ] Setup environment
- [ ] Write catalog tests
- [ ] Implement catalog module
- [ ] Write retrieval tests
- [ ] Implement retrieval module
- [ ] All unit tests for catalog & retrieval pass

### Day 2 (Phase 1.3–1.5)
- [ ] Write state machine tests
- [ ] Implement state machine
- [ ] Write validation tests
- [ ] Implement validation module
- [ ] Write prompt tests
- [ ] Implement prompt module
- [ ] All 30 unit tests pass

### Day 3 (Phase 2.1–2.3)
- [ ] Write agent end-to-end tests
- [ ] Implement LangChain agent
- [ ] Implement FastAPI endpoints
- [ ] Write behavior probe tests
- [ ] Refine prompts to pass probes
- [ ] Write edge case tests
- [ ] All 14 integration tests pass

### Day 4 (Phase 3.1–3.2)
- [ ] Write public trace tests
- [ ] Run all 10 traces
- [ ] Write Recall@10 test
- [ ] Measure Mean Recall@10
- [ ] Log low-scoring traces

### Day 5 (Phase 3.3)
- [ ] Debug low-scoring traces
- [ ] Improve retrieval weights
- [ ] Improve prompts
- [ ] Re-run Recall@10 test
- [ ] Target: >0.75

### Day 6 (Phase 4)
- [ ] Prepare Docker image
- [ ] Deploy to Render
- [ ] Test live endpoints
- [ ] Write approach document
- [ ] Final submission check
- [ ] Submit!

---

## Success Signals (You're On Track If...)

✅ **Day 1 End**
- 30 unit tests all pass
- All 5 modules implemented (catalog, retrieval, state, validation, prompts)

✅ **Day 3 End**
- 44 total tests passing (30 unit + 14 integration)
- All behavior probes pass
- FastAPI endpoints working locally

✅ **Day 5 End**
- Mean Recall@10 > 0.75
- All public traces run without error
- All tests passing

✅ **Day 6 End**
- Live on Render
- Both endpoints working
- Approach document written
- Ready to submit

---

## Trouble? Use This Flowchart

```
Tests failing?
├─ RED state (test fails on implementation)?
│  └─ Implement more code
├─ Schema mismatch?
│  └─ Check Pydantic models, use validation
├─ Recall@10 low?
│  └─ Improve retrieval: Check Roadmap Phase 3
├─ Behavior probes fail?
│  └─ Refine prompts, improve state machine
└─ Timeout >30s?
   └─ Optimize retrieval, reduce prompt size
```

---

## Key Resources Bookmark These

- **PRD:** `/mnt/user-data/outputs/PRD_SHL_Assessment_Recommender.md`
- **TDD:** `/mnt/user-data/outputs/TDD_Test_Plan_SHL_Recommender.md`
- **Roadmap:** `/mnt/user-data/outputs/Implementation_Roadmap_Quick_Reference.md`
- **Summary:** `/mnt/user-data/outputs/Master_Summary_How_Documents_Connect.md`
- **This:** `/mnt/user-data/outputs/Quick_Start_Checklist.md`

---

## Now Start Coding!

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Create file structure
mkdir -p app tests/{test_unit,test_integration,test_e2e} data

# 3. Start Day 1 Phase 1.1
# Write: tests/test_unit/test_catalog.py
# Implement: app/catalog.py
# Run: pytest tests/test_unit/test_catalog.py -v

# 4. Watch it turn GREEN
# Continue to next module...
```

**Good luck! You've got this! 🚀**
