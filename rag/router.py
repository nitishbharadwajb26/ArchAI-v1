"""
RAG Router
───────────
Analyses the user's prompt and decides which tech stacks are relevant.
Uses llama3.1:8b (via Ollama) or falls back to Groq/OpenAI.

Flow:
    user query → LLM classification → list of tech_ids
    e.g. "build a REST API with Python" → ["fastapi"]
    e.g. "full stack dashboard"         → ["nestjs", "react"]
"""

import sys
import json
import logging
import re
from pathlib import Path
from typing import Optional

# ── Path bootstrap ──────────────────────────────────────────────────────────
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

from config.tech_registry import TECH_REGISTRY
from config.provider_config import get_config, LLMProvider
from prompts import ROUTER_SYSTEM, ROUTER_USER

logger = logging.getLogger(__name__)


class Router:
    """
    Classifies a user query into relevant tech stack IDs.
    """

    def __init__(self, available_tech_ids: Optional[list[str]] = None):
        """
        Args:
            available_tech_ids: Restrict routing to only these techs.
                                Defaults to all techs in TECH_REGISTRY.
        """
        self.cfg = get_config()
        self.available_ids = available_tech_ids or list(TECH_REGISTRY.keys())
        self._tech_description = self._build_tech_description()
        logger.info(f"Router initialised | techs={self.available_ids}")

    # ── Public ───────────────────────────────────────────────────────────────

    def route(self, query: str) -> list[str]:
        """
        Classify the query and return relevant tech IDs.

        Args:
            query: User's natural language project description

        Returns:
            List of tech_ids e.g. ["fastapi", "react"]
            Falls back to keyword matching if LLM call fails.
        """
        if not query.strip():
            return []

        try:
            raw = self._call_llm(query)
            tech_ids = self._parse_response(raw)
            if tech_ids:
                logger.info(f"Router → {tech_ids}")
                return tech_ids
        except Exception as e:
            logger.warning(f"LLM routing failed ({e}), falling back to keyword match")

        # Fallback: keyword-based matching
        return self._keyword_fallback(query)

    # ── LLM call ─────────────────────────────────────────────────────────────

    def _call_llm(self, query: str) -> str:
        provider = self.cfg.router_provider

        system_prompt = ROUTER_SYSTEM.format(available_techs=self._tech_description)
        user_prompt = ROUTER_USER.format(user_query=query)

        if provider == LLMProvider.OLLAMA:
            return self._call_ollama(system_prompt, user_prompt)
        elif provider == LLMProvider.GROQ:
            return self._call_groq(system_prompt, user_prompt)
        elif provider == LLMProvider.OPENAI:
            return self._call_openai(system_prompt, user_prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def _call_ollama(self, system: str, user: str) -> str:
        import requests
        payload = {
            "model": self.cfg.router_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0.1},  # Low temp for deterministic routing
        }
        resp = requests.post(
            f"{self.cfg.ollama_base_url}/api/chat",
            json=payload,
            timeout=self.cfg.router_timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _call_groq(self, system: str, user: str) -> str:
        from groq import Groq
        if not self.cfg.groq_api_key:
            raise ValueError("GROQ_API_KEY not set in .env")
        client = Groq(api_key=self.cfg.groq_api_key)
        resp = client.chat.completions.create(
            model=self.cfg.router_model.replace("groq/", ""),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=200,
            timeout=self.cfg.router_timeout,
        )
        return resp.choices[0].message.content

    def _call_openai(self, system: str, user: str) -> str:
        from openai import OpenAI
        if not self.cfg.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        client = OpenAI(api_key=self.cfg.openai_api_key)
        resp = client.chat.completions.create(
            model=self.cfg.router_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.1,
            max_tokens=200,
        )
        return resp.choices[0].message.content

    # ── Response parsing ──────────────────────────────────────────────────────

    def _parse_response(self, raw: str) -> list[str]:
        """Extract JSON array from LLM response and validate tech IDs."""
        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Find array pattern
        match = re.search(r"\[.*?\]", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON array found in: {raw}")

        parsed = json.loads(match.group())
        valid = [t for t in parsed if t in self.available_ids]

        if not valid:
            raise ValueError(f"No valid tech IDs in parsed list: {parsed}")

        return valid

    # ── Keyword fallback ─────────────────────────────────────────────────────

    def _keyword_fallback(self, query: str) -> list[str]:
        """Simple keyword matching as a last resort."""
        query_lower = query.lower()
        matched = []

        keyword_map = {
            "fastapi": ["fastapi", "fast api"],
            "django": ["django"],
            "flask": ["flask"],
            "nodejs": ["node.js", "nodejs", "node js", "express"],
            "nestjs": ["nestjs", "nest.js", "nest js"],
            "loopback": ["loopback", "loop back"],
            "react": ["react", "reactjs", "react.js"],
            "angular": ["angular"],
            "dotnet_core": ["asp.net", "dotnet", ".net core", "aspnet"],
            "dotnet_mvc": ["mvc", "razor", "asp.net mvc"],
            "blazor": ["blazor"],
        }

        for tech_id, keywords in keyword_map.items():
            if tech_id in self.available_ids:
                if any(kw in query_lower for kw in keywords):
                    matched.append(tech_id)

        # Generic fallback heuristics
        if not matched:
            if any(w in query_lower for w in ["python", "api", "backend", "rest"]):
                matched.append("fastapi")
            if any(w in query_lower for w in ["frontend", "ui", "dashboard", "web app"]):
                matched.append("react")

        logger.info(f"Keyword fallback → {matched}")
        return matched[:4]  # Cap at 4

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_tech_description(self) -> str:
        """Build a human-readable list of available techs for the system prompt."""
        lines = []
        for tid in self.available_ids:
            tech = TECH_REGISTRY.get(tid)
            if tech:
                lines.append(
                    f"  - {tid}: {tech.name} ({tech.language}, {tech.category})"
                )
        return "\n".join(lines)