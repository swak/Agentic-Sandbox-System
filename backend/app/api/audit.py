"""
API endpoints for audit logs and metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import logging

from app.models.database import get_db
from app.models.agent import Conversation, AuditLog, APIUsage

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/logs")
async def get_conversation_logs(
    agent_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation logs with optional filtering.

    - **agent_id**: Filter by agent UUID (optional)
    - **limit**: Maximum number of results (default: 50)
    - **offset**: Number of results to skip (default: 0)
    """
    try:
        query = select(Conversation).order_by(Conversation.timestamp.desc())

        if agent_id:
            import uuid
            query = query.where(Conversation.agent_id == uuid.UUID(agent_id))

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        conversations = result.scalars().all()

        return {
            "conversations": [conv.to_dict() for conv in conversations],
            "total": len(conversations),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "LOGS_FAILED",
                    "message": "Failed to retrieve logs",
                    "details": str(e)
                }
            }
        )


@router.get("/usage")
async def get_api_usage(
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get API usage metrics.

    - **agent_id**: Filter by agent UUID (optional)
    """
    try:
        query = select(
            func.sum(APIUsage.tokens_used).label('total_tokens'),
            func.sum(APIUsage.cost_usd).label('total_cost'),
            func.count(APIUsage.id).label('request_count')
        )

        if agent_id:
            import uuid
            query = query.where(APIUsage.agent_id == uuid.UUID(agent_id))

        result = await db.execute(query)
        row = result.first()

        return {
            "total_tokens": int(row.total_tokens or 0),
            "total_cost_usd": float(row.total_cost or 0),
            "request_count": int(row.request_count or 0)
        }

    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "USAGE_FAILED",
                    "message": "Failed to retrieve usage metrics",
                    "details": str(e)
                }
            }
        )


@router.get("/export")
async def export_logs(
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Export conversation logs as JSON.

    - **agent_id**: Filter by agent UUID (optional)
    """
    try:
        query = select(Conversation).order_by(Conversation.timestamp.desc())

        if agent_id:
            import uuid
            query = query.where(Conversation.agent_id == uuid.UUID(agent_id))

        result = await db.execute(query)
        conversations = result.scalars().all()

        export_data = {
            "export_date": "2025-01-15T10:30:00Z",
            "agent_id": agent_id,
            "total_conversations": len(conversations),
            "conversations": [conv.to_dict() for conv in conversations]
        }

        return export_data

    except Exception as e:
        logger.error(f"Error exporting logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "EXPORT_FAILED",
                    "message": "Failed to export logs",
                    "details": str(e)
                }
            }
        )
