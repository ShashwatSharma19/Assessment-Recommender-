# SHL Assessment Recommender - Implementation Roadmap
## Quick Reference Guide for Claude Code

**Start Date:** May 15, 2026  
**Target Submission:** Within 6 days  
**Status:** Ready for Development Phase  

---

## 1. Project Overview (30-Second Summary)

Build a **conversational FastAPI agent** using **LangChain** that helps hiring managers find SHL assessments.

**User Journey:**
1. User: "I need a Java developer assessment"
2. Agent: "What seniority level?"
3. User: "Mid-level, 4 years"
4. Agent: [Returns 5–7 best-fit tests from SHL catalog]

**Key Constraint:** Zero hallucination. All URLs must come from scraped SHL catalog.

---

## 2. Architecture at a Glance

```
┌─────────────────────────────────────────────────────┐
│         FastAPI Server (main.py)                    │
│  GET /health  |  POST /chat                         │
└────────┬──────────────────────────────────┬─────────┘
         │                                  │
         ▼                                  ▼
    [Health Check]              [Chat Handler]
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              [LangChain Agent]  [Retrieval]    [State Machine]
                    │              (FAISS+BM25)    (Explicit)
                    │                  │                │
                    └────────────────┬─┴────────────────┘
                                     ▼
                         [SHL Catalog (JSON)]
                         [Sentence-Transformers]
```

---

## 3. Quick Stack Reference

| Component | Choice | Why |
|-----------|--------|-----|
| **Framework** | FastAPI + Uvicorn | Simple, fast, lightweight |
| **LLM** | Gemini 2.0 Flash | Free, fast, good grounding |
| **Agentic** | LangChain (ReAct) | Best Recall@10, handles re-ranking |
| **Vector DB** | FAISS (local) | Free, fast, no API calls |
| **Keyword Search** | BM25 | Fast, explainable |
| **Embeddings** | Sentence-Transformers MiniLM-L6-v2 | Free, local, lightweight |
| **State** | Explicit StateMachine class | Reliable, turn-cap safe |
| **Deploy** | Render | Free, simple, reliable |
| **Testing** | pytest + fixtures | TDD approach |

---

## 4. File Structure (Expected)

```
shl-recommender/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, endpoints
│   ├── catalog.py                 # Load/parse catalog.json
│   ├── retrieval.py               # FAISS + BM25 search
│   ├── agent.py                   # LangChain agent setup
│   ├── state.py                   # Explicit state machine
│   ├── prompts.py                 # System prompts, CoT
│   ├── validation.py              # URL validation, schema checks
│   └── models.py                  # Pydantic models (request/response)
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── test_unit/
│   │   ├── test_catalog.py
│   │   ├── test_retrieval.py
│   │   ├── test_state_machine.py
│   │   ├── test_validation.py
│   │   └── test_prompts.py
│   ├── test_integration/
│   │   ├── test_agent_end_to_end.py
│   │   ├── test_behavior_probes.py
│   │   └── test_edge_cases.py
│   └── test_e2e/
│       ├── test_public_traces.py
│       └── test_recall_at_10.py
├── data/
│   ├── catalog.json               # Scraped SHL catalog
│   └── public_traces.json         # 10 public evaluation traces
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 5. Implementation Phases (TDD Order)

### Phase 1: Unit Tests + Implementation (Days 1–2)

**Write tests FIRST, implement to pass:**

```bash
# 1. Catalog loading & validation
pytest tests/test_unit/test_catalog.py -v
# Implement: app/catalog.py
#   - load_catalog(path)
#   - validate_structure()
#   - get_assessment_by_name()

# 2. Retrieval (FAISS + BM25)
pytest tests/test_unit/test_retrieval.py -v
# Implement: app/retrieval.py
#   - create_faiss_index()
#   - BM25Retriever class
#   - hybrid_search()

# 3. State machine
pytest tests/test_unit/test_state_machine.py -v
# Implement: app/state.py
#   - StateMachine class
#   - State enum (GATHERING, READY, RECOMMENDING, DONE)
#   - State transitions + validation

# 4. Validation
pytest tests/test_unit/test_validation.py -v
# Implement: app/validation.py
#   - is_valid_catalog_url()
#   - validate_response_schema()
#   - validate_recommendations()

# 5. Prompts
pytest tests/test_unit/test_prompts.py -v
# Implement: app/prompts.py
#   - generate_system_prompt()
#   - generate_cot_prompt()
#   - generate_refusal_prompt()
```

### Phase 2: Integration Tests + Implementation (Days 2–3)

```bash
# 1. Full agent flow
pytest tests/test_integration/test_agent_end_to_end.py -v
# Implement: app/agent.py
#   - LangChain ReAct agent setup
#   - Tool definitions (retriever tool, state updater)
#   - Message handling

# 2. Implement FastAPI endpoints
pytest tests/test_integration/ -v  # Run all integration tests
# Implement: app/main.py
#   - POST /chat handler
#   - GET /health handler
#   - Request/response validation (Pydantic models)

# 3. Behavior probes
pytest tests/test_integration/test_behavior_probes.py -v
# Refine: Prompts, state machine, validation to pass probes

# 4. Edge cases
pytest tests/test_integration/test_edge_cases.py -v
# Refine: Handle contradictions, comparisons, unknown tests
```

### Phase 3: E2E Tests + Tuning (Days 3–5)

```bash
# 1. Public traces
pytest tests/test_e2e/test_public_traces.py -v
# Debug: Which traces fail? Why?

# 2. Recall@10 measurement
pytest tests/test_e2e/test_recall_at_10.py -v
# Target: Mean Recall@10 > 0.75
# If low, improve: retrieval, prompt, re-ranking

# 3. Iterate
# - Run traces
# - Measure Recall@10
# - Identify low-scoring traces
# - Improve retrieval/ranking
# - Repeat until >0.75
```

### Phase 4: Deployment + Polish (Days 5–6)

```bash
# 1. Docker + Render
docker build -t shl-recommender .
# Deploy to Render

# 2. Test live endpoints
curl https://<your-render-url>/health
curl -X POST https://<your-render-url>/chat -d '{"messages": [...]}'

# 3. Write approach document (2 pages)
# - Design choices (why LangChain, why FAISS+BM25, etc.)
# - Retrieval setup (hybrid search strategy)
# - Prompt design (system prompt, CoT structure)
# - Evaluation approach (testing, Recall@10 measurement)
# - What didn't work (iterations, debugging)

# 4. Submit
```

---

## 6. Critical Implementation Decisions

### 6.1 Catalog Scraping
```python
# Use BeautifulSoup first
from bs4 import BeautifulSoup
import requests

response = requests.get("https://www.shl.com/solutions/products/product-catalog/")
soup = BeautifulSoup(response.content, 'html.parser')

# Extract: name, url, description, target_roles, domains
# Save to data/catalog.json
# If fails, use Playwright fallback
```

### 6.2 Vector Search (FAISS)
```python
from sentence_transformers import SentenceTransformer
import faiss

# Load model once
embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")

# Embed catalog
texts = [f"{a.name} {a.description}" for a in catalog.assessments]
embeddings = embeddings_model.encode(texts)

# Create FAISS index
index = faiss.IndexFlatL2(len(embeddings[0]))
index.add(np.array(embeddings))

# Search
query_embedding = embeddings_model.encode("Java developer")
distances, indices = index.search(np.array([query_embedding]), k=5)
```

### 6.3 BM25 Search
```python
from rank_bm25 import BM25Okapi

# Tokenize and index
corpus = [f"{a.name} {a.description}" for a in catalog.assessments]
tokenized = [doc.split() for doc in corpus]
bm25 = BM25Okapi(tokenized)

# Search
query = "Java developer"
scores = bm25.get_scores(query.split())
top_k = np.argsort(scores)[-5:][::-1]
```

### 6.4 Hybrid Search (Combine Both)
```python
def hybrid_search(query, catalog, faiss_index, bm25, k=10):
    # Get FAISS results (scaled to 0-1)
    faiss_results, faiss_scores = faiss_search(query, k)
    faiss_ranks = {r.id: (k - i) / k for i, r in enumerate(faiss_results)}
    
    # Get BM25 results (scale scores)
    bm25_scores = bm25.get_scores(query.split())
    bm25_ranks = {i: (s - min(bm25_scores)) / (max(bm25_scores) - min(bm25_scores))
                  for i, s in enumerate(bm25_scores) if s > 0}
    
    # Combine (average ranks)
    combined = {}
    for id, score in faiss_ranks.items():
        combined[id] = combined.get(id, 0) + score
    for id, score in bm25_ranks.items():
        combined[id] = combined.get(id, 0) + score
    
    # Sort and return top-k
    return sorted(combined.items(), key=lambda x: -x[1])[:k]
```

### 6.5 LangChain Agent Setup
```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool

# Define retriever tool
def retriever_tool(query):
    results = hybrid_search(query, ...)
    return f"Found assessments: {results}"

tools = [
    Tool(
        name="search_assessments",
        func=retriever_tool,
        description="Search SHL assessments by role, skill, etc."
    )
]

# Define agent
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
agent = create_react_agent(llm, tools, prompt=system_prompt)
executor = AgentExecutor(agent=agent, tools=tools, max_iterations=3)

# Run
result = executor.invoke({"input": "I need a Java developer assessment"})
```

### 6.6 State Machine
```python
from enum import Enum

class State(Enum):
    GATHERING_CONTEXT = "gathering_context"
    READY_TO_RECOMMEND = "ready_to_recommend"
    RECOMMENDING = "recommending"
    DONE = "done"

class StateMachine:
    def __init__(self):
        self.current_state = State.GATHERING_CONTEXT
        self.context = {}
        self.turn_count = 0
        self.recommendations = []
    
    def is_context_sufficient(self):
        required = {'role', 'seniority'}
        return required.issubset(self.context.keys())
    
    def process_message(self, message):
        if self.current_state == State.GATHERING_CONTEXT:
            # Extract context from message
            self.context.update(extract_context(message))
            
            if self.is_context_sufficient():
                self.current_state = State.READY_TO_RECOMMEND
        
        self.turn_count += 1
        if self.turn_count >= 8:
            self.current_state = State.DONE
```

### 6.7 Response Schema (Pydantic)
```python
from pydantic import BaseModel

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: list[Recommendation] = []
    end_of_conversation: bool = False
```

---

## 7. Key Prompts (Save These)

### System Prompt
```
You are an expert SHL assessment recommendation agent. Your role is to help 
hiring managers find the right assessments for their hiring needs.

IMPORTANT:
- You ONLY recommend from the provided assessment catalog.
- You NEVER invent or hallucinate assessment names or URLs.
- You ask clarifying questions until you have enough context:
  - Role/title (e.g., "Java Developer", "Product Manager")
  - Seniority level (e.g., "Junior", "Mid-level", "Senior")
  - Industry/domain (e.g., "Finance", "Tech", "Healthcare")
  - Key skill focus (e.g., "Technical", "Leadership", "Communication")

- Once you have enough context, recommend 1-10 assessments.
- If the user asks about off-topic topics (salary, legal, competitors),
  politely refuse and stay focused on SHL assessments.

Available assessments:
{CATALOG_CONTEXT_HERE}

Chain of thought: Think step-by-step about which assessments match the user's needs.
```

### Clarification Prompt
```
The user's request is vague. Ask ONE specific clarifying question.

Current context: {context}
User said: "{user_message}"

Ask about: {missing_field}
Example: "What level of seniority are you looking to assess?"
```

### Refusal Prompt
```
The user asked about something outside SHL assessments. Politely decline
and redirect to SHL assessment discussion.

User asked: "{user_message}"

Respond with: "I appreciate your question, but I'm specifically focused on 
helping you find the right SHL assessments..."
```

---

## 8. Testing Checklist

### Before Submission:
- [ ] Unit tests: All passing (50 tests)
- [ ] Integration tests: All passing (30 tests)
- [ ] E2E tests: All public traces run (10 traces)
- [ ] Mean Recall@10: >0.75
- [ ] Hallucination rate: <5%
- [ ] Schema compliance: 100%
- [ ] URL validation: 100%
- [ ] Turn cap: Always ≤8
- [ ] Off-topic refusal: Passes probe
- [ ] No turn-1 vague recommend: Passes probe
- [ ] Edit honoring: Passes probe
- [ ] Deployed on Render: Live endpoint
- [ ] Approach document: 2 pages, defensible

---

## 9. Common Gotchas

❌ **Don't:**
- Hardcode URLs (scrape from catalog)
- Recommend without context (always clarify first)
- Exceed 8 turns (enforce cap)
- Use model's prior knowledge for comparison (ground in catalog)
- Build custom state without testing (use TDD)

✅ **Do:**
- Test early and often (TDD approach)
- Measure Recall@10 on public traces
- Validate all URLs post-response
- Log decisions for debugging
- Document why you made each choice

---

## 10. Submission Checklist

**Required Files:**
- [ ] Public API URL (e.g., https://shl-recommender.onrender.com)
  - [ ] `/health` endpoint working
  - [ ] `/chat` endpoint working
  - [ ] Schema-compliant responses
- [ ] Approach document (2 pages max)
  - [ ] Design choices explained
  - [ ] Retrieval setup described
  - [ ] Prompt strategy documented
  - [ ] Evaluation approach explained
  - [ ] Iteration notes (what didn't work)

**Code Quality:**
- [ ] Modular code (functions, classes, clear separation)
- [ ] Docstrings on all functions
- [ ] Type hints (Python 3.10+)
- [ ] Error handling (graceful degradation)
- [ ] No hardcoded secrets in code

**Evaluation Readiness:**
- [ ] Mean Recall@10 >0.75 on public traces
- [ ] All behavior probes pass
- [ ] Hallucination rate <5%
- [ ] Schema compliance 100%
- [ ] Cold start <2 minutes
- [ ] Timeout <30 seconds per call

---

## 11. Resources & Links

**SHL Assignment:**
- Catalog: https://www.shl.com/solutions/products/product-catalog/
- Public traces: (Download from assignment link)

**Libraries:**
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/
- Gemini API: https://ai.google.dev/
- Sentence-Transformers: https://www.sbert.net/
- FAISS: https://github.com/facebookresearch/faiss
- BM25: https://github.com/dorianbrown/rank_bm25

**Deployment:**
- Render: https://render.com/
- Docker: https://docs.docker.com/

---

## 12. Quick Command Reference

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Scrape catalog (one-time)
python scripts/scrape_catalog.py

# Run tests
pytest tests/ -v
pytest tests/test_unit/ -v  # Just unit
pytest tests/test_e2e/ -v   # Just E2E

# Local development
uvicorn app.main:app --reload --port 8000

# Check coverage
pytest tests/ --cov=app --cov-report=html

# Docker
docker build -t shl-recommender .
docker run -p 8000:8000 shl-recommender
```

---

## 13. Success Indicator

When you see this, you're on track:
```
tests/test_unit/ ........................... PASSED
tests/test_integration/ .................... PASSED
tests/test_e2e/test_public_traces.py ....... PASSED
Mean Recall@10 across traces: 0.78 ✓
Hallucination check: 2/100 calls (2%) ✓
Deployed on Render ✓
Approach document (2 pages) ✓

Ready for submission!
```

---

**Next Step:** Start with Phase 1 → Write unit tests for catalog loading.

Good luck! 🚀
