"""
MCP Connector for PostgreSQL-based Agent and Team Configuration Management

This module provides a connector class that implements the Model Context Protocol (MCP)
for managing agent and team configurations in a PostgreSQL database.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Union

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    raise ImportError("`psycopg` not installed. Please install it using `pip install psycopg2-binary`")

from agno.agent import Agent
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.models.google.gemini import Gemini

logger = logging.getLogger(__name__)


class PostgresMCPConnector:
    """
    PostgreSQL-based MCP connector for dynamic agent and team configuration management.
    
    This connector provides methods to load and save agent/team configurations
    from/to a PostgreSQL database, enabling dynamic configuration management.
    """
    
    def __init__(
        self,
        db_url: str,
        table_schema: str = "public"
    ):
        """
        Initialize the PostgreSQL MCP connector.
        
        Args:
            db_url: PostgreSQL connection URL
            table_schema: Database schema name (default: "public")
        """
        self.db_url = db_url
        self.table_schema = table_schema
        self._connection = None
    
    @property
    def connection(self):
        """Get or create a database connection."""
        if self._connection is None or self._connection.closed:
            logger.debug("Establishing new PostgreSQL connection for MCP connector.")
            self._connection = psycopg.connect(
                self.db_url,
                row_factory=dict_row,
                options=f"-c search_path={self.table_schema}"
            )
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection and not self._connection.closed:
            self._connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def load_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an agent configuration from the database.
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Dictionary containing agent configuration or None if not found
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM agents WHERE agent_id = %s AND is_active = true",
                    (agent_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error loading agent config for {agent_id}: {e}")
            return None
    
    def save_agent_config(self, agent_config: Dict[str, Any]) -> bool:
        """
        Save an agent configuration to the database.
        
        Args:
            agent_config: Dictionary containing agent configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                # Use UPSERT to insert or update
                cursor.execute("""
                    INSERT INTO agents (
                        agent_id, name, model_id, model_provider, instructions, 
                        description, system_prompt, tool_ids, memory_config, 
                        knowledge_config, session_config, additional_config, is_active
                    ) VALUES (
                        %(agent_id)s, %(name)s, %(model_id)s, %(model_provider)s, 
                        %(instructions)s, %(description)s, %(system_prompt)s, 
                        %(tool_ids)s, %(memory_config)s, %(knowledge_config)s, 
                        %(session_config)s, %(additional_config)s, %(is_active)s
                    )
                    ON CONFLICT (agent_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        model_id = EXCLUDED.model_id,
                        model_provider = EXCLUDED.model_provider,
                        instructions = EXCLUDED.instructions,
                        description = EXCLUDED.description,
                        system_prompt = EXCLUDED.system_prompt,
                        tool_ids = EXCLUDED.tool_ids,
                        memory_config = EXCLUDED.memory_config,
                        knowledge_config = EXCLUDED.knowledge_config,
                        session_config = EXCLUDED.session_config,
                        additional_config = EXCLUDED.additional_config,
                        is_active = EXCLUDED.is_active
                """, agent_config)
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving agent config: {e}")
            self.connection.rollback()
            return False
    
    def load_team_config(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a team configuration from the database.
        
        Args:
            team_id: Unique identifier for the team
            
        Returns:
            Dictionary containing team configuration or None if not found
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM teams WHERE team_id = %s AND is_active = true",
                    (team_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error loading team config for {team_id}: {e}")
            return None
    
    def save_team_config(self, team_config: Dict[str, Any]) -> bool:
        """
        Save a team configuration to the database.
        
        Args:
            team_config: Dictionary containing team configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                # Use UPSERT to insert or update
                cursor.execute("""
                    INSERT INTO teams (
                        team_id, name, description, instructions, agent_ids, 
                        orchestration_pattern, team_config, is_active
                    ) VALUES (
                        %(team_id)s, %(name)s, %(description)s, %(instructions)s, 
                        %(agent_ids)s, %(orchestration_pattern)s, %(team_config)s, %(is_active)s
                    )
                    ON CONFLICT (team_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        instructions = EXCLUDED.instructions,
                        agent_ids = EXCLUDED.agent_ids,
                        orchestration_pattern = EXCLUDED.orchestration_pattern,
                        team_config = EXCLUDED.team_config,
                        is_active = EXCLUDED.is_active
                """, team_config)
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving team config: {e}")
            self.connection.rollback()
            return False
    
    def load_tool_config(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a tool configuration from the database.
        
        Args:
            tool_id: Unique identifier for the tool
            
        Returns:
            Dictionary containing tool configuration or None if not found
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tools WHERE tool_id = %s AND is_active = true",
                    (tool_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Error loading tool config for {tool_id}: {e}")
            return None
    
    def save_tool_config(self, tool_config: Dict[str, Any]) -> bool:
        """
        Save a tool configuration to the database.
        
        Args:
            tool_config: Dictionary containing tool configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.connection.cursor() as cursor:
                # Use UPSERT to insert or update
                cursor.execute("""
                    INSERT INTO tools (
                        tool_id, name, description, tool_type, tool_class, tool_config, is_active
                    ) VALUES (
                        %(tool_id)s, %(name)s, %(description)s, %(tool_type)s, 
                        %(tool_class)s, %(tool_config)s, %(is_active)s
                    )
                    ON CONFLICT (tool_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        tool_type = EXCLUDED.tool_type,
                        tool_class = EXCLUDED.tool_class,
                        tool_config = EXCLUDED.tool_config,
                        is_active = EXCLUDED.is_active
                """, tool_config)
                
                self.connection.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving tool config: {e}")
            self.connection.rollback()
            return False
    
    def list_agents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all agent configurations.
        
        Args:
            active_only: If True, only return active agents
            
        Returns:
            List of agent configuration dictionaries
        """
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM agents"
                if active_only:
                    query += " WHERE is_active = true"
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return []
    
    def list_teams(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        List all team configurations.
        
        Args:
            active_only: If True, only return active teams
            
        Returns:
            List of team configuration dictionaries
        """
        try:
            with self.connection.cursor() as cursor:
                query = "SELECT * FROM teams"
                if active_only:
                    query += " WHERE is_active = true"
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error listing teams: {e}")
            return []
    
    def create_agent_from_config(
        self, 
        agent_config: Dict[str, Any], 
        db=None, 
        knowledge=None
    ) -> Optional[Agent]:
        """
        Create an Agent instance from a database configuration.
        
        Args:
            agent_config: Agent configuration dictionary from database
            db: Database instance to pass to the agent
            knowledge: Knowledge instance to pass to the agent
            
        Returns:
            Agent instance or None if creation fails
        """
        try:
            # Map model configurations
            model_id = agent_config.get('model_id')
            model_provider = agent_config.get('model_provider', 'openai')
            
            # Create model instance based on provider
            if model_provider.lower() == 'openai':
                model = OpenAIChat(id=model_id)
            elif model_provider.lower() == 'google' or model_provider.lower() == 'gemini':
                model = Gemini(id=model_id)
            else:
                # Default to OpenAI if provider not recognized
                model = OpenAIChat(id=model_id)
            
            # Create agent with configuration
            agent = Agent(
                id=agent_config['agent_id'],
                name=agent_config.get('name'),
                model=model,
                instructions=agent_config.get('instructions'),
                description=agent_config.get('description'),
                db=db,
                knowledge=knowledge,
                # Add other configurations as needed
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent from config: {e}")
            return None
    
    def create_team_from_config(
        self, 
        team_config: Dict[str, Any], 
        agents: List[Agent]
    ) -> Optional[Team]:
        """
        Create a Team instance from a database configuration.
        
        Args:
            team_config: Team configuration dictionary from database
            agents: List of Agent instances that are part of this team
            
        Returns:
            Team instance or None if creation fails
        """
        try:
            team = Team(
                id=team_config['team_id'],
                name=team_config.get('name'),
                members=agents,
                instructions=team_config.get('instructions'),
                description=team_config.get('description'),
                # Add other configurations as needed
            )
            
            return team
            
        except Exception as e:
            logger.error(f"Error creating team from config: {e}")
            return None