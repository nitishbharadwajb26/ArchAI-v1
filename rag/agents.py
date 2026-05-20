"""
Agent Orchestrator
───────────────────
Uses the registry of specialised agents (one per tech) where available,
and falls back to a generic agent for techs without a dedicated class.

Each tech_id resolves to its specialist agent (FastAPIAgent, DjangoAgent,
NodeJSAgent, etc.) which has a tailored persona, strengths/weaknesses,
and anti-patterns built into its system prompt.

Agents run concurrently using ThreadPoolExecutor for speed.
"""

import sys
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

# Path bootstrap
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

TECH_AGENTS_ROOT = RAG_ROOT / "tech_agents"
if str(TECH_AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TECH_AGENTS_ROOT))

from config.tech_registry import TECH_REGISTRY
from retriever import Retriever

# Import the specialised agents — this populates AGENT_REGISTRY via decorators
import tech_agents  # noqa: F401  (side-effect: registers all agent classes)
from tech_agents.base_agent import BaseTechAgent, AgentResult
from tech_agents.registry import AGENT_REGISTRY, get_agent_class

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Generic fallback agent (used when no specialised class exists for a tech)
# ─────────────────────────────────────────────────────────────────────────────

class GenericTechAgent(BaseTechAgent):
    """Catch-all agent — used if no specialised class is registered for a tech_id."""

    def __init__(self, tech_id: str, retriever: Retriever):
        # Bypass class-attribute checks by setting per-instance
        self.TECH_ID = tech_id
        from config.tech_registry import TECH_REGISTRY
        tech = TECH_REGISTRY.get(tech_id)
        if not tech:
            raise ValueError(f"Unknown tech_id: {tech_id}")
        self.TECH_NAME = tech.name
        self.EXPERT_PERSONA = (
            f"You are a senior {tech.name} architect with deep expertise in "
            f"{tech.language} and the {tech.category} space."
        )
        self.ARCHITECTURE_FOCUS = (
            f"Modern {tech.name} patterns and best practices."
        )
        self.STRENGTHS = [f"Use {tech.name} when it fits the requirement"]
        self.WEAKNESSES = ["Recommend a different tech if the requirement is a poor fit"]
        self.ANTI_PATTERNS = ["Avoid common {tech.name} pitfalls"]

        super().__init__(retriever)


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class AgentOrchestrator:
    """Spawns the right specialised agent per tech and runs them concurrently."""

    def __init__(self, retriever: Optional[Retriever] = None, max_workers: int = 4):
        self.retriever = retriever or Retriever()
        self.max_workers = max_workers
        registered = sorted(AGENT_REGISTRY.keys())
        logger.info(
            f"AgentOrchestrator initialised | max_workers={max_workers} | "
            f"specialised agents: {registered}"
        )

    def _make_agent(self, tech_id: str) -> BaseTechAgent:
        """Return the specialised agent for tech_id, or a generic fallback."""
        cls = get_agent_class(tech_id)
        if cls is not None:
            return cls(self.retriever)
        logger.warning(
            f"[{tech_id}] No specialised agent registered — using GenericTechAgent"
        )
        return GenericTechAgent(tech_id, self.retriever)

    def run(self, tech_ids: list[str], query: str) -> list[AgentResult]:
        if not tech_ids:
            return []

        valid_ids = [t for t in tech_ids if t in TECH_REGISTRY]
        if not valid_ids:
            logger.error(f"No valid tech IDs: {tech_ids}")
            return []

        results: list[AgentResult] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_tech = {}
            for tid in valid_ids:
                try:
                    agent = self._make_agent(tid)
                    future_to_tech[executor.submit(agent.run, query)] = tid
                except Exception as e:
                    logger.error(f"[{tid}] Failed to construct agent: {e}")

            for future in as_completed(future_to_tech):
                tid = future_to_tech[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(
                        f"[{tid}] {result.__class__.__name__} done | "
                        f"recommended={result.recommended} | "
                        f"confidence={result.confidence:.2f}"
                    )
                except Exception as e:
                    logger.error(f"[{tid}] Agent exception: {e}")

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
