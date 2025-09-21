from agno.os import AgentOS
from _agents import agent_one, agent_two  # Import your defined agents
from _teams import my_agent_team  # Import your defined team

# Create the AgentOS instance
agent_os = AgentOS(
    os_id="my-agentos-app",
    agents=[agent_one, agent_two],  # List your agents here
    teams=[my_agent_team],  # List your teams here
)

# Get the application instance
app = agent_os.get_app()

if __name__ == "__main__":
    # Start the AgentOS application server
    agent_os.serve(app="main:app", reload=True)