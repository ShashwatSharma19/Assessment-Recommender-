"""FastAPI application for SHL Assessment Recommender."""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ChatRequest, ChatResponse, HealthResponse, AssessmentRecommendation
from app.catalog import load_catalog, Assessment
from app.retrieval import HybridRetriever
from app.state import ConversationStateMachine
from app.validation import (
    is_off_topic, looks_like_jailbreak_attempt, validate_recommendations, sanitize_output
)
from app.prompts import (
    SYSTEM_PROMPT, generate_clarification_question, generate_refusal,
    generate_recommendation_summary
)

# Initialize FastAPI app
app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational agent to help select SHL assessments",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load catalog
CATALOG_PATH = "data/catalog.json"
try:
    catalog = load_catalog(CATALOG_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load catalog: {e}")

# Initialize retriever
try:
    retriever = HybridRetriever(catalog)
except Exception as e:
    print(f"Warning: Could not initialize retriever with embeddings: {e}")
    retriever = None


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat endpoint for assessment recommendations.

    Stateless: each request carries full conversation history.
    """
    try:
        # Validate request
        if not request.messages or len(request.messages) == 0:
            raise HTTPException(status_code=400, detail="No messages provided")

        # Extract conversation history
        messages = request.messages
        last_user_message = None

        # Find the last user message
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_message = msg.content
                break

        if not last_user_message:
            raise HTTPException(status_code=400, detail="No user message in history")

        # Check for jailbreak/injection attempts
        if looks_like_jailbreak_attempt(last_user_message):
            return ChatResponse(
                reply=generate_refusal("jailbreak"),
                recommendations=[],
                end_of_conversation=False
            )

        # Check for off-topic queries
        if is_off_topic(last_user_message):
            reason = "off_topic"
            if "legal" in last_user_message.lower():
                reason = "legal"
            elif "salary" in last_user_message.lower() or "pay" in last_user_message.lower():
                reason = "salary"

            return ChatResponse(
                reply=generate_refusal(reason),
                recommendations=[],
                end_of_conversation=False
            )

        # Initialize state machine for this conversation
        state_machine = ConversationStateMachine(max_turns=8)

        # Count existing turns
        user_turn_count = sum(1 for m in messages if m.role == "user")
        state_machine.turn_count = user_turn_count

        # If we have enough turns and only a vague query, clarify first
        if user_turn_count == 1:
            # First turn: check if query is specific enough
            if not _has_sufficient_context(last_user_message):
                reply = "I'd like to help you find the right assessment. " + \
                        generate_clarification_question({})
                return ChatResponse(
                    reply=reply,
                    recommendations=[],
                    end_of_conversation=False
                )

        # Extract context from conversation
        context = _extract_context(messages)
        state_machine.gathered_context.update_from_dict(context)

        # If we still don't have enough context, ask for clarification
        if not context.get("role") and not context.get("domains") and not context.get("test_type_preference"):
            reply = "To find the right assessment, " + generate_clarification_question(context)
            return ChatResponse(
                reply=reply,
                recommendations=[],
                end_of_conversation=False
            )

        # If we have enough context, provide recommendations
        if context.get("role") or context.get("domains") or context.get("test_type_preference"):
            # Perform search
            search_query = _build_search_query(context)
            if retriever:
                # Use weights favoring BM25 for better keyword matching on roles
                results = retriever.search(search_query, k=10, weights=(0.4, 0.6))
            else:
                # Fallback to catalog search if retriever not available
                results = _fallback_search(catalog, context)

            # Filter results
            results = _filter_results(results, context)
            results = results[:10]  # Max 10 recommendations

            if results:
                # Build response
                recommendations = [
                    AssessmentRecommendation(
                        name=a.name,
                        url=a.url,
                        test_type=a.test_type
                    )
                    for a in results
                ]

                # Validate URLs
                validation = validate_recommendations([r.model_dump() for r in recommendations], catalog)
                if not validation["valid"]:
                    # Fallback: filter out invalid recommendations
                    recommendations = [r for r in recommendations if r.url in [a.url for a in catalog.assessments]]

                reply = generate_recommendation_summary(results, context)
                reply += f"\n\nI found {len(recommendations)} relevant assessment(s) for you."

                return ChatResponse(
                    reply=sanitize_output(reply),
                    recommendations=recommendations,
                    end_of_conversation=len(recommendations) > 0
                )

        # Default: ask for more information
        reply = "To find the right assessment, " + generate_clarification_question(context)
        return ChatResponse(
            reply=reply,
            recommendations=[],
            end_of_conversation=False
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in chat endpoint: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _has_sufficient_context(user_message: str) -> bool:
    """Check if user message provides sufficient context."""
    message_lower = user_message.lower()

    # Keywords that indicate sufficient context
    sufficient_keywords = [
        "developer", "manager", "engineer", "analyst",
        "java", "python", "javascript", "sql",
        "cognitive", "personality", "behavioral",
        "junior", "mid", "senior", "executive",
    ]

    return any(kw in message_lower for kw in sufficient_keywords)


def _extract_context(messages: list) -> dict:
    """Extract context from conversation messages."""
    context = {
        "role": None,
        "seniority": None,
        "domains": [],
        "test_type_preference": [],
    }

    # Handle both Message objects and dicts
    full_text = ""
    for m in messages:
        if hasattr(m, 'content'):
            full_text += " " + m.content
        elif isinstance(m, dict):
            full_text += " " + m.get('content', '')
        else:
            full_text += " " + str(m)

    full_text = full_text.lower()

    # Extract role
    roles = ["developer", "manager", "engineer", "analyst", "architect", "designer",
             "consultant", "coordinator", "specialist", "officer", "director",
             "representative", "sales", "support", "executive", "operator"]
    for role in roles:
        if role in full_text:
            context["role"] = role.title()
            break

    # Extract seniority
    seniority_map = {
        "junior": "Junior",
        "mid": "Mid-level",
        "middle": "Mid-level",
        "senior": "Senior",
        "executive": "Executive",
        "entry": "Junior",
    }
    for key, value in seniority_map.items():
        if key in full_text:
            context["seniority"] = value
            break

    # Extract domains
    domain_keywords = {
        "technical": ["technical", "code", "programming", "python", "java", "javascript"],
        "cognitive": ["cognitive", "reasoning", "iq", "ability"],
        "behavioral": ["personality", "behavioral", "leadership", "culture"],
    }
    for domain, keywords in domain_keywords.items():
        if any(kw in full_text for kw in keywords):
            context["domains"].append(domain.title())

    # Extract test type preference
    if "personality" in full_text or "behavioral" in full_text:
        context["test_type_preference"].append("P")
    if "cognitive" in full_text or "reasoning" in full_text or "ability" in full_text:
        context["test_type_preference"].append("C")
    if "knowledge" in full_text or "skill" in full_text or "technical" in full_text:
        context["test_type_preference"].append("K")

    return context


def _build_search_query(context: dict) -> str:
    """Build a search query from context."""
    parts = []

    if context.get("role"):
        parts.append(context["role"])

    if context.get("domains"):
        parts.extend(context["domains"])

    if context.get("seniority"):
        parts.append(context["seniority"])

    return " ".join(parts) if parts else "assessment"


def _fallback_search(catalog, context: dict) -> list:
    """Fallback search using catalog methods."""
    results = []

    # Search by role
    if context.get("role"):
        results.extend(catalog.filter_by_role(context["role"]))

    # Search by domain
    for domain in context.get("domains", []):
        results.extend(catalog.filter_by_domain(domain))

    # Filter by test type
    if context.get("test_type_preference"):
        typed_results = []
        for result in results:
            if result.test_type in context["test_type_preference"]:
                typed_results.append(result)
        if typed_results:
            results = typed_results

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for r in results:
        if r.id not in seen:
            seen.add(r.id)
            unique_results.append(r)

    return unique_results


def _filter_results(assessments: list, context: dict) -> list:
    """Filter assessment results based on context."""
    results = assessments

    # Filter by test type if specified
    if context.get("test_type_preference"):
        filtered = [a for a in results if a.test_type in context["test_type_preference"]]
        if filtered:
            results = filtered

    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
