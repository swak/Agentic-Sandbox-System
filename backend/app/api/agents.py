"""
API endpoints for agent management (CRUD operations).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
import logging
import uuid

from app.models.database import get_db
from app.models.agent import Agent, AuditLog
from app.schemas.agent import (
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentResponse,
    AgentListResponse,
    AgentDeleteResponse
)
from app.services.agent_manager import AgentManager
from app.services.config_manager import ConfigManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new agent.

    - **name**: Agent name (required)
    - **type**: Agent type (default: chat)
    - **api_provider**: openai or anthropic (required)
    - **model**: Model name like gpt-4, claude-3-sonnet (required)
    - **system_prompt**: Custom system prompt (optional)
    - **api_key**: API key (optional if using environment variable)
    """
    try:
        logger.info(f"Creating agent: {request.name}")

        # Initialize agent manager
        agent_manager = AgentManager(db)

        # Create agent
        agent = await agent_manager.create_agent(
            name=request.name,
            agent_type=request.type,
            api_provider=request.api_provider,
            model=request.model,
            system_prompt=request.system_prompt,
            api_key=request.api_key
        )

        # Log audit event
        audit_log = AuditLog(
            agent_id=agent.id,
            event_type="agent_created",
            event_data={
                "name": agent.name,
                "type": agent.type,
                "api_provider": agent.api_provider,
                "model": agent.model
            }
        )
        db.add(audit_log)
        await db.commit()

        logger.info(f"Agent created successfully: {agent.id}")

        return AgentResponse(
            id=str(agent.id),
            name=agent.name,
            type=agent.type,
            api_provider=agent.api_provider,
            model=agent.model,
            system_prompt=agent.system_prompt,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )

    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_CREATION_FAILED",
                    "message": "Failed to create agent",
                    "details": str(e)
                }
            }
        )


@router.get("", response_model=AgentListResponse)
async def list_agents(
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all agents with optional filtering.

    - **status**: Filter by status (active, inactive, error)
    - **type**: Filter by type (chat, task_planner)
    """
    try:
        query = select(Agent)

        # Apply filters
        if status_filter:
            query = query.where(Agent.status == status_filter)
        if type_filter:
            query = query.where(Agent.type == type_filter)

        query = query.order_by(Agent.created_at.desc())

        result = await db.execute(query)
        agents = result.scalars().all()

        agent_responses = [
            AgentResponse(
                id=str(agent.id),
                name=agent.name,
                type=agent.type,
                api_provider=agent.api_provider,
                model=agent.model,
                system_prompt=agent.system_prompt,
                status=agent.status,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
            for agent in agents
        ]

        return AgentListResponse(
            agents=agent_responses,
            total=len(agent_responses)
        )

    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_LIST_FAILED",
                    "message": "Failed to list agents",
                    "details": str(e)
                }
            }
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific agent.

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

        # Query agent
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

        return AgentResponse(
            id=str(agent.id),
            name=agent.name,
            type=agent.type,
            api_provider=agent.api_provider,
            model=agent.model,
            system_prompt=agent.system_prompt,
            status=agent.status,
            created_at=agent.created_at,
            updated_at=agent.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_GET_FAILED",
                    "message": "Failed to get agent",
                    "details": str(e)
                }
            }
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    request: AgentUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing agent.

    - **agent_id**: UUID of the agent
    - **name**: New agent name (optional)
    - **system_prompt**: New system prompt (optional)
    - **model**: New model (optional)
    - **status**: New status (optional)
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

        # Check if agent exists
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

        # Build update data
        update_data = {}
        if request.name is not None:
            update_data['name'] = request.name
        if request.system_prompt is not None:
            update_data['system_prompt'] = request.system_prompt
        if request.model is not None:
            update_data['model'] = request.model
        if request.status is not None:
            update_data['status'] = request.status

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "NO_UPDATE_DATA",
                        "message": "No fields provided for update"
                    }
                }
            )

        # Update agent
        stmt = (
            update(Agent)
            .where(Agent.id == agent_uuid)
            .values(**update_data)
        )
        await db.execute(stmt)

        # Update config file
        config_manager = ConfigManager()
        await config_manager.update_config(str(agent_uuid), update_data)

        # Log audit event
        audit_log = AuditLog(
            agent_id=agent_uuid,
            event_type="agent_updated",
            event_data=update_data
        )
        db.add(audit_log)

        await db.commit()

        # Fetch updated agent
        result = await db.execute(query)
        updated_agent = result.scalar_one()

        logger.info(f"Agent updated successfully: {agent_id}")

        return AgentResponse(
            id=str(updated_agent.id),
            name=updated_agent.name,
            type=updated_agent.type,
            api_provider=updated_agent.api_provider,
            model=updated_agent.model,
            system_prompt=updated_agent.system_prompt,
            status=updated_agent.status,
            created_at=updated_agent.created_at,
            updated_at=updated_agent.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_UPDATE_FAILED",
                    "message": "Failed to update agent",
                    "details": str(e)
                }
            }
        )


@router.delete("/{agent_id}", response_model=AgentDeleteResponse)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an agent.

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

        # Check if agent exists
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

        # Delete agent (cascade will delete related data)
        stmt = delete(Agent).where(Agent.id == agent_uuid)
        await db.execute(stmt)

        # Delete config file
        config_manager = ConfigManager()
        await config_manager.delete_config(agent_id)

        # Log audit event
        audit_log = AuditLog(
            agent_id=None,  # Agent is deleted
            event_type="agent_deleted",
            event_data={"agent_id": agent_id, "name": agent.name}
        )
        db.add(audit_log)

        await db.commit()

        logger.info(f"Agent deleted successfully: {agent_id}")

        return AgentDeleteResponse(
            message="Agent deleted successfully",
            agent_id=agent_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "AGENT_DELETE_FAILED",
                    "message": "Failed to delete agent",
                    "details": str(e)
                }
            }
        )
