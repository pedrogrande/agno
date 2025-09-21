from agno.agent import Agent
from agno.team import Team

# Define your agents here
agent_one = Agent(
    model="your_model_1",
    tools=["tool_1", "tool_2"],
    instructions="Instructions for agent one."
)

agent_two = Agent(
    model="your_model_2",
    tools=["tool_3", "tool_4"],
    instructions="Instructions for agent two."
)

# Define your teams here
finance_team = Team(
    name="Finance Team",
    agents=[agent_one, agent_two],
    instructions="Team instructions for finance-related tasks."
)