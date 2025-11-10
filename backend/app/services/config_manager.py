"""
Configuration manager service for JSON file operations.
"""

import json
import os
import aiofiles
from typing import Dict, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages JSON configuration files for agents."""

    def __init__(self):
        """Initialize config manager."""
        self.config_dir = settings.CONFIG_DIR
        os.makedirs(self.config_dir, exist_ok=True)

    def _get_config_path(self, agent_id: str) -> str:
        """Get file path for agent config."""
        return os.path.join(self.config_dir, f"agent_{agent_id}.json")

    async def save_config(self, agent_id: str, config: Dict) -> bool:
        """
        Save agent configuration to JSON file.

        Args:
            agent_id: Agent UUID
            config: Configuration dictionary

        Returns:
            True if successful
        """
        try:
            file_path = self._get_config_path(agent_id)

            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(config, indent=2))

            logger.info(f"Config saved: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}", exc_info=True)
            raise

    async def load_config(self, agent_id: str) -> Optional[Dict]:
        """
        Load agent configuration from JSON file.

        Args:
            agent_id: Agent UUID

        Returns:
            Configuration dictionary or None
        """
        try:
            file_path = self._get_config_path(agent_id)

            if not os.path.exists(file_path):
                logger.warning(f"Config file not found: {file_path}")
                return None

            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                return json.loads(content)

        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}", exc_info=True)
            return None

    async def update_config(self, agent_id: str, updates: Dict) -> bool:
        """
        Update agent configuration.

        Args:
            agent_id: Agent UUID
            updates: Fields to update

        Returns:
            True if successful
        """
        try:
            config = await self.load_config(agent_id)
            if not config:
                logger.warning(f"Config not found for agent {agent_id}")
                return False

            config.update(updates)
            return await self.save_config(agent_id, config)

        except Exception as e:
            logger.error(f"Failed to update config: {str(e)}", exc_info=True)
            raise

    async def delete_config(self, agent_id: str) -> bool:
        """
        Delete agent configuration file.

        Args:
            agent_id: Agent UUID

        Returns:
            True if successful
        """
        try:
            file_path = self._get_config_path(agent_id)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Config deleted: {file_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete config: {str(e)}", exc_info=True)
            raise
