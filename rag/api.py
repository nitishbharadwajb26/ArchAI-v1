"""
FastAPI Application
────────────────────
Exposes the RAG pipeline as REST endpoints.

Endpoints:
  POST /api/recommend   — Main architectural recommendation
  GET  /api/techs       — List available tech stacks with stats
  GET  /api/health      — Health check
  POST /api/retrieve    — Raw retrieval (for debugging)
  GET  /                — Simple HTML page redirecting to /docs

Run from the rag/ folder:
    cd E:/ArchAI/rag
    uvicorn api:app --reload --port 8000

Or, run from the project root:
    cd E:/ArchAI
    uvicorn rag.api:app --reload --port 8000
"""

import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ── Path bootstrap ──────────────────────────────────────────────────────────
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

from chain import RAGChain
from retriever import Retriever
from config.tech_registry import TECH_REGISTRY
from config.provider_config import get_config

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

# Globals — initialised in lifespan
chain: Optional[RAGChain] = None
retriever: Optional[Retriever] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise RAG chain at startup."""
    global chain, retriever
    cfg = get_config()
    logger.info("\n" + cfg.summary())
    logger.info("Initialising RAG chain...")
    retriever = Retriever()
    chain = RAGChain(retriever=retriever)
    logger.info("RAGChain ready ✓")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="ArchAI — Architectural Decision Engine",
    description="RAG-powered tech stack recommender backed by official documentation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    query: str
    tech_filter: Optional[list[str]] = None  # Optional: limit to specific techs


class RetrieveRequest(BaseModel):
    tech_ids: list[str]
    query: str
    top_k: int = 5


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with quick links."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArchAI</title>
        <style>
            body { font-family: -apple-system, system-ui, sans-serif; max-width: 700px;
                   margin: 60px auto; padding: 0 20px; color: #1a1a1a; }
            h1 { color: #2563eb; }
            a { color: #2563eb; text-decoration: none; }
            a:hover { text-decoration: underline; }
            code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
            .links { margin-top: 20px; }
            .links a { display: inline-block; margin-right: 15px; padding: 8px 14px;
                       background: #eff6ff; border-radius: 6px; }
        </style>
    </head>
    <body>
        <h1>ArchAI — Architectural Decision Engine</h1>
        <p>RAG-powered tech stack recommender backed by official documentation.</p>
        <div class="links">
            <a href="/docs">📖 API Docs</a>
            <a href="/api/health">💚 Health</a>
            <a href="/api/techs">📚 Available Tech Stacks</a>
        </div>
        <h3>Quick test</h3>
        <pre><code>curl -X POST http://localhost:8000/api/recommend \\
  -H "Content-Type: application/json" \\
  -d '{"query": "I need a scalable Python REST API with async"}'</code></pre>
    </body>
    </html>
    """


@app.post("/api/recommend")
async def recommend(request: RecommendRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query too long (max 2000 chars)")

    if chain is None:
        raise HTTPException(status_code=503, detail="RAG chain not initialised")

    try:
        response = chain.run(request.query)
        return response.to_dict()
    except Exception as e:
        logger.exception("Recommend endpoint failed")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")


@app.get("/api/techs")
async def list_techs():
    """Returns all tech stacks with their ChromaDB collection stats."""
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialised")

    stats = retriever.get_available_techs()
    stats_map = {s["tech_id"]: s for s in stats}

    result = []
    for tech_id, tech in TECH_REGISTRY.items():
        stat = stats_map.get(tech_id, {})
        result.append({
            "id": tech_id,
            "name": tech.name,
            "language": tech.language,
            "category": tech.category,
            "tags": tech.tags,
            "chunk_count": stat.get("chunk_count", 0),
            "status": stat.get("status", "empty"),
        })

    return {"techs": result, "total": len(result)}


@app.get("/api/health")
async def health():
    """Health check — verifies ChromaDB and provider connectivity."""
    cfg = get_config()
    health_data = {
        "status": "ok",
        "config": {
            "router_model": cfg.router_model,
            "router_provider": cfg.router_provider.value,
            "agent_model": cfg.agent_model,
            "agent_provider": cfg.agent_provider.value,
            "embedding_model": cfg.embedding_model,
            "embedding_provider": cfg.embedding_provider.value,
            "fully_local": cfg.is_fully_local(),
        },
    }

    # ChromaDB stats
    if retriever is not None:
        try:
            tech_stats = retriever.get_available_techs()
            health_data["chromadb"] = {
                "populated_collections": len(tech_stats),
                "total_chunks": sum(s.get("chunk_count", 0) for s in tech_stats),
                "techs": [s["tech_id"] for s in tech_stats],
            }
        except Exception as e:
            health_data["chromadb"] = {"error": str(e)}
            health_data["status"] = "degraded"
    else:
        health_data["chromadb"] = {"error": "retriever not initialised"}
        health_data["status"] = "degraded"

    # Provider check
    from config.provider_config import LLMProvider
    if cfg.agent_provider == LLMProvider.OLLAMA:
        try:
            from utils.embedding_factory import check_ollama_status
            health_data["ollama"] = check_ollama_status(cfg.ollama_base_url)
        except Exception as e:
            health_data["ollama"] = {"running": False, "error": str(e)}
    elif cfg.agent_provider == LLMProvider.GROQ:
        health_data["groq"] = {
            "api_key_set": bool(cfg.groq_api_key),
        }
        if not cfg.groq_api_key:
            health_data["status"] = "degraded"
            health_data["error"] = "GROQ_API_KEY not set in .env"

    return health_data


@app.post("/api/retrieve")
async def retrieve_chunks(request: RetrieveRequest):
    """Debug endpoint — returns raw retrieved chunks without running the LLM."""
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not initialised")
    chunks = retriever.retrieve(request.tech_ids, request.query, top_k=request.top_k)
    return {
        "query": request.query,
        "tech_ids": request.tech_ids,
        "chunks": chunks,
        "count": len(chunks),
    }
