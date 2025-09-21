from _agents import agno_expert_consultant_agent, gemini_agent
from _teams import rag_team  # Import your new team
from agno.os import AgentOS

# Create the AgentOS
agent_os = AgentOS(
    os_id="my-agentos-app",
    agents=[gemini_agent, agno_expert_consultant_agent],
    teams=[rag_team],  # Add the rag_team to the list
)
app = agent_os.get_app()

if __name__ == "__main__":
    agent_os.serve(app="main:app", reload=True)
