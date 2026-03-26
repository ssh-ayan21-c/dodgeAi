import logging
from backend.db.connection import get_db_driver

logger = logging.getLogger(__name__)

def get_node(node_id: str):
    """Fetches a specific target node decoupled from any LLM logic constraints."""
    driver = get_db_driver()
    query = """
    MATCH (n {id: $node_id})
    RETURN n
    """
    with driver.session() as session:
        result = session.run(query, node_id=node_id)
        record = result.single()
        return dict(record["n"]) if record else None

def get_trace(node_id: str, depth: int = 3):
    """
    Extracts a fully formatted trace lineage returning precise distinct node 
    dictionaries and topological vectors formatted explicitly for frontend visualization endpoints.
    """
    driver = get_db_driver()
    query = """
    MATCH path = (n {id: $node_id})-[*1..$depth]-(m)
    WITH nodes(path) AS ns, relationships(path) AS rs
    UNWIND ns AS node
    UNWIND rs AS rel
    RETURN collect(distinct node) AS nodes, collect(distinct rel) AS links
    """
    with driver.session() as session:
        result = session.run(query, node_id=node_id, depth=depth)
        record = result.single()
        
        # Guardrails for empty sets
        if not record or not record.get("nodes"):
            return {"nodes": [], "links": []}
            
        nodes = [dict(n) for n in record["nodes"]]
        # Safely parse relationship edges back into standard source/target JSONs
        links = [{"source": dict(r.start_node).get('id'), "target": dict(r.end_node).get('id'), "type": type(r).__name__} for r in record["links"]]
        return {"nodes": nodes, "links": links}

def get_all_nodes(limit: int = 150):
    """Failsafe global pool query."""
    driver = get_db_driver()
    query = "MATCH (n) RETURN n LIMIT $limit"
    with driver.session() as session:
        return [dict(x["n"]) for x in session.run(query, limit=limit)]
