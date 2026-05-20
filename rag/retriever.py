"""
RAG Retriever
─────────────
Queries ChromaDB collections using the existing ChromaStorage layer
from the scraper module.

Collection naming follows the scraper convention:
    architectai_docs_{tech_id}   e.g. architectai_docs_fastapi

Usage:
    from rag.retriever import Retriever
    retriever = Retriever()
    chunks = retriever.retrieve(["fastapi", "react"], "how to build a REST API")
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# ── Path bootstrap ─────────────────────────────────────────────────────────
# Allows the RAG folder to reuse scraper's storage, config and utils
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

from storage.chroma_store import ChromaStorage
from config.tech_registry import TECH_REGISTRY, get_tech

logger = logging.getLogger(__name__)


class Retriever:
    """
    Wraps ChromaStorage and provides RAG-friendly query methods.
    """

    def __init__(self, top_k: int = 5):
        """
        Args:
            top_k: Number of chunks to retrieve per query (default 5).
        """
        self.top_k = top_k

        # Always resolve chromadb path relative to the scraper folder,
        # regardless of which directory the script is run from.
        chroma_path = str(SCRAPER_ROOT / "data" / "chromadb")
        self.storage = ChromaStorage(persist_dir=chroma_path)
        logger.info(f"Retriever initialised | top_k={top_k} | chroma_path={chroma_path}")

    # ── Main retrieve method ────────────────────────────────────────────────

    def retrieve(
        self,
        tech_ids: list[str],
        query: str,
        top_k: Optional[int] = None,
        only_code: bool = False,
    ) -> list[dict]:
        """
        Retrieve relevant chunks for a list of tech stacks.

        Args:
            tech_ids   : e.g. ["fastapi", "react"]
            query      : User's natural language query
            top_k      : Override instance-level top_k for this call
            only_code  : If True, filter to chunks that contain code examples

        Returns:
            List of dicts with keys: content, metadata, relevance_score, tech_id
        """
        if not tech_ids or not query.strip():
            return []

        # Validate tech ids against registry
        valid_ids = [t for t in tech_ids if t in TECH_REGISTRY]
        unknown = set(tech_ids) - set(valid_ids)
        if unknown:
            logger.warning(f"Unknown tech IDs skipped: {unknown}")
        if not valid_ids:
            logger.error("No valid tech IDs to query.")
            return []

        k = top_k or self.top_k
        results = self.storage.query(
            tech_ids=valid_ids,
            query_text=query,
            n_results=k,
            filter_has_code=True if only_code else None,
        )

        # Attach tech_id to each result for downstream agents
        enriched = []
        for r in results:
            meta = r.get("metadata", {})
            enriched.append({
                "content": r["content"],
                "metadata": meta,
                "relevance_score": r["relevance_score"],
                "tech_id": meta.get("tech_id", "unknown"),
                "source_url": meta.get("source_url", ""),
                "has_code": meta.get("has_code", False),
            })

        logger.info(
            f"Retrieved {len(enriched)} chunks for techs={valid_ids} | query='{query[:60]}...'"
        )
        return enriched

    # ── Per-tech retrieve (for individual agents) ───────────────────────────

    def retrieve_for_tech(
        self,
        tech_id: str,
        query: str,
        top_k: Optional[int] = None,
    ) -> list[dict]:
        """
        Retrieve chunks for a single tech stack. Used by individual agents.
        """
        return self.retrieve([tech_id], query, top_k=top_k)

    # ── Utility ─────────────────────────────────────────────────────────────

    def get_available_techs(self) -> list[dict]:
        """
        Returns all tech stacks that have data in ChromaDB.
        """
        stats = self.storage.get_all_stats()
        available = [s for s in stats if s.get("chunk_count", 0) > 0]
        logger.info(f"{len(available)} tech collections populated in ChromaDB")
        return available

    def get_tech_stats(self, tech_id: str) -> dict:
        """Collection stats for a single tech."""
        return self.storage.get_collection_stats(tech_id)

    def format_context(self, chunks: list[dict], max_chars: int = 6000) -> str:
        """
        Format retrieved chunks into a clean context string for the LLM prompt.
        Respects a character budget to avoid overflowing context windows.
        """
        if not chunks:
            return "No relevant documentation found."

        parts = []
        total = 0
        for i, chunk in enumerate(chunks, 1):
            tech = chunk.get("tech_id", "unknown").upper()
            url = chunk.get("source_url", "")
            content = chunk.get("content", "").strip()
            block = f"[{i}] [{tech}] {url}\n{content}\n"
            if total + len(block) > max_chars:
                break
            parts.append(block)
            total += len(block)

        return "\n".join(parts)