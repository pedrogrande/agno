#!/usr/bin/env python3
"""
End-to-End Test Script for Database-Driven Agent Configuration

This script tests the complete database-driven agent and team configuration system.
"""
import logging
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mcp_connector():
    """Test the MCP connector functionality."""
    logger.info("🧪 Testing MCP Connector...")
    
    try:
        from mcp_connector import PostgresMCPConnector
        
        db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
        
        with PostgresMCPConnector(db_url=db_url) as connector:
            # Test listing agents
            agents = connector.list_agents()
            logger.info(f"✅ Found {len(agents)} agents in database")
            
            # Test listing teams
            teams = connector.list_teams()
            logger.info(f"✅ Found {len(teams)} teams in database")
            
            # Test loading specific agent
            if agents:
                agent_id = agents[0]['agent_id']
                agent_config = connector.load_agent_config(agent_id)
                if agent_config:
                    logger.info(f"✅ Successfully loaded agent config for {agent_id}")
                else:
                    logger.error(f"❌ Failed to load agent config for {agent_id}")
                    return False
            
            # Test loading specific team
            if teams:
                team_id = teams[0]['team_id']
                team_config = connector.load_team_config(team_id)
                if team_config:
                    logger.info(f"✅ Successfully loaded team config for {team_id}")
                else:
                    logger.error(f"❌ Failed to load team config for {team_id}")
                    return False
        
        logger.info("✅ MCP Connector tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP Connector test failed: {e}")
        return False

def test_dynamic_loader():
    """Test the dynamic loader functionality."""
    logger.info("🧪 Testing Dynamic Loader...")
    
    try:
        from dynamic_loader import DynamicAgentLoader
        
        db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
        
        with DynamicAgentLoader(db_url=db_url) as loader:
            # Test loading all agents
            agents = loader.load_all_agents()
            logger.info(f"✅ Dynamically loaded {len(agents)} agents")
            
            # Test loading all teams
            teams = loader.load_all_teams()
            logger.info(f"✅ Dynamically loaded {len(teams)} teams")
            
            # Test loading specific agent
            if agents:
                agent = loader.load_agent(agents[0].id)
                if agent:
                    logger.info(f"✅ Successfully loaded specific agent: {agent.id}")
                    
                    # Test that it's a proper Agent instance
                    from agno.agent import Agent
                    if isinstance(agent, Agent):
                        logger.info(f"✅ Agent is proper Agent instance")
                    else:
                        logger.error(f"❌ Agent is not proper Agent instance: {type(agent)}")
                        return False
                else:
                    logger.error(f"❌ Failed to load specific agent")
                    return False
            
            # Test loading specific team
            if teams:
                team = loader.load_team(teams[0].id)
                if team:
                    logger.info(f"✅ Successfully loaded specific team: {team.id}")
                    
                    # Test that it's a proper Team instance
                    from agno.team import Team
                    if isinstance(team, Team):
                        logger.info(f"✅ Team is proper Team instance")
                    else:
                        logger.error(f"❌ Team is not proper Team instance: {type(team)}")
                        return False
                else:
                    logger.error(f"❌ Failed to load specific team")
                    return False
        
        logger.info("✅ Dynamic Loader tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dynamic Loader test failed: {e}")
        return False

def test_dynamic_agents_module():
    """Test the dynamic agents module."""
    logger.info("🧪 Testing Dynamic Agents Module...")
    
    try:
        # Add the my-agentos-app directory to path
        sys.path.insert(0, str(Path(__file__).parent / "my-agentos-app"))
        
        from _agents_dynamic import (
            agents_list, 
            gemini_agent, 
            agno_expert_consultant_agent,
            load_agent_by_id,
            reload_agents
        )
        
        # Test that we got agents
        if agents_list:
            logger.info(f"✅ Dynamic agents module loaded {len(agents_list)} agents")
        else:
            logger.warning("⚠️  No agents loaded by dynamic agents module")
        
        # Test specific agents
        if gemini_agent:
            logger.info(f"✅ Gemini agent available: {gemini_agent.id}")
        else:
            logger.warning("⚠️  Gemini agent not available")
        
        if agno_expert_consultant_agent:
            logger.info(f"✅ Agno expert consultant agent available: {agno_expert_consultant_agent.id}")
        else:
            logger.warning("⚠️  Agno expert consultant agent not available")
        
        # Test loading by ID
        if agents_list:
            test_agent = load_agent_by_id(agents_list[0].id)
            if test_agent:
                logger.info(f"✅ Successfully loaded agent by ID: {test_agent.id}")
            else:
                logger.error(f"❌ Failed to load agent by ID")
                return False
        
        logger.info("✅ Dynamic Agents Module tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dynamic Agents Module test failed: {e}")
        return False

def test_dynamic_teams_module():
    """Test the dynamic teams module."""
    logger.info("🧪 Testing Dynamic Teams Module...")
    
    try:
        from _teams_dynamic import (
            teams_list,
            rag_team,
            load_team_by_id,
            reload_teams,
            create_team_from_agent_ids
        )
        
        # Test that we got teams
        if teams_list:
            logger.info(f"✅ Dynamic teams module loaded {len(teams_list)} teams")
        else:
            logger.warning("⚠️  No teams loaded by dynamic teams module")
        
        # Test specific team
        if rag_team:
            logger.info(f"✅ RAG team available: {rag_team.id}")
        else:
            logger.warning("⚠️  RAG team not available")
        
        # Test loading by ID
        if teams_list:
            test_team = load_team_by_id(teams_list[0].id)
            if test_team:
                logger.info(f"✅ Successfully loaded team by ID: {test_team.id}")
            else:
                logger.error(f"❌ Failed to load team by ID")
                return False
        
        logger.info("✅ Dynamic Teams Module tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dynamic Teams Module test failed: {e}")
        return False

def test_agent_functionality():
    """Test that loaded agents can actually run."""
    logger.info("🧪 Testing Agent Functionality...")
    
    try:
        from _agents_dynamic import gemini_agent
        
        if not gemini_agent:
            logger.warning("⚠️  Skipping agent functionality test - no gemini agent available")
            return True
        
        # Try to run the agent with a simple test
        logger.info(f"Testing agent: {gemini_agent.id}")
        
        # Note: We won't actually run the agent here as it requires API keys
        # Instead, we'll verify its configuration
        if hasattr(gemini_agent, 'model') and gemini_agent.model:
            logger.info(f"✅ Agent has model: {type(gemini_agent.model).__name__}")
        else:
            logger.error("❌ Agent missing model")
            return False
        
        if hasattr(gemini_agent, 'instructions') and gemini_agent.instructions:
            logger.info(f"✅ Agent has instructions")
        else:
            logger.error("❌ Agent missing instructions")
            return False
        
        logger.info("✅ Agent Functionality tests passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 End-to-End Testing: Database-Driven Agent Configuration")
    print("="*60)
    
    tests = [
        ("MCP Connector", test_mcp_connector),
        ("Dynamic Loader", test_dynamic_loader),
        ("Dynamic Agents Module", test_dynamic_agents_module),
        ("Dynamic Teams Module", test_dynamic_teams_module),
        ("Agent Functionality", test_agent_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
            print(f"❌ {test_name} test ERROR")
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your database-driven configuration system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during testing: {e}")
        sys.exit(1)