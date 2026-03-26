import os
import logging
from backend.ingestion.ingest import run_ingestion
from backend.graph.builder import graph_builder
from backend.db.connection import db_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🚀 BOOTING AURA CLOUD HYDRATION PIPELINE')
    print('='*50 + '\n')
    
    # Resolving accurate path for neo4j desktop local volume
    IMPORT_DIR = "/Users/ayan/Library/Application Support/neo4j-desktop/Application/Data/dbmss/dbms-1660baa1-a526-46e2-a4dc-23e6973e547f/import"
    
    if not os.path.exists(IMPORT_DIR):
        print(f"CRITICAL: Failed to locate raw dataset volume at {IMPORT_DIR}")
        exit(1)
        
    try:
        # Step 1: Push recursive Nodes
        print("STAGE 1: Re-hydrating Cloud Database with Native Property Streams...")
        run_ingestion(IMPORT_DIR)
        
        # Step 2: Edge Mapping
        print("\nSTAGE 2: Generating Vectorized Relationships...")
        graph_builder.build_core_relationships()
        
        print("\n✅ CLOUD DEPLOYMENT COMPLETED!")
    except Exception as e:
        logger.error(f"Migration Failed: {e}")
    finally:
        db_manager.close()
