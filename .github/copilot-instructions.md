## Agno Codebase Instructions for AI Agents

This document provides essential guidelines for AI coding agents to effectively understand and contribute to the Agno codebase.

### 1. Big Picture Architecture

Agno is a high-performance runtime for multi-agent systems. Key components include:

- **AgentOS**: The core runtime, a FastAPI application for deploying and managing agentic systems. It includes a control plane for monitoring and runs securely in the user's cloud.
- **Agents**: Fundamental units defined by `agno.agent.Agent`, configured with models, tools, and instructions. They support memory, state, and multimodal capabilities.
- **Teams**: Collections of agents collaborating on tasks.
- **Workflows**: Step-based orchestrations for complex multi-step agent processes.
- **Database Integration**: Supports various databases (PostgreSQL, SQLite, MongoDB, etc.) for persistent storage, session management, and chat history.

### 2. Critical Developer Workflows

- **Environment Setup**:
  - Create virtual environment: `python3 -m venv .venv && source .venv/bin/activate`
  - Install core dependencies: `pip install openai ddgs yfinance lancedb tantivy pypdf requests exa-py newspaper4k lxml_html_clean sqlalchemy agno`
  - Install specific database drivers as needed (e.g., `pip install psycopg2-binary` for PostgreSQL).
- **Running Agents/AgentOS**:
  - Individual agents: `python <path_to_agent_file.py>`
  - AgentOS applications: `agent_os.serve(app="my_app:app", reload=True)`
- **Performance Evaluation**: Refer to `evals/performance/` and `scripts/perf_setup.sh` for running benchmarks.

### 3. Project-Specific Conventions and Patterns

- **Agent Definition**: Agents are instantiated from `agno.agent.Agent`. Key parameters include `model`, `tools`, `instructions`, and `db` for persistence.
- **Tooling**: Agents integrate with `Agno ToolKits`, custom functions, or custom `Toolkit` classes for external interactions.
- **RAG**: Retrieval-Augmented Generation is implemented via integration with vector databases and knowledge bases (e.g., `cookbook/agents/rag/`).
- **Human-in-the-Loop**: Agents can be configured for user confirmation or dynamic input (e.g., `cookbook/agents/human_in_the_loop/`).
- **State Management**: Persistent session state and context are managed through database integrations (e.g., `cookbook/db/`).
- **Structured Output**: Pydantic models are used for defining and validating structured outputs from agents.
- **Model Specialization**: Different models can be designated for reasoning, parsing structured outputs, or generating final responses to optimize cost and performance (e.g., `cookbook/agents/other/parse_model.py`).

### 4. Integration Points and Dependencies

- **LLM Providers**: Integrates with various large language model providers (e.g., OpenAI, Anthropic).
- **External Tools**: Utilizes tools like HackerNews, DuckDuckGo, Exa, Newspaper4k for data retrieval and processing.
- **Databases**: Broad support for SQL and NoSQL databases for data persistence.
- **User Interfaces**: AgentOS can expose agents via interfaces like Slack, WhatsApp, and AGUI.
- **Model Context Protocol (MCP)**: Supports converting AgentOS into an MCP server for advanced multi-server communication (e.g., `cookbook/agent_os/mcp/`).

### 5. LLM-Friendly Documentation

For LLMs and AI assistants to efficiently parse and reference Agno's documentation, refer to the LLM-friendly documentation available at: `https://docs.agno.com/llms-full.txt`
