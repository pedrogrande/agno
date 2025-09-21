# Database-Driven Agent and Team Configuration System

This implementation provides a complete database-driven configuration system for Agno agents and teams, moving away from hard-coded definitions to a dynamic, PostgreSQL-based approach.

## 🌟 Features

- **Database-Driven Configuration**: Store agent and team definitions in PostgreSQL
- **Dynamic Loading**: Load agents and teams at runtime from database configurations
- **Backward Compatibility**: Fallback to hard-coded configurations if database is unavailable
- **Admin Interface**: Streamlit-based web interface for managing configurations
- **MCP Integration**: Leverages Agno's Model Context Protocol for configuration management
- **Caching**: Performance optimization with intelligent caching
- **Hot Reloading**: Update configurations without restarting the application

## 📁 Project Structure

```
agno/
├── database_schemas.sql          # Database table definitions
├── mcp_connector.py             # PostgreSQL MCP connector
├── dynamic_loader.py            # Dynamic agent/team loader
├── seed_database.py             # Database seeding script
├── setup_database.py            # Complete setup script
├── test_end_to_end.py           # End-to-end testing
├── admin_interface.py           # Streamlit admin interface
└── my-agentos-app/
    ├── _agents_dynamic.py       # Dynamic agents module
    ├── _teams_dynamic.py        # Dynamic teams module
    ├── main_dynamic.py          # Updated main application
    ├── _agents.py               # Original agents (fallback)
    ├── _teams.py                # Original teams (fallback)
    └── main.py                  # Original main (fallback)
```

## 🚀 Quick Start

### 1. Prerequisites

Ensure you have PostgreSQL running. If using Docker:

```bash
docker run -d --name postgres \
    -e POSTGRES_USER=ai \
    -e POSTGRES_PASSWORD=ai \
    -e POSTGRES_DB=ai \
    -p 5532:5432 \
    postgres:13
```

### 2. Setup Database

Run the complete setup script:

```bash
cd /home/runner/work/agno/agno
python setup_database.py
```

This will:
- Check database connectivity
- Create all necessary tables
- Seed with initial agent and team configurations
- Verify the setup

### 3. Run the Application

Start the application with database-driven configuration:

```bash
cd my-agentos-app
python main_dynamic.py
```

The application will:
- Load agents and teams from the database
- Fall back to hard-coded configurations if database is unavailable
- Provide management endpoints at `/admin/status` and `/admin/reload`

### 4. Use the Admin Interface

Launch the Streamlit admin interface:

```bash
cd /home/runner/work/agno/agno
streamlit run admin_interface.py
```

Features:
- View and edit agent configurations
- Manage team compositions
- Create new agents and teams
- Monitor system status

## 📊 Database Schema

### Agents Table

| Column | Type | Description |
|--------|------|-------------|
| agent_id | VARCHAR (PK) | Unique agent identifier |
| name | VARCHAR | Human-readable agent name |
| model_id | VARCHAR | Model identifier (e.g., "gemini-2.5-flash") |
| model_provider | VARCHAR | Model provider ("google", "openai", etc.) |
| instructions | TEXT | Agent instructions |
| description | TEXT | Agent description |
| system_prompt | TEXT | Optional system prompt |
| tool_ids | JSONB | Array of tool identifiers |
| memory_config | JSONB | Memory configuration object |
| knowledge_config | JSONB | Knowledge configuration object |
| session_config | JSONB | Session configuration object |
| additional_config | JSONB | Additional configuration options |
| is_active | BOOLEAN | Whether agent is active |
| created_at | BIGINT | Creation timestamp |
| updated_at | BIGINT | Last update timestamp |

### Teams Table

| Column | Type | Description |
|--------|------|-------------|
| team_id | VARCHAR (PK) | Unique team identifier |
| name | VARCHAR | Human-readable team name |
| description | TEXT | Team description |
| instructions | TEXT | Team instructions |
| agent_ids | JSONB | Array of member agent IDs |
| orchestration_pattern | VARCHAR | "sequential", "hierarchical", "collaborative" |
| team_config | JSONB | Team-specific configuration |
| is_active | BOOLEAN | Whether team is active |
| created_at | BIGINT | Creation timestamp |
| updated_at | BIGINT | Last update timestamp |

### Tools Table

| Column | Type | Description |
|--------|------|-------------|
| tool_id | VARCHAR (PK) | Unique tool identifier |
| name | VARCHAR | Human-readable tool name |
| description | TEXT | Tool description |
| tool_type | VARCHAR | "builtin", "custom", "external" |
| tool_class | VARCHAR | Python class name for custom tools |
| tool_config | JSONB | Tool-specific configuration |
| is_active | BOOLEAN | Whether tool is active |
| created_at | BIGINT | Creation timestamp |
| updated_at | BIGINT | Last update timestamp |

## 🔧 API Usage

### Loading Agents Dynamically

```python
from dynamic_loader import DynamicAgentLoader

# Initialize loader
loader = DynamicAgentLoader(db_url="postgresql+psycopg://ai:ai@localhost:5532/ai")

# Load specific agent
agent = loader.load_agent("gemini-agent")

# Load all active agents
agents = loader.load_all_agents()

# Load specific team
team = loader.load_team("rag-team")
```

### Using the MCP Connector

```python
from mcp_connector import PostgresMCPConnector

with PostgresMCPConnector(db_url="your_db_url") as connector:
    # Save agent configuration
    agent_config = {
        'agent_id': 'my-agent',
        'name': 'My Agent',
        'model_id': 'gpt-4',
        'model_provider': 'openai',
        'instructions': 'You are a helpful assistant.',
        'is_active': True
    }
    connector.save_agent_config(agent_config)
    
    # Load agent configuration
    config = connector.load_agent_config('my-agent')
    
    # Create agent from config
    agent = connector.create_agent_from_config(config, db=my_db)
```

### Management Endpoints

When running the dynamic application, these endpoints are available:

- `GET /admin/status` - View current configuration status
- `GET /admin/reload` - Reload configurations from database

```bash
# Check status
curl http://localhost:8000/admin/status

# Reload configurations
curl http://localhost:8000/admin/reload
```

## 🧪 Testing

Run the end-to-end test suite:

```bash
python test_end_to_end.py
```

This tests:
- MCP connector functionality
- Dynamic loader operations
- Agent and team module loading
- Integration with the application

## 🔄 Migration from Hard-Coded

The system provides backward compatibility:

1. **Automatic Fallback**: If database is unavailable, falls back to hard-coded configurations
2. **Gradual Migration**: You can migrate agents/teams one by one
3. **Dual Mode**: Both systems can coexist during transition

### Migration Steps

1. Set up the database using `setup_database.py`
2. Verify seeded data matches your existing configurations
3. Test with `main_dynamic.py` alongside existing `main.py`
4. Gradually move custom configurations to database
5. Switch to dynamic mode permanently

## 🛠️ Configuration Examples

### Creating a New Agent

```python
agent_config = {
    'agent_id': 'research-agent',
    'name': 'Research Assistant',
    'model_id': 'gpt-4-turbo',
    'model_provider': 'openai',
    'instructions': [
        'You are a research assistant specialized in academic papers.',
        'Provide detailed analysis and summaries.',
        'Always cite your sources.'
    ],
    'description': 'AI assistant for academic research',
    'tool_ids': ['web-search', 'pdf-reader', 'citation-tool'],
    'memory_config': {
        'enable_session_summaries': True,
        'enable_user_memories': True,
        'num_history_runs': 5
    },
    'knowledge_config': {
        'knowledge_enabled': True,
        'vector_db_table': 'research_knowledge'
    },
    'is_active': True
}

connector.save_agent_config(agent_config)
```

### Creating a New Team

```python
team_config = {
    'team_id': 'research-team',
    'name': 'Academic Research Team',
    'description': 'Team specialized in academic research and analysis',
    'instructions': 'Collaborate to provide comprehensive research assistance',
    'agent_ids': ['research-agent', 'analysis-agent', 'writing-agent'],
    'orchestration_pattern': 'sequential',
    'team_config': {
        'collaboration_type': 'research_pipeline',
        'output_format': 'academic_report'
    },
    'is_active': True
}

connector.save_team_config(team_config)
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection manually
psql -h localhost -p 5532 -U ai -d ai
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install psycopg2-binary sqlalchemy agno
```

### Agent Loading Failures

Check logs for specific errors:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Configuration Validation

Use the test script to verify setup:
```bash
python test_end_to_end.py
```

## 📈 Performance Considerations

- **Caching**: Agents and teams are cached after first load
- **Connection Pooling**: Consider using connection pooling for high-load scenarios
- **Lazy Loading**: Agents are only instantiated when first accessed
- **Batch Operations**: Use bulk operations for multiple configuration changes

## 🔐 Security Best Practices

1. **Database Security**: Secure your PostgreSQL instance with proper authentication
2. **Network Security**: Use SSL connections for production databases
3. **Access Control**: Implement role-based access control for configuration management
4. **Secrets Management**: Store sensitive configuration in environment variables or secret management systems
5. **Audit Trail**: The system automatically tracks creation and update timestamps

## 🤝 Contributing

1. Test changes with the end-to-end test suite
2. Update documentation for new features
3. Follow the existing code style and patterns
4. Ensure backward compatibility when possible

## 📝 License

This implementation follows the same license as the Agno framework.