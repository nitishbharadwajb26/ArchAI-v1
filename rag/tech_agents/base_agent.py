"""
Base Tech Agent
────────────────
Shared logic for all specialised tech agents:
  - LLM provider routing (Ollama / Groq / OpenAI)
  - Retrieval and context formatting
  - JSON response parsing
  - Error handling

Subclasses only need to define:
  TECH_ID, TECH_NAME, EXPERT_PERSONA, ARCHITECTURE_FOCUS,
  STRENGTHS, WEAKNESSES, ANTI_PATTERNS
"""

import sys
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Path bootstrap
SCRAPER_ROOT = Path(__file__).resolve().parent.parent.parent / "scraper"
if str(SCRAPER_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent.parent
if str(RAG_ROOT) not in sys.path:
    sys.path.insert(0, str(RAG_ROOT))

from config.tech_registry import TECH_REGISTRY
from config.provider_config import get_config, LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    tech_id: str
    tech_name: str
    recommended: bool
    confidence: float
    reason: str
    architecture_notes: str
    pros: list[str]
    cons: list[str]
    code_example: str
    sources: list[str]
    raw_chunks: list[dict]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "tech_id": self.tech_id,
            "tech_name": self.tech_name,
            "recommended": self.recommended,
            "confidence": self.confidence,
            "reason": self.reason,
            "architecture_notes": self.architecture_notes,
            "pros": self.pros,
            "cons": self.cons,
            "code_example": self.code_example,
            "sources": self.sources,
            "error": self.error,
        }


class BaseTechAgent:
    """
    Base class for all tech-specific agents.

    Subclasses must override these class attributes:
      TECH_ID            : str — registry key e.g. "fastapi"
      TECH_NAME          : str — display name e.g. "FastAPI"
      EXPERT_PERSONA     : str — opening line of the system prompt
      ARCHITECTURE_FOCUS : str — what this expert prioritises
      STRENGTHS          : list[str] — when this tech shines
      WEAKNESSES         : list[str] — when this tech is wrong choice
      ANTI_PATTERNS      : list[str] — common mistakes to flag
    """

    # Subclass overrides
    TECH_ID: str = ""
    TECH_NAME: str = ""
    EXPERT_PERSONA: str = ""
    ARCHITECTURE_FOCUS: str = ""
    STRENGTHS: list[str] = []
    WEAKNESSES: list[str] = []
    ANTI_PATTERNS: list[str] = []

    def __init__(self, retriever):
        if not self.TECH_ID:
            raise ValueError(f"{self.__class__.__name__} must define TECH_ID")
        self.retriever = retriever
        self.cfg = get_config()
        self.tech = TECH_REGISTRY.get(self.TECH_ID)
        if not self.tech:
            raise ValueError(f"TECH_ID '{self.TECH_ID}' not in TECH_REGISTRY")

    # ── Main entry point ─────────────────────────────────────────────────────

    def run(self, query: str) -> AgentResult:
        """Run the full retrieve → prompt → parse cycle."""
        chunks = self.retriever.retrieve_for_tech(self.TECH_ID, query, top_k=6)
        context = self.retriever.format_context(chunks, max_chars=4000)

        try:
            raw = self._call_llm(query, context)
            return self._parse_response(raw, chunks)
        except Exception as e:
            logger.error(f"[{self.TECH_ID}] Agent failed: {e}")
            return self._error_result(str(e), chunks)

    # ── Prompt construction (uses subclass attributes) ───────────────────────

    def _build_system_prompt(self) -> str:
        strengths = "\n".join(f"  - {s}" for s in self.STRENGTHS)
        weaknesses = "\n".join(f"  - {w}" for w in self.WEAKNESSES)
        anti_patterns = "\n".join(f"  - {ap}" for ap in self.ANTI_PATTERNS)

        return f"""{self.EXPERT_PERSONA}

YOUR ARCHITECTURAL FOCUS:
{self.ARCHITECTURE_FOCUS}

WHEN {self.TECH_NAME} IS THE RIGHT CHOICE:
{strengths}

WHEN TO RECOMMEND AGAINST {self.TECH_NAME}:
{weaknesses}

ANTI-PATTERNS TO FLAG:
{anti_patterns}

TASK:
Given a user requirement and {self.TECH_NAME} documentation excerpts, decide whether {self.TECH_NAME} is the right tool for THIS specific job. Be honest. If it's a poor fit, set "recommended": false and explain why with confidence < 0.4.

OUTPUT (valid JSON only — no markdown, no preamble):
{{
  "tech_id": "{self.TECH_ID}",
  "tech_name": "{self.TECH_NAME}",
  "recommended": true | false,
  "confidence": 0.0-1.0,
  "reason": "Concrete 2-3 sentence justification specific to THIS user's requirement",
  "architecture_notes": "Specific architectural decisions and patterns FOR THIS use case using {self.TECH_NAME}",
  "pros": ["advantage specific to this use case", ...],
  "cons": ["honest trade-off for this use case", ...],
  "code_example": "Idiomatic {self.TECH_NAME} code for the most important pattern in this use case",
  "sources": ["url1", "url2"]
}}"""

    def _build_user_prompt(self, query: str, context: str) -> str:
        return f"""USER REQUIREMENT:
{query}

RELEVANT {self.TECH_NAME.upper()} DOCUMENTATION:
{context}

Provide your specialist recommendation as a JSON object."""

    # ── LLM call ─────────────────────────────────────────────────────────────

    def _call_llm(self, query: str, context: str) -> str:
        system = self._build_system_prompt()
        user = self._build_user_prompt(query, context)

        provider = self.cfg.agent_provider
        if provider == LLMProvider.OLLAMA:
            return self._call_ollama(system, user)
        elif provider == LLMProvider.GROQ:
            return self._call_groq(system, user)
        elif provider == LLMProvider.OPENAI:
            return self._call_openai(system, user)
        raise ValueError(f"Unknown provider: {provider}")

    def _call_ollama(self, system: str, user: str) -> str:
        import requests
        payload = {
            "model": self.cfg.agent_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": 0.3},
        }
        resp = requests.post(
            f"{self.cfg.ollama_base_url}/api/chat",
            json=payload,
            timeout=self.cfg.agent_timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _call_groq(self, system: str, user: str) -> str:
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
            temperature=0.3,
            max_tokens=1500,
            timeout=self.cfg.agent_timeout,
        )
        return resp.choices[0].message.content

    def _call_openai(self, system: str, user: str) -> str:
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
            temperature=0.3,
            max_tokens=1500,
        )
        return resp.choices[0].message.content

    # ── Response parsing ──────────────────────────────────────────────────────

    def _parse_response(self, raw: str, chunks: list[dict]) -> AgentResult:
        raw = re.sub(r"```(?:json)?", "", raw).strip("` \n")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise ValueError(f"No JSON object in response: {raw[:200]}")

        data = json.loads(match.group())
        chunk_sources = list({c.get("source_url", "") for c in chunks if c.get("source_url")})

        return AgentResult(
            tech_id=self.TECH_ID,
            tech_name=self.TECH_NAME,
            recommended=data.get("recommended", True),
            confidence=float(data.get("confidence", 0.7)),
            reason=data.get("reason", ""),
            architecture_notes=data.get("architecture_notes", ""),
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            code_example=data.get("code_example", ""),
            sources=data.get("sources", chunk_sources) or chunk_sources,
            raw_chunks=chunks,
        )

    def _error_result(self, error: str, chunks: list[dict]) -> AgentResult:
        chunk_sources = list({c.get("source_url", "") for c in chunks if c.get("source_url")})
        return AgentResult(
            tech_id=self.TECH_ID,
            tech_name=self.TECH_NAME,
            recommended=False,
            confidence=0.0,
            reason=f"Agent failed to generate a response: {error}",
            architecture_notes="",
            pros=[],
            cons=[],
            code_example="",
            sources=chunk_sources,
            raw_chunks=chunks,
            error=error,
        )
