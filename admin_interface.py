"""
Admin Interface for Database-Driven Agent and Team Configuration

This Streamlit application provides a user-friendly interface for managing
agent and team configurations stored in the database.
"""
import streamlit as st
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from mcp_connector import PostgresMCPConnector
    from dynamic_loader import DynamicAgentLoader
except ImportError as e:
    st.error(f"Could not import required modules: {e}")
    st.stop()

# Database configuration
DB_URL = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Streamlit page configuration
st.set_page_config(
    page_title="Agno Agent Admin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'connector' not in st.session_state:
    st.session_state.connector = PostgresMCPConnector(db_url=DB_URL)
if 'dynamic_loader' not in st.session_state:
    st.session_state.dynamic_loader = DynamicAgentLoader(db_url=DB_URL)

def format_timestamp(timestamp: Optional[int]) -> str:
    """Format a timestamp for display."""
    if timestamp is None:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(timestamp / 1000)  # Convert from milliseconds
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def display_agent_form(agent_config: Optional[Dict[str, Any]] = None):
    """Display form for creating/editing an agent."""
    st.subheader("Agent Configuration")
    
    # Initialize with existing values or defaults
    defaults = agent_config or {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        agent_id = st.text_input(
            "Agent ID*", 
            value=defaults.get('agent_id', ''),
            help="Unique identifier for the agent"
        )
        name = st.text_input(
            "Name*", 
            value=defaults.get('name', ''),
            help="Human-readable name for the agent"
        )
        model_id = st.text_input(
            "Model ID*", 
            value=defaults.get('model_id', 'gemini-2.5-flash'),
            help="Model identifier (e.g., gemini-2.5-flash, gpt-4)"
        )
        model_provider = st.selectbox(
            "Model Provider", 
            options=['google', 'openai', 'anthropic'],
            index=['google', 'openai', 'anthropic'].index(defaults.get('model_provider', 'google'))
        )
    
    with col2:
        description = st.text_area(
            "Description", 
            value=defaults.get('description', ''),
            help="Brief description of the agent's purpose"
        )
        system_prompt = st.text_area(
            "System Prompt", 
            value=defaults.get('system_prompt', ''),
            help="Optional system prompt (overrides instructions)"
        )
        is_active = st.checkbox(
            "Active", 
            value=defaults.get('is_active', True),
            help="Whether the agent is active and available for use"
        )
    
    # Instructions (can be string or list)
    instructions_value = defaults.get('instructions', '')
    if isinstance(instructions_value, list):
        instructions_value = '\n'.join(instructions_value)
    elif isinstance(instructions_value, str) and instructions_value.startswith('['):
        try:
            parsed = json.loads(instructions_value)
            if isinstance(parsed, list):
                instructions_value = '\n'.join(parsed)
        except:
            pass
    
    instructions = st.text_area(
        "Instructions*", 
        value=instructions_value,
        height=150,
        help="Agent instructions (one per line for multiple instructions)"
    )
    
    # Advanced configuration in expandable section
    with st.expander("Advanced Configuration"):
        col3, col4 = st.columns(2)
        
        with col3:
            # Tool IDs
            tool_ids_value = defaults.get('tool_ids', [])
            if isinstance(tool_ids_value, str):
                try:
                    tool_ids_value = json.loads(tool_ids_value)
                except:
                    tool_ids_value = []
            
            tool_ids_text = st.text_area(
                "Tool IDs (JSON array)", 
                value=json.dumps(tool_ids_value, indent=2),
                help="JSON array of tool identifiers"
            )
            
            # Memory configuration
            memory_config_value = defaults.get('memory_config', {})
            if isinstance(memory_config_value, str):
                try:
                    memory_config_value = json.loads(memory_config_value)
                except:
                    memory_config_value = {}
            
            memory_config_text = st.text_area(
                "Memory Configuration (JSON)", 
                value=json.dumps(memory_config_value, indent=2),
                help="JSON object for memory settings"
            )
        
        with col4:
            # Knowledge configuration
            knowledge_config_value = defaults.get('knowledge_config', {})
            if isinstance(knowledge_config_value, str):
                try:
                    knowledge_config_value = json.loads(knowledge_config_value)
                except:
                    knowledge_config_value = {}
            
            knowledge_config_text = st.text_area(
                "Knowledge Configuration (JSON)", 
                value=json.dumps(knowledge_config_value, indent=2),
                help="JSON object for knowledge settings"
            )
            
            # Additional configuration
            additional_config_value = defaults.get('additional_config', {})
            if isinstance(additional_config_value, str):
                try:
                    additional_config_value = json.loads(additional_config_value)
                except:
                    additional_config_value = {}
            
            additional_config_text = st.text_area(
                "Additional Configuration (JSON)", 
                value=json.dumps(additional_config_value, indent=2),
                help="JSON object for additional settings"
            )
    
    # Form submission
    if st.button("Save Agent", type="primary"):
        if not agent_id or not name or not model_id or not instructions:
            st.error("Please fill in all required fields (marked with *)")
            return False
        
        try:
            # Parse JSON fields
            tool_ids = json.loads(tool_ids_text)
            memory_config = json.loads(memory_config_text)
            knowledge_config = json.loads(knowledge_config_text)
            additional_config = json.loads(additional_config_text)
            
            # Prepare instructions (convert to list if multi-line)
            instructions_list = [line.strip() for line in instructions.split('\n') if line.strip()]
            if len(instructions_list) == 1:
                instructions_final = instructions_list[0]
            else:
                instructions_final = instructions_list
            
            # Create agent configuration
            agent_config = {
                'agent_id': agent_id,
                'name': name,
                'model_id': model_id,
                'model_provider': model_provider,
                'instructions': instructions_final,
                'description': description,
                'system_prompt': system_prompt if system_prompt else None,
                'tool_ids': tool_ids,
                'memory_config': memory_config,
                'knowledge_config': knowledge_config,
                'additional_config': additional_config,
                'is_active': is_active
            }
            
            # Save to database
            success = st.session_state.connector.save_agent_config(agent_config)
            
            if success:
                st.success(f"Agent '{agent_id}' saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save agent configuration")
                
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in configuration fields: {e}")
        except Exception as e:
            st.error(f"Error saving agent: {e}")
        
        return success
    
    return False

def display_team_form(team_config: Optional[Dict[str, Any]] = None):
    """Display form for creating/editing a team."""
    st.subheader("Team Configuration")
    
    # Initialize with existing values or defaults
    defaults = team_config or {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        team_id = st.text_input(
            "Team ID*", 
            value=defaults.get('team_id', ''),
            help="Unique identifier for the team"
        )
        name = st.text_input(
            "Name*", 
            value=defaults.get('name', ''),
            help="Human-readable name for the team"
        )
        orchestration_pattern = st.selectbox(
            "Orchestration Pattern",
            options=['sequential', 'hierarchical', 'collaborative'],
            index=['sequential', 'hierarchical', 'collaborative'].index(
                defaults.get('orchestration_pattern', 'sequential')
            )
        )
    
    with col2:
        description = st.text_area(
            "Description", 
            value=defaults.get('description', ''),
            help="Brief description of the team's purpose"
        )
        is_active = st.checkbox(
            "Active", 
            value=defaults.get('is_active', True),
            help="Whether the team is active and available for use"
        )
    
    instructions = st.text_area(
        "Instructions*", 
        value=defaults.get('instructions', ''),
        help="Team instructions and objectives"
    )
    
    # Agent selection
    st.subheader("Team Members")
    
    # Get available agents
    available_agents = st.session_state.connector.list_agents(active_only=True)
    agent_options = {agent['agent_id']: f"{agent['name']} ({agent['agent_id']})" for agent in available_agents}
    
    # Current agent IDs
    current_agent_ids = defaults.get('agent_ids', [])
    if isinstance(current_agent_ids, str):
        try:
            current_agent_ids = json.loads(current_agent_ids)
        except:
            current_agent_ids = []
    
    selected_agents = st.multiselect(
        "Select Team Members*",
        options=list(agent_options.keys()),
        default=current_agent_ids,
        format_func=lambda x: agent_options.get(x, x),
        help="Select agents to include in this team"
    )
    
    # Advanced configuration
    with st.expander("Advanced Configuration"):
        team_config_value = defaults.get('team_config', {})
        if isinstance(team_config_value, str):
            try:
                team_config_value = json.loads(team_config_value)
            except:
                team_config_value = {}
        
        team_config_text = st.text_area(
            "Team Configuration (JSON)", 
            value=json.dumps(team_config_value, indent=2),
            help="JSON object for team-specific settings"
        )
    
    # Form submission
    if st.button("Save Team", type="primary"):
        if not team_id or not name or not instructions or not selected_agents:
            st.error("Please fill in all required fields (marked with *)")
            return False
        
        try:
            # Parse JSON fields
            team_config_obj = json.loads(team_config_text)
            
            # Create team configuration
            team_config = {
                'team_id': team_id,
                'name': name,
                'description': description,
                'instructions': instructions,
                'agent_ids': selected_agents,
                'orchestration_pattern': orchestration_pattern,
                'team_config': team_config_obj,
                'is_active': is_active
            }
            
            # Save to database
            success = st.session_state.connector.save_team_config(team_config)
            
            if success:
                st.success(f"Team '{team_id}' saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save team configuration")
                
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON in configuration fields: {e}")
        except Exception as e:
            st.error(f"Error saving team: {e}")
        
        return success
    
    return False

def main():
    """Main application."""
    st.title("🤖 Agno Agent Administration")
    st.markdown("Manage your database-driven agent and team configurations")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Dashboard", "Agents", "Teams", "Create Agent", "Create Team"]
    )
    
    if page == "Dashboard":
        st.header("📊 Dashboard")
        
        # Stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agents = st.session_state.connector.list_agents(active_only=True)
            st.metric("Active Agents", len(agents))
        
        with col2:
            teams = st.session_state.connector.list_teams(active_only=True)
            st.metric("Active Teams", len(teams))
        
        with col3:
            all_agents = st.session_state.connector.list_agents(active_only=False)
            inactive_count = len([a for a in all_agents if not a.get('is_active', True)])
            st.metric("Inactive Agents", inactive_count)
        
        # Recent activity
        st.subheader("Recent Agents")
        if agents:
            for agent in agents[:5]:  # Show first 5
                with st.expander(f"🤖 {agent['name']} ({agent['agent_id']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Model:** {agent.get('model_provider', 'unknown')}/{agent.get('model_id', 'unknown')}")
                        st.write(f"**Created:** {format_timestamp(agent.get('created_at'))}")
                    with col2:
                        st.write(f"**Active:** {'✅' if agent.get('is_active') else '❌'}")
                        st.write(f"**Updated:** {format_timestamp(agent.get('updated_at'))}")
                    if agent.get('description'):
                        st.write(f"**Description:** {agent['description']}")
    
    elif page == "Agents":
        st.header("🤖 Agent Management")
        
        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            show_inactive = st.checkbox("Show Inactive Agents")
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Load agents
        agents = st.session_state.connector.list_agents(active_only=not show_inactive)
        
        if not agents:
            st.info("No agents found. Create your first agent using the 'Create Agent' page.")
        else:
            for agent in agents:
                with st.expander(f"🤖 {agent['name']} ({'Active' if agent.get('is_active') else 'Inactive'})"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**ID:** {agent['agent_id']}")
                        st.write(f"**Model:** {agent.get('model_provider', 'unknown')}/{agent.get('model_id', 'unknown')}")
                        if agent.get('description'):
                            st.write(f"**Description:** {agent['description']}")
                    
                    with col2:
                        st.write(f"**Created:** {format_timestamp(agent.get('created_at'))}")
                        st.write(f"**Updated:** {format_timestamp(agent.get('updated_at'))}")
                        st.write(f"**Active:** {'✅' if agent.get('is_active') else '❌'}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_agent_{agent['agent_id']}"):
                            st.session_state.edit_agent = agent
                            st.session_state.page = "Create Agent"
                            st.rerun()
        
        # Handle edit mode
        if hasattr(st.session_state, 'edit_agent'):
            st.subheader("Edit Agent")
            display_agent_form(st.session_state.edit_agent)
            if st.button("Cancel Edit"):
                del st.session_state.edit_agent
                st.rerun()
    
    elif page == "Teams":
        st.header("👥 Team Management")
        
        # Filter controls
        col1, col2 = st.columns(2)
        with col1:
            show_inactive = st.checkbox("Show Inactive Teams")
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        
        # Load teams
        teams = st.session_state.connector.list_teams(active_only=not show_inactive)
        
        if not teams:
            st.info("No teams found. Create your first team using the 'Create Team' page.")
        else:
            for team in teams:
                with st.expander(f"👥 {team['name']} ({'Active' if team.get('is_active') else 'Inactive'})"):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**ID:** {team['team_id']}")
                        st.write(f"**Pattern:** {team.get('orchestration_pattern', 'sequential')}")
                        if team.get('description'):
                            st.write(f"**Description:** {team['description']}")
                    
                    with col2:
                        st.write(f"**Created:** {format_timestamp(team.get('created_at'))}")
                        st.write(f"**Updated:** {format_timestamp(team.get('updated_at'))}")
                        
                        # Show agent members
                        agent_ids = team.get('agent_ids', [])
                        if isinstance(agent_ids, str):
                            try:
                                agent_ids = json.loads(agent_ids)
                            except:
                                agent_ids = []
                        st.write(f"**Members:** {', '.join(agent_ids) if agent_ids else 'None'}")
                    
                    with col3:
                        if st.button(f"Edit", key=f"edit_team_{team['team_id']}"):
                            st.session_state.edit_team = team
                            st.session_state.page = "Create Team"
                            st.rerun()
        
        # Handle edit mode
        if hasattr(st.session_state, 'edit_team'):
            st.subheader("Edit Team")
            display_team_form(st.session_state.edit_team)
            if st.button("Cancel Edit"):
                del st.session_state.edit_team
                st.rerun()
    
    elif page == "Create Agent":
        st.header("➕ Create New Agent")
        display_agent_form()
    
    elif page == "Create Team":
        st.header("➕ Create New Team")
        display_team_form()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application error: {e}", exc_info=True)