"""
RAG Chain
──────────
Main orchestrator for the RAG pipeline.

Flow:
    user query
        ↓
    Router            → which tech stacks are relevant?
        ↓
    AgentOrchestrator → run all relevant TechAgents concurrently
        ↓
    Synthesiser       → combine agent outputs into final recommendation
        ↓
    ArchitectureResponse (structured JSON)
"""

import sys
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ── Path bootstrap ──────────────────────────────────────────────────────────
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

RAG_PARENT = Path(__file__).resolve().parent.parent
if str(RAG_PARENT) not in sys.path:
    sys.path.insert(0, str(RAG_PARENT))

TECH_AGENTS_ROOT = RAG_ROOT / "tech_agents"
if str(TECH_AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TECH_AGENTS_ROOT))

# Verify scraper/config exists where we expect it
_expected_tech_registry = SCRAPER_ROOT / "config" / "tech_registry.py"
if not _expected_tech_registry.exists():
    raise ImportError(
        f"Cannot find tech_registry.py at expected path:\n"
        f"  {_expected_tech_registry}\n"
        f"Make sure your folder structure is:\n"
        f"  ArchAI/\n"
        f"  ├── rag/        (this folder)\n"
        f"  └── scraper/\n"
        f"      └── config/\n"
        f"          └── tech_registry.py\n"
        f"Resolved SCRAPER_ROOT = {SCRAPER_ROOT}\n"
        f"sys.path = {sys.path[:5]}"
    )

from config.provider_config import get_config, LLMProvider
from config.tech_registry import TECH_REGISTRY
from retriever import Retriever
from router import Router
from agents import AgentOrchestrator
from tech_agents.base_agent import AgentResult
from prompts import CHAIN_SYSTEM, CHAIN_USER, FALLBACK_SYSTEM, FALLBACK_USER

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Final Response Model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ArchitectureResponse:
    query: str
    routed_techs: list[str]
    summary: str
    recommended_stack: dict
    architecture_overview: str
    implementation_roadmap: list[dict]
    key_code_examples: list[dict]
    alternative_consideration: str
    sources: list[str]
    agent_details: list[dict]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "routed_techs": self.routed_techs,
            "summary": self.summary,
            "recommended_stack": self.recommended_stack,
            "architecture_overview": self.architecture_overview,
            "implementation_roadmap": self.implementation_roadmap,
            "key_code_examples": self.key_code_examples,
            "alternative_consideration": self.alternative_consideration,
            "sources": self.sources,
            "agent_details": self.agent_details,
            "error": self.error,
        }


# ─────────────────────────────────────────────────────────────────────────────
# RAG Chain
# ─────────────────────────────────────────────────────────────────────────────

class RAGChain:
    """Wires Router → AgentOrchestrator → Synthesiser."""

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        router: Optional[Router] = None,
        orchestrator: Optional[AgentOrchestrator] = None,
    ):
        self.cfg = get_config()
        self.retriever = retriever or Retriever()
        self.router = router or Router(
            available_tech_ids=self._get_populated_techs()
        )
        self.orchestrator = orchestrator or AgentOrchestrator(retriever=self.retriever)
        logger.info("RAGChain initialised")

    def run(self, query: str) -> ArchitectureResponse:
        """Run the full pipeline for a user query."""
        logger.info(f"RAGChain.run | query='{query[:80]}...'")

        # Step 1: Route
        tech_ids = self.router.route(query)
        logger.info(f"Routed to: {tech_ids}")

        if not tech_ids:
            return self._fallback_response(query, [])

        # Step 2: Run agents concurrently
        agent_results: list[AgentResult] = self.orchestrator.run(tech_ids, query)

        if not agent_results:
            return self._fallback_response(query, tech_ids)

        # Step 3: Synthesise
        return self._synthesise(query, tech_ids, agent_results)

    # ── Synthesis ─────────────────────────────────────────────────────────────

    def _synthesise(
        self,
        query: str,
        tech_ids: list[str],
        agent_results: list[AgentResult],
    ) -> ArchitectureResponse:
        """Combine all agent outputs into a final architectural recommendation."""

        agent_outputs_str = json.dumps(
            [r.to_dict() for r in agent_results],
            indent=2,
        )

        try:
            raw = self._call_llm(
                system=CHAIN_SYSTEM,
                user=CHAIN_USER.format(user_query=query, agent_outputs=agent_outputs_str),
            )
            synthesis = self._parse_synthesis(raw)
        except Exception as e:
            logger.error(f"Synthesis LLM failed: {e}. Falling back to manual synthesis.")
            synthesis = self._manual_synthesis(agent_results)

        # Collect all unique source URLs
        all_sources = []
        for r in agent_results:
            all_sources.extend(r.sources)
        all_sources = list(dict.fromkeys(all_sources))

        return ArchitectureResponse(
            query=query,
            routed_techs=tech_ids,
            summary=synthesis.get("summary", ""),
            recommended_stack=synthesis.get("recommended_stack", {}),
            architecture_overview=synthesis.get("architecture_overview", ""),
            implementation_roadmap=synthesis.get("implementation_roadmap", []),
            key_code_examples=synthesis.get("key_code_examples", []),
            alternative_consideration=synthesis.get("alternative_consideration", ""),
            sources=all_sources[:10],
            agent_details=[r.to_dict() for r in agent_results],
        )

    def _parse_synthesis(self, raw: str) -> dict:
        raw = re.sub(r"```(?:json)?", "", raw).strip("` \n")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON in synthesis response: {raw[:200]}")
        return json.loads(match.group())

    def _manual_synthesis(self, results: list[AgentResult]) -> dict:
        """Build a synthesis dict from agent results without calling the LLM."""
        recommended = [r for r in results if r.recommended] or results

        # Pick a backend and frontend based on tech_registry categories
        backend = None
        frontend = None
        additional = []
        for r in recommended:
            tech = TECH_REGISTRY.get(r.tech_id)
            if not tech:
                continue
            if tech.category == "backend" and not backend:
                backend = r.tech_id
            elif tech.category == "frontend" and not frontend:
                frontend = r.tech_id
            else:
                additional.append(r.tech_id)

        return {
            "summary": (
                f"Based on your requirements, the recommended stack includes: "
                f"{', '.join(r.tech_name for r in recommended)}."
            ),
            "recommended_stack": {
                "backend": backend,
                "frontend": frontend,
                "additional": additional,
            },
            "architecture_overview": " | ".join(
                r.architecture_notes for r in recommended if r.architecture_notes
            ),
            "implementation_roadmap": [
                {"phase": 1, "title": "Project Setup",
                 "tasks": ["Initialise project", "Install dependencies", "Configure environment"]},
                {"phase": 2, "title": "Core Development",
                 "tasks": ["Build core features", "Implement API layer", "Set up frontend"]},
                {"phase": 3, "title": "Testing & Deployment",
                 "tasks": ["Write tests", "Configure CI/CD", "Deploy"]},
            ],
            "key_code_examples": [
                {"tech": r.tech_id, "title": f"{r.tech_name} example", "code": r.code_example}
                for r in recommended if r.code_example
            ],
            "alternative_consideration": "",
        }

    # ── LLM call ─────────────────────────────────────────────────────────────

    def _call_llm(self, system: str, user: str, max_tokens: int = 2000) -> str:
        provider = self.cfg.agent_provider

        if provider == LLMProvider.OLLAMA:
            import requests
            payload = {
                "model": self.cfg.agent_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.4},
            }
            resp = requests.post(
                f"{self.cfg.ollama_base_url}/api/chat",
                json=payload,
                timeout=self.cfg.synthesis_timeout,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

        elif provider == LLMProvider.GROQ:
            from groq import Groq
            if not self.cfg.groq_api_key:
                raise ValueError("GROQ_API_KEY not set in .env")
            client = Groq(api_key=self.cfg.groq_api_key)
            resp = client.chat.completions.create(
                model=self.cfg.agent_model.replace("groq/", ""),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
                max_tokens=max_tokens,
                timeout=self.cfg.synthesis_timeout,
            )
            return resp.choices[0].message.content

        elif provider == LLMProvider.OPENAI:
            from openai import OpenAI
            if not self.cfg.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in .env")
            client = OpenAI(api_key=self.cfg.openai_api_key)
            resp = client.chat.completions.create(
                model=self.cfg.agent_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content

        raise ValueError(f"Unknown provider: {provider}")

    # ── Fallback when no chunks / no routing ─────────────────────────────────

    def _fallback_response(self, query: str, tech_ids: list[str]) -> ArchitectureResponse:
        logger.warning("Falling back to general LLM response (no ChromaDB results)")
        try:
            raw = self._call_llm(FALLBACK_SYSTEM, FALLBACK_USER.format(user_query=query))
            summary = raw.strip()
        except Exception as e:
            summary = f"Unable to generate a response: {e}"

        return ArchitectureResponse(
            query=query,
            routed_techs=tech_ids,
            summary=summary,
            recommended_stack={},
            architecture_overview="",
            implementation_roadmap=[],
            key_code_examples=[],
            alternative_consideration="",
            sources=[],
            agent_details=[],
            error="No relevant documentation found in ChromaDB. Responded from general knowledge.",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_populated_techs(self) -> list[str]:
        """Only route to tech collections that actually have data."""
        stats = self.retriever.get_available_techs()
        ids = [s["tech_id"] for s in stats]
        logger.info(f"Populated collections: {ids}")
        return ids if ids else list(TECH_REGISTRY.keys())
