# SHL Conversational Assessment Recommender

A FastAPI-based conversational agent that helps hiring managers discover the right SHL assessments through natural dialogue. Built as part of the SHL Hiring Challenge.

## Results

| Metric | Value |
|--------|-------|
| Mean Recall@10 | 68.33% (target ≥55%) |
| Schema Compliance | 100% |
| Hallucinated URLs | 0% |
| Turn Cap Enforcement | 100% |
| Tests Passing | 63 / 63 |

## Quick Start

**Requirements:** Python 3.11+, ~500 MB disk (embedding model), ~300 MB RAM

```bash
git clone https://github.com/ShashwatSharma19/Assessment-Recommender-.git
cd Assessment-Recommender-
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API docs.

## API

### `GET /health`
```json
{ "status": "ok" }
```

### `POST /chat`

Stateless — send the full conversation history on every request.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hiring a Java developer"},
    {"role": "assistant", "content": "What seniority level?"},
    {"role": "user", "content": "Mid-level, 4 years"}
  ]
}
```

**Response:**
```json
{
  "reply": "For a mid-level Developer, I recommend:",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/java/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": true
}
```

## Agent Behaviours

| Behaviour | Trigger | Action |
|-----------|---------|--------|
| **Clarify** | Vague first message | Asks one focused question (role → seniority → domain) |
| **Recommend** | Sufficient context gathered | Returns 1–10 ranked assessments |
| **Refine** | "Actually, add personality tests" | Updates recommendations in-place |
| **Compare** | "Difference between OPQ and GSA?" | Answers from catalog data only |
| **Refuse** | Salary / legal / off-topic queries | Polite refusal, redirects to assessments |

## Architecture

```
POST /chat
    │
    ├── Jailbreak / off-topic check (regex, validation.py)
    ├── Turn-1 vagueness check → clarify if needed
    ├── Context extraction from full history
    │
    ├── HybridRetriever.search()
    │       ├── FAISS vector search  (semantic similarity, weight 0.4)
    │       └── BM25 keyword search  (exact match, weight 0.6)
    │             + name-match bonuses + competing-tech penalty
    │
    ├── Filter by test type (if specified)
    ├── URL validation against catalog (zero hallucination guarantee)
    └── Return ChatResponse
```

**Stack:** FastAPI · FAISS · BM25 · sentence-transformers (MiniLM-L6-v2) · Pydantic · pytest

## Running Tests

```bash
pytest tests/ -v
```

## Deployment (Docker)

```bash
docker build -t shl-recommender .
docker run -p 8000:8000 shl-recommender
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CATALOG_PATH` | `data/catalog.json` | Path to assessment catalog |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `HF_TOKEN` | — | HuggingFace token (optional, higher rate limits) |
