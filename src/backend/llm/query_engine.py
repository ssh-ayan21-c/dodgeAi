import os
import logging
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
logger = logging.getLogger(__name__)

class GraphQueryEngine:
    """
    Decoupled LLM AI Layer. Wraps Google Gemini and Neo4j drivers
    to parse Natural Language strictly into validated Cypher executions
    running internally over the normalized dataset graph structure.
    """
    def __init__(self):
        uri = os.environ.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "ayan@123")
        google_api_key = os.environ.get("GOOGLE_API_KEY")

        if not google_api_key:
            logger.error("GOOGLE_API_KEY missing from environment payload!")
            raise ValueError("GOOGLE_API_KEY environment variable is absolutely required.")

        logger.info("Booting LangChain Neo4j Graph Schema Interrogator...")
        self.graph = Neo4jGraph(url=uri, username=user, password=password)
        self.graph.refresh_schema()

        logger.info("Initializing Google Gemini 2.5 Flash constraints for Cypher synthesis...")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

        self._setup_prompts()

    def _setup_prompts(self):
        self.cypher_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Neo4j Cypher translator. Convert the natural language question into a precise Cypher query based on the following graph schema:\n{schema}\n\nIMPORTANT: Return ONLY the raw Cypher query string. Do NOT include markdown blocks like ```cypher and do NOT include explanations."),
            ("human", "Question: {question}")
        ])

        self.correction_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert Neo4j Cypher developer. The following Cypher query executed against the schema produced an execution error. Fix the query and return ONLY the corrected raw Cypher string.\nSchema:\n{schema}\n\nOriginal Query:\n{query}\n\nError Message:\n{error}"),
            ("human", "Fix the query to answer: {question}")
        ])

        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful data analyst. Format your answer using cleanly structured Markdown (bullet points, bold text for key:values, lists) to ensure maximum frontend readability. Avoid dense paragraphs. Use the provided database query results to answer the user's original question naturally. If the results are empty, state that no matching records were found."),
            ("human", "Question: {question}\nDatabase Results: {results}")
        ])

        # Functional Pipeline Chains
        self.cypher_chain = self.cypher_prompt | self.llm
        self.correction_chain = self.correction_prompt | self.llm
        self.summary_chain = self.summary_prompt | self.llm

    def execute_with_self_correction(self, question: str, max_retries: int = 3):
        schema = self.graph.get_schema
        response = self.cypher_chain.invoke({"question": question, "schema": schema})
        current_query = response.content.replace("```cypher", "").replace("```", "").strip()

        for attempt in range(max_retries):
            try:
                logger.info(f"Internal Execution Attempt {attempt + 1} | Vectorized Query:\n{current_query}")
                results = self.graph.query(current_query)
                logger.info("Cypher query processed flawlessly.")
                return current_query, results
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} System Rejected. Cypher Fault: {e}")
                if attempt == max_retries - 1:
                    logger.error("Max self-correction iterations exceeded. Aborting graph pipeline.")
                    raise e
                
                correction_response = self.correction_chain.invoke({
                    "question": question,
                    "schema": schema,
                    "query": current_query,
                    "error": str(e)
                })
                current_query = correction_response.content.replace("```cypher", "").replace("```", "").strip()

    def process_query(self, question: str):
        try:
            cypher_query, raw_results = self.execute_with_self_correction(question)
            
            # NLP Answer Synthesis
            summary_response = self.summary_chain.invoke({
                "question": question,
                "results": str(raw_results)
            })
            answer = summary_response.content
            
            return {
                "answer": answer,
                "cypher_query": cypher_query,
                "graph_data": raw_results
            }
        except Exception as e:
            logger.error(f"Fatal Engine Failure Triggered: {e}")
            raise ValueError(str(e))

# Lazy-loaded Singleton 
engine_instance = None

def get_query_engine():
    global engine_instance
    if engine_instance is None:
        logger.info("Spawning core generic Google Gemini instance locally...")
        engine_instance = GraphQueryEngine()
    return engine_instance
