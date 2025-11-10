"""
SQLAlchemy models for agents and related data.
"""

from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid

from app.models.database import Base


class Agent(Base):
    """
    Agent database model.
    Stores agent configuration and metadata.
    """
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'chat', 'task_planner' (future)
    api_provider = Column(String(50), nullable=False)  # 'openai', 'anthropic'
    model = Column(String(100), nullable=False)  # 'gpt-4', 'claude-3-sonnet'
    system_prompt = Column(Text)
    config_json = Column(JSONB)  # Full JSON config
    api_key_encrypted = Column(Text)  # Encrypted API key
    status = Column(String(20), default='active')  # 'active', 'inactive', 'error'
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.type,
            "api_provider": self.api_provider,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "config_json": self.config_json,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Conversation(Base):
    """
    Conversation database model.
    Stores chat interaction logs.
    """
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    tokens_used = Column(Integer)
    response_time_ms = Column(Integer)
    rag_context = Column(JSONB)  # Retrieved documents
    timestamp = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "agent_id": str(self.agent_id),
            "user_message": self.user_message,
            "agent_response": self.agent_response,
            "tokens_used": self.tokens_used,
            "response_time_ms": self.response_time_ms,
            "rag_context": self.rag_context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class KnowledgeVector(Base):
    """
    Knowledge vector database model.
    Stores RAG embeddings with PGVector.
    """
    __tablename__ = "knowledge_vectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='CASCADE'), nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding dimension
    metadata = Column(JSONB)  # Source file, page number, etc.
    created_at = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "agent_id": str(self.agent_id),
            "chunk_text": self.chunk_text,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    """
    Audit log database model.
    Tracks system events and changes.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='SET NULL'))
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSONB)
    user_id = Column(String(255))  # Future: multi-user support
    timestamp = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class APIUsage(Base):
    """
    API usage database model.
    Tracks token consumption and costs.
    """
    __tablename__ = "api_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('agents.id', ondelete='SET NULL'))
    api_provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost_usd = Column(String(20))  # Decimal stored as string
    timestamp = Column(TIMESTAMP, server_default=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "agent_id": str(self.agent_id) if self.agent_id else None,
            "api_provider": self.api_provider,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
