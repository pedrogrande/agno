from agno.agent import Agent
from agno.team import Team
from _agents import gemini_agent

# # Define your agents here
# agent_one = Agent(
#     model="your_model_1",
#     tools=["tool_1", "tool_2"],
#     instructions="Instructions for agent one."
# )

# agent_two = Agent(
#     model="your_model_2",
#     tools=["tool_3", "tool_4"],
#     instructions="Instructions for agent two."
# )

# # Define your teams here
# finance_team = Team(
#     name="Finance Team",
#     agents=[agent_one, agent_two],
#     instructions="Team instructions for finance-related tasks."
# )

# 1. Define a team that includes the RAG-enabled agent
rag_team = Team(
    id="rag-team",
    members=[gemini_agent],
    instructions="Answer questions using the knowledge available to the team members.",
)

__all__ = ["rag_team"]
