"""
Pydantic schemas for chat-related requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for sending a message to an agent."""

    message: str = Field(..., min_length=1, description="User message")
    stream: bool = Field(default=False, description="Enable streaming responses")

    class Config:
        schema_extra = {
            "example": {
                "message": "What's your return policy?",
                "stream": False
            }
        }


class ChatResponse(BaseModel):
    """Response schema for agent chat."""

    response: str = Field(..., description="Agent's response")
    tokens_used: int = Field(..., description="Total tokens consumed")
    response_time_ms: int = Field(..., description="Response latency in milliseconds")
    rag_context: Optional[List[str]] = Field(None, description="Retrieved RAG documents")

    class Config:
        schema_extra = {
            "example": {
                "response": "We accept returns within 30 days of purchase...",
                "tokens_used": 45,
                "response_time_ms": 1230,
                "rag_context": [
                    "Q: What is your return policy? A: We accept...",
                    "...within 30 days of purchase..."
                ]
            }
        }


class ConversationResponse(BaseModel):
    """Response schema for a single conversation."""

    id: str
    agent_id: str
    user_message: str
    agent_response: str
    tokens_used: Optional[int]
    response_time_ms: Optional[int]
    rag_context: Optional[List[str]]
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "conv_123",
                "agent_id": "agent_456",
                "user_message": "What's your return policy?",
                "agent_response": "We accept returns within 30 days...",
                "tokens_used": 45,
                "response_time_ms": 1230,
                "rag_context": ["Q: What is your return policy..."],
                "timestamp": "2025-01-15T10:30:00Z"
            }
        }


class ConversationListResponse(BaseModel):
    """Response schema for listing conversations."""

    conversations: List[ConversationResponse]
    total: int

    class Config:
        schema_extra = {
            "example": {
                "conversations": [
                    {
                        "id": "conv_123",
                        "agent_id": "agent_456",
                        "user_message": "What's your return policy?",
                        "agent_response": "We accept returns...",
                        "tokens_used": 45,
                        "response_time_ms": 1230,
                        "timestamp": "2025-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }
