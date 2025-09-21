"""
Database Seeding Script for Agent and Team Configurations

This script populates the database with initial agent and team configurations
based on the existing hard-coded definitions in the application.
"""
import json
import logging
from mcp_connector import PostgresMCPConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_URL = "postgresql+psycopg://ai:ai@localhost:5532/ai"

def seed_database():
    """Seed the database with initial agent and team configurations."""
    
    with PostgresMCPConnector(db_url=DB_URL) as connector:
        logger.info("Starting database seeding...")
        
        # Seed agents based on existing configurations
        agents_to_seed = [
            {
                'agent_id': 'gemini-agent',
                'name': 'Gemini Agent',
                'model_id': 'gemini-2.5-flash',
                'model_provider': 'google',
                'instructions': 'You are a helpful assistant powered by Google Gemini. Answer questions based on the provided knowledge.',
                'description': 'A helpful assistant powered by Google Gemini',
                'system_prompt': None,
                'tool_ids': json.dumps([]),  # No specific tools defined
                'memory_config': json.dumps({
                    'enable_session_summaries': True,
                    'enable_user_memories': True,
                    'add_history_to_context': True,
                    'num_history_runs': 3
                }),
                'knowledge_config': json.dumps({
                    'knowledge_enabled': True,
                    'vector_db_table': 'gemini_agent_vectors'
                }),
                'session_config': json.dumps({
                    'db_enabled': True
                }),
                'additional_config': json.dumps({}),
                'is_active': True
            },
            {
                'agent_id': 'agno-expert-consultant',
                'name': 'Agno Expert Consultant Agent',
                'model_id': 'gemini-2.5-flash',
                'model_provider': 'google',
                'instructions': json.dumps([
                    "You are operating as an expert AI development consultant specialising in the Agno agentic framework.",
                    "Analyse user requirements for AI applications and provide comprehensive guidance on implementing solutions using the Agno framework.",
                    "Break down complex requirements into small, logically ordered tasks that can be systematically executed.",
                    "Provide specific recommendations on framework features, tool integrations, MCP integrations, and implementation approaches that best suit the user's needs while ensuring security, user-friendliness, and developer-friendliness.",
                    "You have comprehensive expertise in the Agno agentic framework."
                ]),
                'description': 'Expert AI development consultant specializing in the Agno agentic framework',
                'system_prompt': None,
                'tool_ids': json.dumps([]),
                'memory_config': json.dumps({
                    'enable_session_summaries': True,
                    'enable_user_memories': True,
                    'add_history_to_context': True,
                    'num_history_runs': 3
                }),
                'knowledge_config': json.dumps({
                    'knowledge_enabled': True,
                    'vector_db_table': 'gemini_agent_vectors'
                }),
                'session_config': json.dumps({
                    'db_enabled': True
                }),
                'additional_config': json.dumps({}),
                'is_active': True
            }
        ]
        
        # Save agent configurations
        for agent_config in agents_to_seed:
            success = connector.save_agent_config(agent_config)
            if success:
                logger.info(f"Successfully seeded agent: {agent_config['agent_id']}")
            else:
                logger.error(f"Failed to seed agent: {agent_config['agent_id']}")
        
        # Seed teams based on existing configurations
        teams_to_seed = [
            {
                'team_id': 'rag-team',
                'name': 'RAG Team',
                'description': 'Team that includes the RAG-enabled agent for knowledge-based responses',
                'instructions': 'Answer questions using the knowledge available to the team members.',
                'agent_ids': json.dumps(['gemini-agent']),
                'orchestration_pattern': 'sequential',
                'team_config': json.dumps({
                    'collaboration_type': 'knowledge_sharing'
                }),
                'is_active': True
            }
        ]
        
        # Save team configurations
        for team_config in teams_to_seed:
            success = connector.save_team_config(team_config)
            if success:
                logger.info(f"Successfully seeded team: {team_config['team_id']}")
            else:
                logger.error(f"Failed to seed team: {team_config['team_id']}")
        
        # Seed some basic tool configurations
        tools_to_seed = [
            {
                'tool_id': 'agno-knowledge-tool',
                'name': 'Agno Knowledge Tool',
                'description': 'Tool for accessing Agno framework documentation and knowledge',
                'tool_type': 'builtin',
                'tool_class': 'agno.knowledge.knowledge.Knowledge',
                'tool_config': json.dumps({
                    'contents_db_table': 'knowledge_contents',
                    'vector_db_table': 'knowledge_vectors'
                }),
                'is_active': True
            }
        ]
        
        # Save tool configurations
        for tool_config in tools_to_seed:
            success = connector.save_tool_config(tool_config)
            if success:
                logger.info(f"Successfully seeded tool: {tool_config['tool_id']}")
            else:
                logger.error(f"Failed to seed tool: {tool_config['tool_id']}")
        
        logger.info("Database seeding completed!")

def verify_seeded_data():
    """Verify that the seeded data was inserted correctly."""
    
    with PostgresMCPConnector(db_url=DB_URL) as connector:
        logger.info("Verifying seeded data...")
        
        # List agents
        agents = connector.list_agents()
        logger.info(f"Found {len(agents)} agents:")
        for agent in agents:
            logger.info(f"  - {agent['agent_id']}: {agent['name']}")
        
        # List teams
        teams = connector.list_teams()
        logger.info(f"Found {len(teams)} teams:")
        for team in teams:
            logger.info(f"  - {team['team_id']}: {team['name']}")
        
        # Test loading specific configurations
        gemini_config = connector.load_agent_config('gemini-agent')
        if gemini_config:
            logger.info(f"Successfully loaded gemini-agent config: {gemini_config['name']}")
        else:
            logger.error("Failed to load gemini-agent config")
        
        rag_team_config = connector.load_team_config('rag-team')
        if rag_team_config:
            logger.info(f"Successfully loaded rag-team config: {rag_team_config['name']}")
            logger.info(f"Team agent IDs: {rag_team_config['agent_ids']}")
        else:
            logger.error("Failed to load rag-team config")

if __name__ == "__main__":
    try:
        seed_database()
        verify_seeded_data()
        logger.info("✅ Seeding process completed successfully!")
    except Exception as e:
        logger.error(f"❌ Error during seeding: {e}")
        raise