"""
API endpoints for chat interactions with agents.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid
import time

from app.models.database import get_db
from app.models.agent import Agent, Conversation, APIUsage
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_client import LLMClient
from app.services.rag_pipeline import RAGPipeline

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to an agent and receive a response.

    - **agent_id**: UUID of the agent
    - **message**: User's message
    - **stream**: Enable streaming responses (default: false)
    """
    start_time = time.time()

    try:
        # Validate UUID
        try:
            agent_uuid = uuid.UUID(agent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid agent ID format"
                    }
                }
            )

        # Get agent
        query = select(Agent).where(Agent.id == agent_uuid)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "AGENT_NOT_FOUND",
                        "message": f"Agent with ID {agent_id} not found"
                    }
                }
            )

        if agent.status != 'active':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "AGENT_INACTIVE",
                        "message": f"Agent is not active (status: {agent.status})"
                    }
                }
            )

        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(db)
        rag_context = []

        # Retrieve relevant context if RAG is enabled
        has_knowledge = await rag_pipeline.check_knowledge_base(str(agent_uuid))
        if has_knowledge:
            logger.info(f"Retrieving RAG context for agent {agent_id}")
            rag_docs = await rag_pipeline.retrieve_context(
                query=request.message,
                agent_id=str(agent_uuid),
                top_k=3
            )
            rag_context = [doc['text'] for doc in rag_docs]

        # Build messages for LLM
        messages = []

        # System prompt with RAG context
        system_content = agent.system_prompt or "You are a helpful AI assistant."
        if rag_context:
            context_text = "\n\n".join([
                f"[Document {i+1}]\n{doc}"
                for i, doc in enumerate(rag_context)
            ])
            system_content += f"\n\nUse the following context to answer questions accurately:\n\n{context_text}"

        messages.append({
            "role": "system",
            "content": system_content
        })

        # User message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # Initialize LLM client
        llm_client = LLMClient(agent.api_provider, agent.api_key_encrypted)

        # Get response from LLM
        logger.info(f"Sending request to {agent.api_provider} ({agent.model})")
        llm_response = await llm_client.chat_completion(
            messages=messages,
            model=agent.model
        )

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Save conversation to database
        conversation = Conversation(
            agent_id=agent_uuid,
            user_message=request.message,
            agent_response=llm_response['content'],
            tokens_used=llm_response['tokens_used'],
            response_time_ms=response_time_ms,
            rag_context=rag_context if rag_context else None
        )
        db.add(conversation)

        # Track API usage
        api_usage = APIUsage(
            agent_id=agent_uuid,
            api_provider=agent.api_provider,
            model=agent.model,
            tokens_used=llm_response['tokens_used'],
            cost_usd=llm_response.get('estimated_cost', '0.00')
        )
        db.add(api_usage)

        await db.commit()

        logger.info(f"Chat completed for agent {agent_id}: {response_time_ms}ms, {llm_response['tokens_used']} tokens")

        return ChatResponse(
            response=llm_response['content'],
            tokens_used=llm_response['tokens_used'],
            response_time_ms=response_time_ms,
            rag_context=rag_context if rag_context else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "CHAT_FAILED",
                    "message": "Failed to process chat request",
                    "details": str(e)
                }
            }
        )


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent status and basic metrics.

    - **agent_id**: UUID of the agent
    """
    try:
        # Validate UUID
        try:
            agent_uuid = uuid.UUID(agent_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_UUID",
                        "message": "Invalid agent ID format"
                    }
                }
            )

        # Get agent
        query = select(Agent).where(Agent.id == agent_uuid)
        result = await db.execute(query)
        agent = result.scalar_one_or_none()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "AGENT_NOT_FOUND",
                        "message": f"Agent with ID {agent_id} not found"
                    }
                }
            )

        # Get conversation count
        from sqlalchemy import func
        conv_query = select(func.count(Conversation.id)).where(Conversation.agent_id == agent_uuid)
        conv_result = await db.execute(conv_query)
        conversation_count = conv_result.scalar()

        # Get total tokens used
        tokens_query = select(func.sum(APIUsage.tokens_used)).where(APIUsage.agent_id == agent_uuid)
        tokens_result = await db.execute(tokens_query)
        total_tokens = tokens_result.scalar() or 0

        return {
            "agent_id": str(agent.id),
            "name": agent.name,
            "status": agent.status,
            "conversation_count": conversation_count,
            "total_tokens_used": total_tokens,
            "created_at": agent.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "STATUS_FAILED",
                    "message": "Failed to get agent status",
                    "details": str(e)
                }
            }
        )
