"""
Agent manager service for agent lifecycle management.
"""

import logging
import json
import os
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.agent import Agent
from app.config import settings
from app.services.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages agent lifecycle: create, read, update, delete."""

    def __init__(self, db: AsyncSession):
        """
        Initialize agent manager.

        Args:
            db: Database session
        """
        self.db = db
        self.config_manager = ConfigManager()

    async def create_agent(
        self,
        name: str,
        agent_type: str,
        api_provider: str,
        model: str,
        system_prompt: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> Agent:
        """
        Create a new agent.

        Args:
            name: Agent name
            agent_type: Type of agent (chat, task_planner)
            api_provider: API provider (openai, anthropic)
            model: Model name
            system_prompt: System prompt
            api_key: API key (optional)

        Returns:
            Created Agent object
        """
        try:
            # Create agent object
            agent = Agent(
                name=name,
                type=agent_type,
                api_provider=api_provider,
                model=model,
                system_prompt=system_prompt or "You are a helpful AI assistant.",
                status='active'
            )

            # Encrypt and store API key if provided
            if api_key:
                # TODO: Implement encryption using pgcrypto
                agent.api_key_encrypted = api_key

            # Build config JSON
            config_json = {
                "name": name,
                "type": agent_type,
                "api_provider": api_provider,
                "model": model,
                "system_prompt": system_prompt,
                "settings": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            agent.config_json = config_json

            # Save to database
            self.db.add(agent)
            await self.db.flush()  # Get agent ID

            # Save config to JSON file
            await self.config_manager.save_config(str(agent.id), config_json)

            await self.db.commit()
            logger.info(f"Agent created: {agent.id} - {name}")

            return agent

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create agent: {str(e)}", exc_info=True)
            raise

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent UUID

        Returns:
            Agent object or None
        """
        try:
            query = select(Agent).where(Agent.id == uuid.UUID(agent_id))
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get agent: {str(e)}", exc_info=True)
            raise

    async def update_agent(self, agent_id: str, updates: dict) -> Agent:
        """
        Update agent configuration.

        Args:
            agent_id: Agent UUID
            updates: Dictionary of fields to update

        Returns:
            Updated Agent object
        """
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")

            # Update fields
            for key, value in updates.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

            # Update config JSON
            if agent.config_json:
                agent.config_json.update(updates)

            await self.db.commit()
            logger.info(f"Agent updated: {agent_id}")

            return agent

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update agent: {str(e)}", exc_info=True)
            raise
