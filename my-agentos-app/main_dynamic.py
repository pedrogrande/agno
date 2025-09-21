"""
Updated main application with database-driven agent and team loading.

This application demonstrates the new database-driven configuration system
while maintaining backward compatibility with the existing setup.
"""
import logging
import os
from typing import List

from agno.os import AgentOS
from agno.agent import Agent
from agno.team import Team

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the dynamic modules first, fall back to original if they fail
try:
    from _agents_dynamic import agents_list, gemini_agent, agno_expert_consultant_agent, dynamic_loader
    from _teams_dynamic import teams_list, rag_team
    USING_DYNAMIC_CONFIG = True
    logger.info("✅ Using database-driven agent and team configuration")
except ImportError as e:
    logger.warning(f"Could not import dynamic modules: {e}")
    logger.info("🔄 Falling back to original hard-coded configuration")
    
    # Fall back to original imports
    from _agents import gemini_agent, agno_expert_consultant_agent
    from _teams import rag_team
    
    agents_list = [gemini_agent, agno_expert_consultant_agent]
    teams_list = [rag_team]
    USING_DYNAMIC_CONFIG = False
    dynamic_loader = None

def create_agent_os() -> AgentOS:
    """
    Create and configure the AgentOS instance.
    
    Returns:
        Configured AgentOS instance
    """
    logger.info("Creating AgentOS instance...")
    
    # Filter out None values in case some agents/teams failed to load
    valid_agents = [agent for agent in agents_list if agent is not None]
    valid_teams = [team for team in teams_list if team is not None]
    
    logger.info(f"Configuring AgentOS with {len(valid_agents)} agents and {len(valid_teams)} teams")
    for agent in valid_agents:
        logger.info(f"  - Agent: {agent.id} ({agent.name if hasattr(agent, 'name') else 'Unnamed'})")
    for team in valid_teams:
        logger.info(f"  - Team: {team.id} ({team.name if hasattr(team, 'name') else 'Unnamed'})")
    
    # Create the AgentOS
    agent_os = AgentOS(
        os_id="my-agentos-app",
        agents=valid_agents,
        teams=valid_teams,
    )
    
    logger.info("✅ AgentOS instance created successfully")
    return agent_os

def add_dynamic_management_endpoints(app):
    """
    Add endpoints for dynamic agent and team management (if using dynamic config).
    
    Args:
        app: FastAPI application instance
    """
    if not USING_DYNAMIC_CONFIG or not dynamic_loader:
        logger.info("Dynamic configuration not available, skipping management endpoints")
        return
    
    try:
        from fastapi import HTTPException
        from pydantic import BaseModel
        from typing import Dict, Any
        
        class ReloadResponse(BaseModel):
            success: bool
            message: str
            agents_count: int
            teams_count: int
        
        @app.get("/admin/reload", response_model=ReloadResponse)
        async def reload_configuration():
            """Reload agent and team configurations from database."""
            try:
                # Import reload functions
                from _agents_dynamic import reload_agents
                from _teams_dynamic import reload_teams
                
                # Reload configurations
                reload_agents()
                reload_teams()
                
                # Get updated counts
                agents_count = len([a for a in agents_list if a is not None])
                teams_count = len([t for t in teams_list if t is not None])
                
                return ReloadResponse(
                    success=True,
                    message="Configuration reloaded successfully",
                    agents_count=agents_count,
                    teams_count=teams_count
                )
            except Exception as e:
                logger.error(f"Error reloading configuration: {e}")
                return ReloadResponse(
                    success=False,
                    message=f"Error reloading configuration: {str(e)}",
                    agents_count=0,
                    teams_count=0
                )
        
        @app.get("/admin/status")
        async def get_configuration_status():
            """Get current configuration status."""
            return {
                "using_dynamic_config": USING_DYNAMIC_CONFIG,
                "agents_count": len([a for a in agents_list if a is not None]),
                "teams_count": len([t for t in teams_list if t is not None]),
                "agent_ids": [a.id for a in agents_list if a is not None],
                "team_ids": [t.id for t in teams_list if t is not None],
            }
        
        logger.info("✅ Added dynamic management endpoints: /admin/reload, /admin/status")
        
    except ImportError:
        logger.warning("FastAPI not available, skipping dynamic management endpoints")
    except Exception as e:
        logger.error(f"Error adding dynamic management endpoints: {e}")

# Create the AgentOS
agent_os = create_agent_os()
app = agent_os.get_app()

# Add dynamic management endpoints
add_dynamic_management_endpoints(app)

if __name__ == "__main__":
    # Add some startup information
    print("\n" + "="*50)
    print("🚀 Starting Agno AgentOS Application")
    print("="*50)
    print(f"Configuration Mode: {'Database-Driven' if USING_DYNAMIC_CONFIG else 'Hard-Coded'}")
    print(f"Agents: {len([a for a in agents_list if a is not None])}")
    print(f"Teams: {len([t for t in teams_list if t is not None])}")
    
    if USING_DYNAMIC_CONFIG:
        print("\n💡 Management Endpoints Available:")
        print("   - GET /admin/status - View current configuration")
        print("   - GET /admin/reload - Reload from database")
        
        print("\n📊 To populate the database with initial data, run:")
        print("   python seed_database.py")
    
    print("\n🌐 Starting server...")
    print("="*50 + "\n")
    
    agent_os.serve(app="main_dynamic:app", reload=True)