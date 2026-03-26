import logging
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime

# Internal backend explicit structural dependencies
from backend.db.connection import db_manager
from backend.llm.query_engine import get_query_engine
from backend.graph.queries import get_node, get_trace

logger = logging.getLogger(__name__)

# FastAPI Boot Lifecycle Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Application Lifespan Events...")
    # Eagerly trigger module singletons to verify memory/API payload mapping early
    try:
        get_query_engine()
    except Exception as e:
        logger.error(f"Failed to bootstrap centralized LLM Engine. Halt dependencies: {e}")
    yield
    # Explicit MVC Connection Teardowns
    db_manager.close()
    logger.info("Application cleanly detached and shutdown.")

app = FastAPI(title="Context Graph API System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Payload Schema Models ===
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    graph_data: list

# === EXPOSED API ROUTES ===

@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """Primary Text-To-Cypher Endpoint Pipeline"""
    try:
        engine = get_query_engine()
        result = engine.process_query(request.question)

        # Securely sanitize arbitrary Neo4j Datetimes or structural objects for FastAPI JSON mapping
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(v) for v in obj]
            elif hasattr(obj, 'labels') and hasattr(obj, 'items'):
                # Serialize Neo4j Node objects
                return {"id": getattr(obj, 'element_id', None), "labels": list(obj.labels), **sanitize(dict(obj.items()))}
            elif hasattr(obj, 'type') and hasattr(obj, 'start_node') and hasattr(obj, 'end_node'):
                # Serialize Neo4j Relationship bounds automatically into d3-force format
                return {
                    "type": obj.type, 
                    "source": getattr(obj.start_node, 'element_id', None) or getattr(obj.start_node, 'id', None) or str(obj.start_node), 
                    "target": getattr(obj.end_node, 'element_id', None) or getattr(obj.end_node, 'id', None) or str(obj.end_node), 
                    **sanitize(dict(obj.items()))
                }
            elif hasattr(obj, 'nodes') and hasattr(obj, 'relationships'):
                # Flatten Neo4j Path routing objects natively
                return {"nodes": sanitize(list(obj.nodes)), "links": sanitize(list(obj.relationships))}
            elif hasattr(obj, 'iso_format'):
                # Serialize Neo4j Timestamps
                return obj.iso_format()
            elif isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return obj

        safe_graph_data = sanitize(result["graph_data"])

        return QueryResponse(
            answer=result["answer"],
            graph_data=safe_graph_data
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Critical arbitrary failure over /api/chat: {e}")
        raise HTTPException(status_code=500, detail="Internal Central Engine Crash.")

@app.get("/api/graph/node/{node_id}")
async def fetch_node(node_id: str):
    """Direct database abstraction pulling explicit node payload securely"""
    node = get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Requested physical entity not locally identifiable.")
    return {"node": node}

@app.get("/api/graph/trace/{node_id}")
async def fetch_trace(node_id: str, depth: int = 3):
    """Lineage topological extraction (e.g. order -> delivery -> invoice -> payment traces)"""
    trace_data = get_trace(node_id, depth)
    return trace_data

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Context Graph API Backbone is fully operational."}
