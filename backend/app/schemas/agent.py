"""
Pydantic schemas for agent-related requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid


class AgentCreateRequest(BaseModel):
    """Request schema for creating a new agent."""

    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    type: str = Field(default="chat", description="Agent type (chat, task_planner)")
    api_provider: str = Field(..., description="API provider (openai, anthropic)")
    model: str = Field(..., description="Model name (gpt-4, claude-3-sonnet)")
    system_prompt: Optional[str] = Field(None, description="System prompt for the agent")
    api_key: Optional[str] = Field(None, description="API key (optional if using env var)")

    @validator('type')
    def validate_type(cls, v):
        """Validate agent type."""
        allowed_types = ['chat', 'task_planner']
        if v not in allowed_types:
            raise ValueError(f"Type must be one of: {', '.join(allowed_types)}")
        return v

    @validator('api_provider')
    def validate_api_provider(cls, v):
        """Validate API provider."""
        allowed_providers = ['openai', 'anthropic']
        if v not in allowed_providers:
            raise ValueError(f"API provider must be one of: {', '.join(allowed_providers)}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "Customer Support Bot",
                "type": "chat",
                "api_provider": "openai",
                "model": "gpt-4",
                "system_prompt": "You are a friendly customer support agent.",
                "api_key": "sk-..."
            }
        }


class AgentUpdateRequest(BaseModel):
    """Request schema for updating an agent."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status."""
        if v is not None:
            allowed_statuses = ['active', 'inactive', 'error']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "Updated Bot Name",
                "system_prompt": "You are a more helpful support agent.",
                "status": "active"
            }
        }


class AgentResponse(BaseModel):
    """Response schema for agent data."""

    id: str
    name: str
    type: str
    api_provider: str
    model: str
    system_prompt: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Customer Support Bot",
                "type": "chat",
                "api_provider": "openai",
                "model": "gpt-4",
                "system_prompt": "You are a friendly support agent.",
                "status": "active",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z"
            }
        }


class AgentListResponse(BaseModel):
    """Response schema for listing agents."""

    agents: List[AgentResponse]
    total: int

    class Config:
        schema_extra = {
            "example": {
                "agents": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Customer Support Bot",
                        "type": "chat",
                        "api_provider": "openai",
                        "model": "gpt-4",
                        "status": "active",
                        "created_at": "2025-01-15T10:30:00Z",
                        "updated_at": "2025-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }


class AgentDeleteResponse(BaseModel):
    """Response schema for agent deletion."""

    message: str
    agent_id: str

    class Config:
        schema_extra = {
            "example": {
                "message": "Agent deleted successfully",
                "agent_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
