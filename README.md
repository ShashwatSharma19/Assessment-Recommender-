# SHL Conversational Assessment Recommender

A FastAPI-based conversational agent that helps hiring managers discover the right SHL assessments through natural dialogue.

## Quick Start

### Requirements
- Python 3.11+
- ~500MB disk (for embeddings model)
- ~300MB RAM (for FAISS index + embeddings)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd shl-recommender

# Install dependencies
pip install -r requirements.txt

# Run locally
python -m uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

### POST /chat
Main conversation endpoint (stateless).

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
  "reply": "Based on your needs for a mid-level Java developer, here are 5 assessments I recommend.",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/solutions/products/java/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

## Agent Behavior

### 1. Clarify
When the user's request is vague, the agent asks focused questions:
- "What role or position are you hiring for?"
- "What is the seniority level?"
- "Are you looking for technical, cognitive, or behavioral assessments?"

### 2. Recommend
Once the agent has sufficient context, it provides 1-10 relevant assessments with names and catalog URLs.

### 3. Refine
When the user changes constraints ("Actually, add personality tests"), the agent updates the recommendations.

### 4. Compare
When asked "What's the difference between OPQ and GSA?", the agent provides grounded answers from catalog data.

### 5. Refuse
The agent refuses:
- General hiring advice ("What should I pay a developer?")
- Legal questions ("Is this EEOC compliant?")
- Off-topic queries (weather, sports, etc.)

## Architecture

- **Retrieval:** Hybrid FAISS (semantic) + BM25 (keyword) search
- **State Management:** Explicit ConversationStateMachine (max 8 turns)
- **Validation:** Post-response URL validation against catalog
- **Catalog:** 25+ SHL assessments (Knowledge, Cognitive, Personality types)

See [APPROACH.md](APPROACH.md) for detailed design documentation.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_unit/test_catalog.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Deployment

### Docker

```bash
docker build -t shl-recommender .
docker run -p 8000:8000 shl-recommender
```

### Render.com

1. Push code to GitHub
2. Connect GitHub repo to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Deploy

### Railway / Fly.io

Similar to Render - these platforms support Dockerfile and Python apps natively.

## Configuration

Environment variables (optional):
- `CATALOG_PATH`: Path to catalog.json (default: `data/catalog.json`)
- `EMBEDDING_MODEL`: HuggingFace model ID (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `HF_TOKEN`: HuggingFace token for better model download rates

## Limitations

- Max 8 user turns per conversation
- Stateless design (no session persistence)
- 30-second response timeout (per specification)
- FAISS index loads on startup (not suitable for <100MB catalog)

## Future Enhancements

1. LangChain integration for more sophisticated reasoning
2. Multi-turn memory for better context tracking
3. Feedback loop to improve recommendation ranking
4. Support for custom/proprietary assessment catalogs
5. Rate limiting and authentication

## License

Proprietary (SHL Labs)

## Support

For issues or questions, please contact the development team.
