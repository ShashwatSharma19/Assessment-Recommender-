# SHL Conversational Assessment Recommender
## Product Requirements Document (PRD)

**Project Name:** Build a Conversational SHL Assessment Recommender  
**Client:** SHL Labs  
**Role:** AI Intern (Take-home Assignment)  
**Status:** In Development  
**Last Updated:** May 15, 2026

---

## 1. Executive Summary

Build a **conversational FastAPI agent** that helps hiring managers discover SHL assessments through natural dialogue. Users start with vague intent ("I need a Java developer test"), the agent clarifies through targeted questions, and returns 1–10 grounded recommendations from SHL's catalog.

**Key Constraint:** Zero hallucination. Every URL must come from the scraped SHL catalog.

---

## 2. Problem Statement

Hiring managers don't know exactly what they want until they describe it. Existing assessment catalogs require keyword search (assumes user knows vocabulary), making discovery slow and shallow.

**Solution:** Conversational agent that takes user from vague intent → grounded shortlist via dialogue.

---

## 3. Success Criteria (Scoring)

### 3.1 Hard Evals (MUST PASS)
- ✅ **Schema compliance** – Every response matches exact JSON structure
- ✅ **Catalog-only URLs** – All recommendations from scraped SHL catalog only
- ✅ **Turn cap** – Conversation ≤ 8 turns (user + assistant)

### 3.2 Recall@10 (60% of score)
- **Mean Recall@10** across 10 public + N holdout traces
- Recall@K = (relevant tests in top-10) / (total relevant tests for query)
- **Target:** >0.75 Mean Recall@10

### 3.3 Behavior Probes (20% of score)
- ✅ Agent refuses off-topic ("What's the best salary for engineers?")
- ✅ Agent does NOT recommend on turn 1 for vague queries
- ✅ Agent honors mid-conversation refinements ("Actually, add personality tests")
- ✅ Low hallucination % (<5%)
- ✅ Handles user corrections gracefully

---

## 4. Functional Requirements

### 4.1 Core Endpoints

#### GET /health
- **Request:** None
- **Response:** `{"status": "ok"}` with HTTP 200
- **Purpose:** Readiness check (up to 2 min cold start allowed)
- **Implementation:** Simple health check

#### POST /chat
- **Request:**
  ```json
  {
    "messages": [
      {"role": "user", "content": "Hiring a Java developer..."},
      {"role": "assistant", "content": "Sure. What is seniority level?"},
      {"role": "user", "content": "Mid-level, around 4 years"}
    ]
  }
  ```

- **Response:**
  ```json
  {
    "reply": "Got it. Here are 5 assessments...",
    "recommendations": [
      {"name": "Java 8 (New)", "url": "https://www.shl.com/...", "test_type": "K"},
      {"name": "OPQ32r", "url": "https://www.shl.com/...", "test_type": "P"}
    ],
    "end_of_conversation": false
  }
  ```

- **Constraints:**
  - Stateless (no server-side session storage)
  - Max 30s timeout per call
  - Schema non-negotiable (breaks automated grader if violated)
  - `recommendations` array: empty (if clarifying/refusing) OR 1–10 items (if recommending)
  - `end_of_conversation`: true only when shortlist committed

---

### 4.2 Agent Conversational Behaviors

The agent must handle **four core behaviors**:

#### 1. **CLARIFY** (Gathering Context)
- **When:** User intent is vague ("I need an assessment")
- **How:** Ask targeted questions to ground context
- **Example:**
  - User: "I'm hiring a developer"
  - Agent: "What type of developer? (e.g., Java, Python, Frontend)"
- **Turn limit:** Must clarify within 3–4 turns before recommending
- **Response:** `recommendations: []` (empty)

#### 2. **RECOMMEND** (Ready to Shortlist)
- **When:** Agent has enough context (role + seniority + domain + focus)
- **How:** Return 1–10 assessments from catalog with URLs
- **Example:**
  - Agent: "Based on mid-level Java developer with stakeholder focus, I recommend..."
  - Return: 5–7 top-ranked tests
- **Response:** `recommendations: [...]` (1–10 items), `end_of_conversation: true`

#### 3. **REFINE** (Accepting Edits)
- **When:** User changes constraints mid-conversation
- **Example:**
  - User: "Actually, add personality assessment tests"
  - Agent: Updates context, re-ranks recommendations
- **Key:** Don't restart conversation, update existing shortlist
- **Response:** New `recommendations` array (updated), `end_of_conversation: true`

#### 4. **COMPARE** (Grounded Comparison)
- **When:** User asks "What's the difference between OPQ and GSA?"
- **How:** Answer from catalog data, NOT model's prior knowledge
- **Example:**
  - Extract OPQ description + GSA description from catalog
  - Synthesize comparison grounded in actual catalog content
- **Key:** Force LangChain retriever to fetch and ground answer
- **Response:** `recommendations: []` (comparison, not recommendation)

---

### 4.3 Scope & Boundaries

#### ✅ IN SCOPE
- SHL Individual Test Solutions only (Job Solutions out of scope)
- Recommend assessments based on role, seniority, industry, skill focus
- Clarify vague queries
- Support comparison between assessments
- Handle mid-conversation refinement

#### ❌ OUT OF SCOPE (Refuse these)
- General hiring advice ("What should I pay a senior dev?")
- Legal/compliance questions ("What EEOC says about assessments?")
- Non-SHL tools ("Should I use competitors' tests?")
- Prompt injection attempts
- Any recommendation outside SHL catalog

---

## 5. Technical Requirements

### 5.1 Stack
- **API Framework:** FastAPI + Uvicorn
- **LLM:** Gemini 2.0 Flash (Google)
- **Agentic Framework:** LangChain (ReAct agent)
- **Retrieval:**
  - Vector search: FAISS + Sentence-Transformers MiniLM-L6-v2
  - Keyword search: BM25
  - Hybrid ranking: Combine both scores
- **State Management:** Explicit state machine (gathering_context → ready_to_recommend → comparing → done)
- **Validation:** Post-response URL validation against catalog
- **Deployment:** Render (free tier)

### 5.2 Catalog Structure
**Data Format (JSON):**
```json
{
  "assessments": [
    {
      "id": "java_8_new",
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/...",
      "description": "Assesses Java 8 programming knowledge...",
      "test_type": "K",
      "target_roles": ["Backend Developer", "Java Developer", "Full-Stack"],
      "domains": ["Technical", "Programming", "Java"],
      "seniority_levels": ["Junior", "Mid-level", "Senior"],
      "duration_minutes": 45,
      "question_count": 40
    }
  ]
}
```

### 5.3 State Machine States

```
[START]
  ↓
[GATHERING_CONTEXT]
  ├─ Ask: Role?
  ├─ Ask: Seniority?
  ├─ Ask: Industry focus?
  ├─ Ask: Key skill areas?
  ↓
[READY_TO_RECOMMEND]
  ├─ Retrieve from hybrid search
  ├─ Re-rank using LangChain
  ├─ Validate URLs
  ↓
[RECOMMENDING]
  ├─ Return 1–10 assessments
  ↓
[COMPARING] (Optional, if user asks)
  ├─ Ground answer in catalog
  ├─ Return without recommendations
  ↓
[DONE] (end_of_conversation: true)
```

### 5.4 Constraints

| Constraint | Value | Reason |
|-----------|-------|--------|
| Max turns | 8 | Evaluator cap |
| Max timeout | 30s | Evaluator cap |
| Cold start | 2 min | Allowed for Render |
| Min recommendations | 1 | Must provide something |
| Max recommendations | 10 | Assignment spec |
| Hallucination rate | <5% | Behavior probe |
| Recall@10 target | >0.75 | Scoring metric |

---

## 6. Data & Integration

### 6.1 Catalog Ingestion
- **Source:** https://www.shl.com/solutions/products/product-catalog/
- **Scope:** Individual Test Solutions only (filter out Job Solutions)
- **Scraping:** BeautifulSoup + requests (fallback to Playwright if JS rendering needed)
- **Output:** `catalog.json` with 50–100+ assessments

### 6.2 Vector Embeddings
- **Model:** Sentence-Transformers MiniLM-L6-v2
- **What to embed:** Assessment name + description + target roles
- **Storage:** FAISS index (local, no API calls)
- **Dimension:** 384D vectors

### 6.3 Public Traces (Evaluation Data)
- **Source:** SHL provides 10 conversation traces (download from assignment link)
- **Format:** JSON with:
  - `persona`: User profile (e.g., "hiring manager for backend role")
  - `facts`: Context user will provide ("3 years seniority", "Python focus")
  - `expected_shortlist`: Ground truth (5–8 correct assessments)
- **Usage:** Dev/test baseline before submission

---

## 7. Non-Functional Requirements

### 7.1 Performance
- **Latency:** <30s per /chat call (30s evaluator timeout)
  - Retrieval: <1s (FAISS + BM25)
  - LLM inference: <5s
  - Post-processing: <1s
- **Cold start:** Up to 2 min allowed (Render free tier)
- **Throughput:** Not critical (single-instance)

### 7.2 Reliability
- **Availability:** 99% (Render SLA)
- **Graceful degradation:** If catalog fails to load, return error (don't hallucinate)
- **Fallback:** If embeddings unavailable, fall back to BM25 only

### 7.3 Security
- **No sensitive data:** No API keys in responses
- **Input validation:** Sanitize user input (prevent injection)
- **Rate limiting:** Not required (stateless, no abuse surface)

### 7.4 Maintainability
- **Code clarity:** Clear variable names, docstrings on functions
- **Testability:** Modular functions (retrieval, state, LLM calls separate)
- **Documentation:** 2-page approach doc + inline comments

---

## 8. Evaluation Approach

### 8.1 Automated Harness (SHL's Grading)
- Simulates LLM-based user following conversation trace
- Runs multi-turn conversation against `/chat`
- Evaluates:
  - Hard evals (schema, URLs, turn cap)
  - Recall@10 on final recommendations
  - Behavior probes (off-topic refusal, no turn-1 recommend, etc.)

### 8.2 Manual Testing (Our Baseline)
- **Unit tests:** Catalog loading, URL validation, state transitions
- **Integration tests:** Full conversation on 10 public traces
- **Custom probes:** 
  - Vague query on turn 1 → should clarify, no recommendations
  - Off-topic question → should refuse
  - Mid-conversation edit → should update recommendations
  - Comparison request → should ground answer in catalog

### 8.3 Metrics to Track
- Recall@10 on each trace (target: >0.75)
- Hallucination count (target: 0)
- Turn count per trace (target: ≤8)
- Response time (target: <15s avg)

---

## 9. Deployment

### 9.1 Hosting
- **Platform:** Render (free tier)
- **Docker:** Standard Python image with requirements.txt
- **Environment variables:**
  - `GEMINI_API_KEY` (from Google)
  - `CATALOG_PATH` (path to catalog.json)

### 9.2 Submission
- **Public API URL:** e.g., `https://shl-recommender.onrender.com`
- **Both endpoints ready:**
  - `GET /health` → responds with {"status": "ok"}
  - `POST /chat` → full agent logic

### 9.3 Approach Document (2 pages max)
- Design choices (why LangChain, why Gemini, why hybrid retrieval)
- Retrieval setup (FAISS + BM25, re-ranking strategy)
- Prompt design (system prompt structure, CoT strategy)
- Evaluation approach (testing, Recall@10 measurement)
- What didn't work (iterations, debugging notes)

---

## 10. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup & Data | 2 days | Catalog scraped, traces analyzed |
| Core Agent | 2 days | FastAPI + LangChain skeleton working |
| Retrieval & Ranking | 1 day | FAISS + BM25 hybrid, tested |
| Prompt & State | 1 day | System prompt tuned, state machine working |
| Testing & Iteration | 1 day | Public traces tested, Recall@10 measured |
| Deployment | 1 day | Deployed to Render, approach doc written |

---

## 11. Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| Low Recall@10 | Medium | Early testing on public traces, iterative re-ranking tuning |
| Hallucinations (URLs) | Medium | Post-response validation, catalog URL allowlist |
| Turn cap exceeded | Low | Explicit turn counter, aggressive early clarification |
| LLM latency >30s | Low | Use Gemini Flash (fast), minimize retrieval overhead |
| Catalog scraping fails | Medium | Manual JSON as fallback, BeautifulSoup → Playwright fallback |
| Schema mismatch | High | Pydantic validation, strict JSON structure checks |

---

## 12. Acceptance Criteria

### MVP (Minimum Viable)
- [x] Scrape SHL catalog (50+ assessments)
- [x] FastAPI with /health and /chat endpoints
- [x] LangChain agent integrated
- [x] FAISS + BM25 retrieval working
- [x] State machine (clarify → recommend → done)
- [x] All responses match schema
- [x] No hallucinated URLs (catalog validation)

### Target (High Score)
- [x] Recall@10 >0.75 on public traces
- [x] All behavior probes pass (off-topic refusal, no turn-1 recommend, edits honored)
- [x] Hallucination <5%
- [x] Deployed & live on Render
- [x] Approach document (2 pages, defensible choices)

---

## 13. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Schema Compliance** | 100% | Every response matches JSON structure |
| **Catalog-Only URLs** | 100% | All URLs validated against scraped catalog |
| **Turn Cap** | ≤8 turns | Explicit counter in code |
| **Recall@10** | >0.75 | Mean Recall@10 across public + holdout traces |
| **Off-Topic Refusal** | 100% | Passes behavior probe |
| **No Turn-1 Recommend** | 100% | Vague query on turn 1 → clarify, no recommendations |
| **Edit Honoring** | 100% | Mid-conversation refinement updates shortlist |
| **Hallucination Rate** | <5% | URL validation + manual inspection |

---

## 14. Questions & Clarifications

**Q: What if a test matches multiple categories?**  
A: That's fine. Hybrid ranking will surface it based on relevance score. Top-10 can have overlap.

**Q: How deep should "Compare" answers go?**  
A: Grounded in catalog data (2–3 key differences). Don't make up details.

**Q: What if user asks for 0 assessments?**  
A: Refuse gracefully. "I recommend at least 1 assessment to properly evaluate the role."

**Q: Can I recommend the same assessment multiple times?**  
A: No. Top-10 should be distinct tests.

---

## 15. Sign-Off

**Status:** Ready for TDD & Implementation  
**Owner:** Shashwat (Developer)  
**Stakeholder:** SHL Labs (Evaluator)  
**Date:** May 15, 2026  

---

**Next Step:** Move to TDD Plan (test cases first, then implementation).
