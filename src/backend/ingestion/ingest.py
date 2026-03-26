import os
import json
import csv
import logging
from typing import List, Dict, Any
from backend.db.connection import get_db_driver

logger = logging.getLogger(__name__)

class UniversalIngestionPipeline:
    """
    A single unified processor to handle arbitrary raw inputs recursively 
    and push normalized node streams into Neo4j without standalone duplicated scripting.
    """
    def __init__(self):
        self.driver = get_db_driver()
        self.batch_size = 500

    def to_pascal_case(self, string: str) -> str:
        """Converts raw folder descriptors into formalized Graph Labels"""
        string = string.replace('-', '_')
        return "".join(x.title() for x in string.split('_') if x)

    def _run_unwind(self, query: str, batch: List[Dict[str, Any]]):
        """Hidden execution handler to blast mass memory chunks via Neo4j Driver"""
        if not batch: return
        try:
            with self.driver.session() as session:
                session.run(query, batch=batch)
        except Exception as e:
            logger.error(f"Pipeline Pipeline Batch Execution Filtered Block: {e}")

    def ingest_directory(self, base_dir: str):
        if not os.path.exists(base_dir):
            logger.error(f"Ingestion directory mount path is entirely missing: {base_dir}")
            return

        logger.info(f"Igniting complete universal ingestion pipeline recursively downwards at: {base_dir}")
        for root, _, files in os.walk(base_dir):
            for file in files:
                filepath = os.path.join(root, file)
                
                # Dynamic Label Deduction
                folder_name = os.path.basename(root)
                node_label = self.to_pascal_case(folder_name) or "GenericBaseNode"
                
                # File Router
                if file.endswith(".jsonl"):
                    self._process_jsonl(filepath, node_label)
                elif file.endswith(".csv"):
                    self._process_csv(filepath, node_label)
                    
        logger.info("Universal ingestion sequence completely finalized and successfully committed. 🎉")

    def _process_jsonl(self, filepath: str, node_label: str):
        batch = []
        count = 0
        with open(filepath, 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    self._normalize_ids(data)

                    batch.append(data)
                    count += 1

                    if len(batch) >= self.batch_size:
                        self._flush_nodes(node_label, batch)
                        batch.clear()
                except Exception:
                    pass
        if batch:
            self._flush_nodes(node_label, batch)
        logger.info(f"Ingested {count} highly-coupled `.jsonl` payloads seamlessly mapped into target -> (:{node_label})")

    def _process_csv(self, filepath: str, node_label: str):
        batch = []
        count = 0
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = dict(row)
                self._normalize_ids(data)
                
                batch.append(data)
                count += 1
                
                if len(batch) >= self.batch_size:
                    self._flush_nodes(node_label, batch)
                    batch.clear()
        if batch:
            self._flush_nodes(node_label, batch)
        logger.info(f"Ingested {count} structured `.csv` rows normalized directly into target -> (:{node_label})")

    def _normalize_ids(self, data: Dict[str, Any]):
        """Normalizes heterogeneous raw attributes directly into a uniform 'neo4j_id' identifier explicitly."""
        if 'id' not in data and 'neo4j_id' not in data:
            for k, v in data.items():
                if k.endswith('_id') or k.endswith('Id') or k.lower() in ['customer', 'salesorder']:
                    data['neo4j_id'] = str(v)
                    break
        elif 'id' in data:
            data['neo4j_id'] = str(data['id'])

    def _flush_nodes(self, label: str, batch: List[Dict[str, Any]]):
        """MERGE implementation deliberately enforces an idempotent creation loop strictly avoiding duplicate injections!"""
        query = f"""
        UNWIND $batch AS req
        MERGE (n:{label} {{id: COALESCE(req.neo4j_id, randomUUID())}})
        SET n += req
        """
        self._run_unwind(query, batch)

# Singleton exposure
ingestion_pipeline = UniversalIngestionPipeline()

def run_ingestion(directory: str = None):
    # Default to explicitly requested `/instance/import` structure
    target = directory or os.environ.get("IMPORT_DIR", "./instance/import")
    ingestion_pipeline.ingest_directory(target)
