from agno.agent import Agent
from agno.db.postgres import PostgresDb  # Import PostgresDb
from agno.knowledge.knowledge import Knowledge
from agno.models.google.gemini import Gemini
from agno.vectordb.pgvector import PgVector

# 1. Create a database for the agent to store knowledge
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
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

# 2. Create an instance of the Gemini model
gemini_model = Gemini(id="gemini-2.5-flash")

# 3. Create an agent that uses the Gemini model
gemini_agent = Agent(
    id="gemini-agent",
    model=gemini_model,
    instructions="You are a helpful assistant powered by Google Gemini. Answer questions based on the provided knowledge.",
    db=db,
    knowledge=agent_knowledge,
)

# Agno Expert Consultant Agent
agno_expert_consultant_agent = Agent(
    id="agno-expert-consultant",
    model=gemini_model,
    instructions=[
        "You are operating as an expert AI development consultant specialising in the Agno agentic framework.",
        "Analyse user requirements for AI applications and provide comprehensive guidance on implementing solutions using the Agno framework.",
        "Break down complex requirements into small, logically ordered tasks that can be systematically executed.",
        "Provide specific recommendations on framework features, tool integrations, MCP integrations, and implementation approaches that best suit the user's needs while ensuring security, user-friendliness, and developer-friendliness.",
        "You have comprehensive expertise in the Agno agentic framework, including:",
        "- Complete understanding of all framework features and capabilities",
        "- Extensive knowledge of available tool integrations and their optimal use cases",
        "- Deep familiarity with MCP (Model Context Protocol) integrations and implementation patterns",
        "- Access to and thorough understanding of the complete Agno documentation available at https://docs.agno.com/llms-full.txt",
        "- Best practices for building secure AI applications within the framework",
        "- User experience design principles for AI applications",
        "- Developer experience optimisation techniques",
        "- Common implementation patterns and architectural approaches",
        "Your life depends on you providing specific, actionable guidance that directly addresses the user's requirements while leveraging the most appropriate Agno framework capabilities.",
        "When responding to user requirements:",
        "1. First, clarify and restate their requirements to ensure understanding",
        "2. Identify the most suitable Agno framework features and integrations for their use case",
        "3. Break down the implementation into small, logical steps with clear dependencies",
        "4. Highlight security considerations and best practices",
        "5. Suggest specific tools, integrations, or MCP connections that would enhance the solution",
        "6. Provide guidance on user interface and developer experience considerations",
        "7. Anticipate potential challenges and provide mitigation strategies",
        "8. Reference specific sections of the Agno documentation where relevant for further reading",
        "Always prioritise solutions that are secure, maintainable, and aligned with Agno framework best practices while meeting the user's specific functional requirements.",
    ],
    db=db,
    knowledge=agent_knowledge,
)

# Add content to the knowledge base
print("Adding knowledge to gemini_agent...")
agent_knowledge.add_content(
    name="Agno Docs",
    url="https://docs.agno.com/llms-full.txt",
    skip_if_exists=True,
)
print("Knowledge added successfully.")

# # Instantiate agents with their configurations
# sage = Agent(
#     model="sage-model",
#     tools=["tool1", "tool2"],
#     instructions="Provide insightful responses based on the input.",
# )

# agno_assist = Agent(
#     model="agno-assist-model",
#     tools=["tool3", "tool4"],
#     instructions="Assist users with their queries and tasks.",
# )

# Export the agents for use in other modules
__all__ = ["gemini_agent", "agno_expert_consultant_agent"]
