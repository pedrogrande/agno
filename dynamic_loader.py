"""
Dynamic Agent and Team Loader

This module provides functionality to dynamically load agents and teams from
the database using the MCP connector, replacing hard-coded definitions.
"""
import logging
from typing import Dict, List, Optional

from agno.agent import Agent
from agno.team import Team
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from agno.knowledge.embedder.openai import OpenAIEmbedder

from mcp_connector import PostgresMCPConnector

logger = logging.getLogger(__name__)


class DynamicAgentLoader:
    """
    Loads agents and teams dynamically from database configurations.
    """
    
    def __init__(
        self, 
        db_url: str,
        db_instance: Optional[PostgresDb] = None,
        knowledge_instance: Optional[Knowledge] = None
    ):
        """
        Initialize the dynamic loader.
        
        Args:
            db_url: Database connection URL
            db_instance: Shared database instance for agents
            knowledge_instance: Shared knowledge instance for agents
        """
        self.db_url = db_url
        self.connector = PostgresMCPConnector(db_url=db_url)
        self.db_instance = db_instance
        self.knowledge_instance = knowledge_instance
        
        # Cache for loaded agents to avoid recreating them
        self._agent_cache: Dict[str, Agent] = {}
        self._team_cache: Dict[str, Team] = {}
    
    def get_or_create_db_instance(self) -> PostgresDb:
        """Get or create the shared database instance."""
        if self.db_instance is None:
            self.db_instance = PostgresDb(db_url=self.db_url)
        return self.db_instance
    
    def get_or_create_knowledge_instance(self) -> Knowledge:
        """Get or create the shared knowledge instance."""
        if self.knowledge_instance is None:
            # Create knowledge instance with default configuration
            db = self.get_or_create_db_instance()
            vector_db = PgVector(
                table_name="gemini_agent_vectors",
                db_url=self.db_url,
                embedder=OpenAIEmbedder(id="text-embedding-3-small")
            )
            
            self.knowledge_instance = Knowledge(
                contents_db=db,
                vector_db=vector_db,
            )
        return self.knowledge_instance
    
    def load_agent(self, agent_id: str, force_reload: bool = False) -> Optional[Agent]:
        """
        Load an agent from the database configuration.
        
        Args:
            agent_id: Unique identifier for the agent
            force_reload: If True, reload even if cached
            
        Returns:
            Agent instance or None if not found
        """
        # Check cache first
        if not force_reload and agent_id in self._agent_cache:
            logger.debug(f"Returning cached agent: {agent_id}")
            return self._agent_cache[agent_id]
        
        # Load configuration from database
        config = self.connector.load_agent_config(agent_id)
        if not config:
            logger.warning(f"Agent configuration not found: {agent_id}")
            return None
        
        # Create agent instance
        db = self.get_or_create_db_instance()
        knowledge = self.get_or_create_knowledge_instance()
        
        agent = self.connector.create_agent_from_config(
            agent_config=config,
            db=db,
            knowledge=knowledge
        )
        
        if agent:
            # Cache the agent
            self._agent_cache[agent_id] = agent
            logger.info(f"Successfully loaded agent: {agent_id}")
        else:
            logger.error(f"Failed to create agent: {agent_id}")
        
        return agent
    
    def load_team(self, team_id: str, force_reload: bool = False) -> Optional[Team]:
        """
        Load a team from the database configuration.
        
        Args:
            team_id: Unique identifier for the team
            force_reload: If True, reload even if cached
            
        Returns:
            Team instance or None if not found
        """
        # Check cache first
        if not force_reload and team_id in self._team_cache:
            logger.debug(f"Returning cached team: {team_id}")
            return self._team_cache[team_id]
        
        # Load team configuration from database
        team_config = self.connector.load_team_config(team_id)
        if not team_config:
            logger.warning(f"Team configuration not found: {team_id}")
            return None
        
        # Load team members (agents)
        agent_ids = team_config.get('agent_ids', [])
        if isinstance(agent_ids, str):
            import json
            agent_ids = json.loads(agent_ids)
        
        agents = []
        for agent_id in agent_ids:
            agent = self.load_agent(agent_id)
            if agent:
                agents.append(agent)
            else:
                logger.warning(f"Failed to load agent {agent_id} for team {team_id}")
        
        if not agents:
            logger.warning(f"No agents available for team {team_id}")
            return None
        
        # Create team instance
        team = self.connector.create_team_from_config(
            team_config=team_config,
            agents=agents
        )
        
        if team:
            # Cache the team
            self._team_cache[team_id] = team
            logger.info(f"Successfully loaded team: {team_id}")
        else:
            logger.error(f"Failed to create team: {team_id}")
        
        return team
    
    def load_all_agents(self) -> List[Agent]:
        """
        Load all active agents from the database.
        
        Returns:
            List of Agent instances
        """
        agent_configs = self.connector.list_agents(active_only=True)
        agents = []
        
        for config in agent_configs:
            agent = self.load_agent(config['agent_id'])
            if agent:
                agents.append(agent)
        
        logger.info(f"Loaded {len(agents)} agents from database")
        return agents
    
    def load_all_teams(self) -> List[Team]:
        """
        Load all active teams from the database.
        
        Returns:
            List of Team instances
        """
        team_configs = self.connector.list_teams(active_only=True)
        teams = []
        
        for config in team_configs:
            team = self.load_team(config['team_id'])
            if team:
                teams.append(team)
        
        logger.info(f"Loaded {len(teams)} teams from database")
        return teams
    
    def reload_cache(self):
        """Clear and reload the agent and team caches."""
        self._agent_cache.clear()
        self._team_cache.clear()
        logger.info("Agent and team caches cleared")
    
    def close(self):
        """Close the connector."""
        self.connector.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Convenience functions for backward compatibility
def get_agent(agent_id: str, db_url: str) -> Optional[Agent]:
    """
    Convenience function to load a single agent.
    
    Args:
        agent_id: Agent identifier
        db_url: Database connection URL
        
    Returns:
        Agent instance or None
    """
    with DynamicAgentLoader(db_url=db_url) as loader:
        return loader.load_agent(agent_id)


def get_team(team_id: str, db_url: str) -> Optional[Team]:
    """
    Convenience function to load a single team.
    
    Args:
        team_id: Team identifier
        db_url: Database connection URL
        
    Returns:
        Team instance or None
    """
    with DynamicAgentLoader(db_url=db_url) as loader:
        return loader.load_team(team_id)


def get_all_agents(db_url: str) -> List[Agent]:
    """
    Convenience function to load all agents.
    
    Args:
        db_url: Database connection URL
        
    Returns:
        List of Agent instances
    """
    with DynamicAgentLoader(db_url=db_url) as loader:
        return loader.load_all_agents()


def get_all_teams(db_url: str) -> List[Team]:
    """
    Convenience function to load all teams.
    
    Args:
        db_url: Database connection URL
        
    Returns:
        List of Team instances
    """
    with DynamicAgentLoader(db_url=db_url) as loader:
        return loader.load_all_teams()