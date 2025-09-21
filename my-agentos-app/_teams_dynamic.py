"""
Updated teams module with database-driven configuration support.

This module provides both backward compatibility for existing hard-coded teams
and new functionality for dynamically loading teams from the database.
"""
import logging
from typing import List, Optional

from agno.team import Team
from dynamic_loader import DynamicAgentLoader
from _agents_dynamic import agents_list, dynamic_loader, gemini_agent

logger = logging.getLogger(__name__)

def get_database_teams() -> List[Team]:
    """
    Load teams from database configuration.
    
    Returns:
        List of teams loaded from database
    """
    try:
        teams = dynamic_loader.load_all_teams()
        if teams:
            logger.info(f"Successfully loaded {len(teams)} teams from database")
            return teams
        else:
            logger.warning("No teams found in database, falling back to hard-coded")
            return []
    except Exception as e:
        logger.error(f"Error loading teams from database: {e}")
        return []

def get_fallback_teams() -> List[Team]:
    """
    Create hard-coded teams as fallback when database is not available.
    
    Returns:
        List of hard-coded teams
    """
    logger.info("Creating fallback hard-coded teams")
    
    # Create the RAG team with available agents
    if gemini_agent:
        rag_team = Team(
            id="rag-team",
            members=[gemini_agent],
            instructions="Answer questions using the knowledge available to the team members.",
        )
        return [rag_team]
    else:
        logger.error("Cannot create fallback teams: gemini_agent not available")
        return []

# Try to load from database, fall back to hard-coded
database_teams = get_database_teams()
if database_teams:
    # Use database teams
    teams_list = database_teams
    logger.info("Using database-driven team configuration")
else:
    # Use hard-coded teams
    teams_list = get_fallback_teams()
    logger.info("Using hard-coded fallback team configuration")

# Extract individual teams for backward compatibility
rag_team = None

for team in teams_list:
    if team.id == "rag-team":
        rag_team = team

# Ensure we have at least the essential team
if rag_team is None and gemini_agent:
    logger.warning("rag-team not found, creating fallback")
    rag_team = Team(
        id="rag-team",
        members=[gemini_agent],
        instructions="Answer questions using the knowledge available to the team members.",
    )
    teams_list.append(rag_team)

# Utility functions for dynamic loading
def load_team_by_id(team_id: str) -> Optional[Team]:
    """
    Load a specific team by ID from the database.
    
    Args:
        team_id: The team identifier
        
    Returns:
        Team instance or None if not found
    """
    return dynamic_loader.load_team(team_id)

def reload_teams():
    """
    Reload all teams from the database (clears cache).
    """
    dynamic_loader.reload_cache()
    global teams_list, rag_team
    
    # Reload from database
    new_teams = get_database_teams()
    if new_teams:
        teams_list = new_teams
        # Update individual team references
        rag_team = None
        
        for team in teams_list:
            if team.id == "rag-team":
                rag_team = team
        
        logger.info("Teams reloaded from database")
    else:
        logger.warning("Failed to reload teams from database")

def create_team_from_agent_ids(team_id: str, agent_ids: List[str]) -> Optional[Team]:
    """
    Create a team dynamically from a list of agent IDs.
    
    Args:
        team_id: Team identifier
        agent_ids: List of agent IDs to include in the team
        
    Returns:
        Team instance or None if creation fails
    """
    try:
        # Load the specified agents
        agents = []
        for agent_id in agent_ids:
            agent = dynamic_loader.load_agent(agent_id)
            if agent:
                agents.append(agent)
            else:
                logger.warning(f"Could not load agent {agent_id} for team {team_id}")
        
        if not agents:
            logger.error(f"No agents available for team {team_id}")
            return None
        
        # Create the team
        team = Team(
            id=team_id,
            members=agents,
            instructions=f"Collaborate as team {team_id} to complete tasks.",
        )
        
        logger.info(f"Created dynamic team {team_id} with {len(agents)} agents")
        return team
        
    except Exception as e:
        logger.error(f"Error creating team {team_id}: {e}")
        return None

# Export teams for use in other modules
__all__ = [
    "rag_team",
    "teams_list", 
    "load_team_by_id",
    "reload_teams",
    "create_team_from_agent_ids",
    "dynamic_loader"
]