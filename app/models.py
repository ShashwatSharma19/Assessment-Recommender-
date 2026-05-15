"""Pydantic models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in the conversation."""
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="The message content")


class ChatRequest(BaseModel):
    """Request body for /chat endpoint."""
    messages: List[Message] = Field(..., description="Conversation history including new user message")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "I'm hiring a Java developer"},
                    {"role": "assistant", "content": "What seniority level?"},
                    {"role": "user", "content": "Mid-level, around 4 years"},
                ]
            }
        }


class AssessmentRecommendation(BaseModel):
    """A single assessment recommendation."""
    name: str = Field(..., description="Assessment name")
    url: str = Field(..., description="URL to assessment in SHL catalog")
    test_type: str = Field(..., description="K=Knowledge, C=Cognitive, P=Personality")


class ChatResponse(BaseModel):
    """Response body for /chat endpoint."""
    reply: str = Field(..., description="The agent's response message")
    recommendations: List[AssessmentRecommendation] = Field(
        default_factory=list,
        description="Empty when clarifying/refusing, 1-10 items when recommending"
    )
    end_of_conversation: bool = Field(
        default=False,
        description="True only when agent has committed to a shortlist"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reply": "Based on your needs for a mid-level Java developer, here are 5 assessments I recommend.",
                "recommendations": [
                    {
                        "name": "Java 8 (New)",
                        "url": "https://www.shl.com/solutions/products/java/",
                        "test_type": "K"
                    },
                    {
                        "name": "OPQ32r",
                        "url": "https://www.shl.com/solutions/products/opq32r/",
                        "test_type": "P"
                    }
                ],
                "end_of_conversation": False
            }
        }


class HealthResponse(BaseModel):
    """Response for health check endpoint."""
    status: str = Field(..., description="Status - should be 'ok'")

    class Config:
        json_schema_extra = {
            "example": {"status": "ok"}
        }
