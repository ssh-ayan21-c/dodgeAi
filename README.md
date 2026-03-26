# Dodge AI - Context Graph System

An LLM-powered Context Graph System tracing complex Order-to-Cash corporate processes natively into Neo4j instances, featuring an interactive physics-simulated Force Graph visualization dashboard.

## Repository Structure
- `/src/backend`: FastAPI server, Universal Data Ingestion pipelines, modular Graph Neo4j abstractions, and LangChain `gemini-2.5-flash` inference Engine.
- `/src/frontend`: React + Vite single-page application using `react-force-graph-2d` and Tailwind.
- `/src/load_jsonl_to_neo4j.py`: Direct Cloud database migration & node hydration runner.
- `/sessions/`: Dedicated storage allocation for future query session tracking / exported artifacts.
- `requirements.txt`: Python global package dependency matrix.

## Setup Instructions

### 1. Environment Configuration
Create a `.env` file cleanly in the Root directory mirroring your Neo4j Cloud / Local connections:
```env
NEO4J_URI=neo4j+s://<YOUR_AURA_ID>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<YOUR_PASSWORD>
GOOGLE_API_KEY=<YOUR_GEMINI_KEY>
```

### 2. Backend Initialization (Python 3.10+)
Initialize the isolated environment and boot the Graph API:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (Optional) Hydrate your interconnected Neo4j Database
cd src
python3 load_jsonl_to_neo4j.py

# Launch the FastAPI Inference Server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Dashboard Initialization (Node 18+)
Open a totally independent, parallel terminal window:
```bash
cd src/frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173` to explore the Graph Node physics canvas interactively!
