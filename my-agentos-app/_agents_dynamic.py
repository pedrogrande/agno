"""
Updated agents module with database-driven configuration support.

This module provides both backward compatibility for existing hard-coded agents
and new functionality for dynamically loading agents from the database.
"""
import logging
from typing import List, Optional

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.models.google.gemini import Gemini
from agno.vectordb.pgvector import PgVector
from agno.knowledge.embedder.openai import OpenAIEmbedder

from dynamic_loader import DynamicAgentLoader

logger = logging.getLogger(__name__)

# Database configuration
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Initialize shared resources
db = PostgresDb(db_url=db_url)

# Create PgVector for vector embeddings
vector_db = PgVector(
    table_name="gemini_agent_vectors",
    db_url=db_url,
)

# Create a Knowledge instance
agent_knowledge = Knowledge(
    contents_db=db,
    vector_db=vector_db,
)

# Initialize dynamic loader
dynamic_loader = DynamicAgentLoader(
    db_url=db_url,
    db_instance=db,
    knowledge_instance=agent_knowledge
)

# Try to load agents from database first, fall back to hard-coded if needed
def get_database_agents() -> List[Agent]:
    """
    Load agents from database configuration.
    
    Returns:
        List of agents loaded from database
    """
    try:
        agents = dynamic_loader.load_all_agents()
        if agents:
            logger.info(f"Successfully loaded {len(agents)} agents from database")
            return agents
        else:
            logger.warning("No agents found in database, falling back to hard-coded")
            return []
    except Exception as e:
        logger.error(f"Error loading agents from database: {e}")
        return []

def get_fallback_agents() -> List[Agent]:
    """
    Create hard-coded agents as fallback when database is not available.
    
    Returns:
        List of hard-coded agents
    """
    logger.info("Creating fallback hard-coded agents")
    
    # Create Gemini model instance
    gemini_model = Gemini(id="gemini-2.5-flash")
    
    # Create hard-coded agents
    gemini_agent = Agent(
        id="gemini-agent",
        model=gemini_model,
        instructions="You are a helpful assistant powered by Google Gemini. Answer questions based on the provided knowledge.",
        db=db,
        knowledge=agent_knowledge,
    )
    
    agno_expert_consultant_agent = Agent(
        id="agno-expert-consultant",
        model=gemini_model,
        instructions=[
            "You are operating as an expert AI development consultant specialising in the Agno agentic framework.",
            "Analyse user requirements for AI applications and provide comprehensive guidance on implementing solutions using the Agno framework.",
            "Break down complex requirements into small, logically ordered tasks that can be systematically executed.",
            "Provide specific recommendations on framework features, tool integrations, MCP integrations, and implementation approaches that best suit the user's needs while ensuring security, user-friendliness, and developer-friendliness.",
        ],
        db=db,
        knowledge=agent_knowledge,
    )
    
    return [gemini_agent, agno_expert_consultant_agent]

# Try to load from database, fall back to hard-coded
database_agents = get_database_agents()
if database_agents:
    # Use database agents
    agents_list = database_agents
    logger.info("Using database-driven agent configuration")
else:
    # Use hard-coded agents
    agents_list = get_fallback_agents()
    logger.info("Using hard-coded fallback agent configuration")

# Extract individual agents for backward compatibility
gemini_agent = None
agno_expert_consultant_agent = None

for agent in agents_list:
    if agent.id == "gemini-agent":
        gemini_agent = agent
    elif agent.id == "agno-expert-consultant":
        agno_expert_consultant_agent = agent

# Ensure we have at least the essential agents
if gemini_agent is None:
    logger.warning("gemini-agent not found, creating fallback")
    gemini_model = Gemini(id="gemini-2.5-flash")
    gemini_agent = Agent(
        id="gemini-agent",
        model=gemini_model,
        instructions="You are a helpful assistant powered by Google Gemini. Answer questions based on the provided knowledge.",
        db=db,
        knowledge=agent_knowledge,
    )

if agno_expert_consultant_agent is None:
    logger.warning("agno-expert-consultant not found, creating fallback")
    gemini_model = Gemini(id="gemini-2.5-flash")
    agno_expert_consultant_agent = Agent(
        id="agno-expert-consultant",
        model=gemini_model,
        instructions=[
            "You are operating as an expert AI development consultant specialising in the Agno agentic framework.",
        ],
        db=db,
        knowledge=agent_knowledge,
    )

# Add content to the knowledge base (only if not already present)
try:
    print("Adding knowledge to agents...")
    agent_knowledge.add_content(
        name="Agno Docs",
        url="https://docs.agno.com/llms-full.txt",
        skip_if_exists=True,
    )
    print("Knowledge added successfully.")
except Exception as e:
    logger.warning(f"Could not add knowledge content: {e}")

# Utility functions for dynamic loading
def load_agent_by_id(agent_id: str) -> Optional[Agent]:
    """
    Load a specific agent by ID from the database.
    
    Args:
        agent_id: The agent identifier
        
    Returns:
        Agent instance or None if not found
    """
    return dynamic_loader.load_agent(agent_id)

def reload_agents():
    """
    Reload all agents from the database (clears cache).
    """
    dynamic_loader.reload_cache()
    global agents_list, gemini_agent, agno_expert_consultant_agent
    
    # Reload from database
    new_agents = get_database_agents()
    if new_agents:
        agents_list = new_agents
        # Update individual agent references
        gemini_agent = None
        agno_expert_consultant_agent = None
        
        for agent in agents_list:
            if agent.id == "gemini-agent":
                gemini_agent = agent
            elif agent.id == "agno-expert-consultant":
                agno_expert_consultant_agent = agent
        
        logger.info("Agents reloaded from database")
    else:
        logger.warning("Failed to reload agents from database")

# Export the agents for use in other modules
__all__ = [
    "gemini_agent", 
    "agno_expert_consultant_agent", 
    "agents_list",
    "load_agent_by_id",
    "reload_agents",
    "dynamic_loader",
    "db",
    "agent_knowledge"
]