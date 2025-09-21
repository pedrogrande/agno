#!/usr/bin/env python3
"""
Setup script for the database-driven agent and team configuration system.

This script handles the complete setup process:
1. Creates the database tables
2. Seeds the database with initial data
3. Verifies the setup
"""
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to Python path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print("❌ psycopg not installed. Please install it using: pip install psycopg2-binary")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_URL = "postgresql+psycopg://ai:ai@localhost:5532/ai"
SCHEMA_FILE = Path(__file__).parent.parent / "database_schemas.sql"

def check_database_connection() -> bool:
    """
    Check if we can connect to the PostgreSQL database.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    logger.info("✅ Database connection successful")
                    return True
        return False
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def create_database_tables() -> bool:
    """
    Create the database tables using the schema file.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not SCHEMA_FILE.exists():
            logger.error(f"❌ Schema file not found: {SCHEMA_FILE}")
            return False
        
        # Read the schema file
        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute(schema_sql)
                conn.commit()
                logger.info("✅ Database tables created successfully")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        return False

def seed_database() -> bool:
    """
    Seed the database with initial data.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import and run the seeding script
        from seed_database import seed_database, verify_seeded_data
        
        logger.info("🌱 Seeding database with initial data...")
        seed_database()
        
        logger.info("🔍 Verifying seeded data...")
        verify_seeded_data()
        
        logger.info("✅ Database seeding completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        return False

def verify_setup() -> bool:
    """
    Verify that the setup was successful by testing the dynamic loader.
    
    Returns:
        True if verification successful, False otherwise
    """
    try:
        logger.info("🔍 Verifying setup by testing dynamic loader...")
        
        from dynamic_loader import DynamicAgentLoader
        
        with DynamicAgentLoader(db_url=DB_URL) as loader:
            # Test loading agents
            agents = loader.load_all_agents()
            logger.info(f"✅ Successfully loaded {len(agents)} agents")
            
            # Test loading teams
            teams = loader.load_all_teams()
            logger.info(f"✅ Successfully loaded {len(teams)} teams")
            
            # Test loading specific agent
            gemini_agent = loader.load_agent('gemini-agent')
            if gemini_agent:
                logger.info(f"✅ Successfully loaded specific agent: {gemini_agent.id}")
            else:
                logger.warning("⚠️  Could not load gemini-agent")
            
            # Test loading specific team
            rag_team = loader.load_team('rag-team')
            if rag_team:
                logger.info(f"✅ Successfully loaded specific team: {rag_team.id}")
            else:
                logger.warning("⚠️  Could not load rag-team")
        
        logger.info("✅ Setup verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup verification failed: {e}")
        return False

def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("🚀 Database-Driven Agent Configuration Setup")
    print("="*60)
    
    # Step 1: Check database connection
    print("\n📡 Step 1: Checking database connection...")
    if not check_database_connection():
        print("\n❌ Setup failed: Cannot connect to database")
        print("💡 Make sure PostgreSQL is running and accessible at:")
        print(f"   {DB_URL}")
        print("💡 You can start PostgreSQL using Docker:")
        print("   docker run -d --name postgres -e POSTGRES_USER=ai -e POSTGRES_PASSWORD=ai -e POSTGRES_DB=ai -p 5532:5432 postgres:13")
        return False
    
    # Step 2: Create database tables
    print("\n🏗️  Step 2: Creating database tables...")
    if not create_database_tables():
        print("\n❌ Setup failed: Could not create database tables")
        return False
    
    # Step 3: Seed database
    print("\n🌱 Step 3: Seeding database with initial data...")
    if not seed_database():
        print("\n❌ Setup failed: Could not seed database")
        return False
    
    # Step 4: Verify setup
    print("\n🔍 Step 4: Verifying setup...")
    if not verify_setup():
        print("\n❌ Setup failed: Verification failed")
        return False
    
    # Success!
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    print("\n✅ Your database-driven agent configuration system is ready!")
    print("\n🚀 Next steps:")
    print("   1. Run the application: python main_dynamic.py")
    print("   2. Access management endpoints:")
    print("      - GET /admin/status - View current configuration")
    print("      - GET /admin/reload - Reload from database")
    print("   3. Modify agent/team configurations in the database")
    print("   4. Use the reload endpoint to pick up changes")
    print("\n💡 You can also manage configurations programmatically:")
    print("   from mcp_connector import PostgresMCPConnector")
    print("   connector = PostgresMCPConnector(db_url='...')")
    print("   # Use connector.save_agent_config(), etc.")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error during setup: {e}")
        sys.exit(1)