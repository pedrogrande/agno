-- Database Schema for Agent and Team Configuration System
-- This script creates the necessary tables for storing agent, team, and tool configurations

-- Create agents table to store agent configurations
CREATE TABLE IF NOT EXISTS agents (
    agent_id VARCHAR PRIMARY KEY NOT NULL,
    name VARCHAR NOT NULL,
    model_id VARCHAR NOT NULL,
    model_provider VARCHAR,
    instructions TEXT,
    description TEXT,
    system_prompt TEXT,
    tool_ids JSONB DEFAULT '[]'::jsonb,  -- Array of tool IDs
    memory_config JSONB DEFAULT '{}'::jsonb,  -- Memory configuration
    knowledge_config JSONB DEFAULT '{}'::jsonb,  -- Knowledge configuration
    session_config JSONB DEFAULT '{}'::jsonb,  -- Session configuration
    additional_config JSONB DEFAULT '{}'::jsonb,  -- Additional configurations
    is_active BOOLEAN DEFAULT true,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000,
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000
);

-- Create teams table to store team configurations
CREATE TABLE IF NOT EXISTS teams (
    team_id VARCHAR PRIMARY KEY NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    instructions TEXT,
    agent_ids JSONB DEFAULT '[]'::jsonb,  -- Array of agent IDs
    orchestration_pattern VARCHAR DEFAULT 'sequential',  -- sequential, hierarchical, collaborative
    team_config JSONB DEFAULT '{}'::jsonb,  -- Team-specific configuration
    is_active BOOLEAN DEFAULT true,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000,
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000
);

-- Create tools table to store tool configurations (optional for dynamic tool management)
CREATE TABLE IF NOT EXISTS tools (
    tool_id VARCHAR PRIMARY KEY NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    tool_type VARCHAR NOT NULL,  -- builtin, custom, external
    tool_class VARCHAR,  -- Python class name for custom tools
    tool_config JSONB DEFAULT '{}'::jsonb,  -- Tool-specific configuration
    is_active BOOLEAN DEFAULT true,
    created_at BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000,
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()) * 1000
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);
CREATE INDEX IF NOT EXISTS idx_teams_active ON teams(is_active);
CREATE INDEX IF NOT EXISTS idx_teams_created_at ON teams(created_at);
CREATE INDEX IF NOT EXISTS idx_tools_active ON tools(is_active);
CREATE INDEX IF NOT EXISTS idx_tools_type ON tools(tool_type);

-- Create a trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = EXTRACT(EPOCH FROM NOW()) * 1000;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply the trigger to all tables
DROP TRIGGER IF EXISTS update_agents_modtime ON agents;
CREATE TRIGGER update_agents_modtime 
    BEFORE UPDATE ON agents 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS update_teams_modtime ON teams;
CREATE TRIGGER update_teams_modtime 
    BEFORE UPDATE ON teams 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();

DROP TRIGGER IF EXISTS update_tools_modtime ON tools;
CREATE TRIGGER update_tools_modtime 
    BEFORE UPDATE ON tools 
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();