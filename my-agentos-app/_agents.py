from agno.agent import Agent

# Instantiate agents with their configurations
sage = Agent(
    model="sage-model",
    tools=["tool1", "tool2"],
    instructions="Provide insightful responses based on the input.",
)

agno_assist = Agent(
    model="agno-assist-model",
    tools=["tool3", "tool4"],
    instructions="Assist users with their queries and tasks.",
)

# Export the agents for use in other modules
__all__ = ["sage", "agno_assist"]