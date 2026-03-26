import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

logger = logging.getLogger(__name__)

class Neo4jConnectionManager:
    """
    Singleton class to manage the universal Neo4j Driver pool connection
    for the lifespan of the FastAPI instance.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing universal Neo4j Connection Manager singleton...")
            cls._instance = super(Neo4jConnectionManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
        
    def _initialize(self):
        uri = os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "ayan@123")
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("Universal Driver successfully achieved connectivity to Neo4j.")
        except Exception as e:
            logger.error(f"CRITICAL: Failed to connect to Neo4j: {e}")
            self.driver = None

    def get_driver(self):
        if not self.driver:
            logger.warning("Driver disconnected or uninitialized. Requesting reconnection...")
            self._initialize()
        return self.driver

    def close(self):
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver connection cleanly closed across all pools.")
            self._instance = None

# Global alias exposing the underlying pool manager instance natively across imports
db_manager = Neo4jConnectionManager()

def get_db_driver():
    return db_manager.get_driver()
