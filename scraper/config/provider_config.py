"""
Provider Configuration
───────────────────────
Single place to configure ALL AI providers.

Default profile: "groq_free" — uses Groq's free API for LLM (fast, no
local RAM needed) and keeps embeddings local. Best choice for 16GB RAM
machines where running an 8B local model is too slow.

To switch profile:
    Windows : set ARCHITECTAI_PROFILE=academic_local
    Linux   : export ARCHITECTAI_PROFILE=academic_local
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root, scraper/, and rag/ — covers all run locations
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
for env_path in [
    _PROJECT_ROOT / ".env",
    _PROJECT_ROOT / "scraper" / ".env",
    _PROJECT_ROOT / "rag" / ".env",
]:
    if env_path.exists():
        load_dotenv(env_path, override=False)


class LLMProvider(str, Enum):
    OLLAMA = "ollama"
    GROQ = "groq"
    OPENAI = "openai"


class EmbeddingProvider(str, Enum):
    OLLAMA = "ollama"
    SENTENCE_TRANSFORMERS = "st"
    OPENAI = "openai"


# ─────────────────────────────────────────────────────────────────────────────
# Active Configuration
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ProviderConfig:
    """Active provider configuration."""

    # ── LLM Settings ─────────────────────────────────────────────────────────
    router_model: str = "groq/llama-3.1-8b-instant"
    router_provider: LLMProvider = LLMProvider.GROQ

    agent_model: str = "groq/llama-3.3-70b-versatile"
    agent_provider: LLMProvider = LLMProvider.GROQ

    ollama_base_url: str = "http://localhost:11434"

    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))

    # ── Embedding Settings ────────────────────────────────────────────────────
    embedding_model: str = "nomic-embed-text"
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OLLAMA

    # Auto-fallback if Ollama not reachable
    embedding_fallback_model: str = "BAAI/bge-small-en-v1.5"
    embedding_fallback_provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS

    # ── Extractor Settings ────────────────────────────────────────────────────
    use_trafilatura: bool = True
    use_markdownify: bool = True

    # ── ChromaDB Settings ────────────────────────────────────────────────────
    chroma_persist_dir: str = "./data/chromadb"

    # ── Generation Settings ───────────────────────────────────────────────────
    temperature: float = 0.2
    max_tokens: int = 2048
    top_p: float = 0.9

    # ── Request timeouts (seconds) ───────────────────────────────────────────
    router_timeout: int = 30
    agent_timeout: int = 90
    synthesis_timeout: int = 120

    def is_fully_local(self) -> bool:
        return (
            self.agent_provider == LLMProvider.OLLAMA
            and self.router_provider == LLMProvider.OLLAMA
            and self.embedding_provider == EmbeddingProvider.OLLAMA
        )

    def summary(self) -> str:
        return "\n".join([
            "─── ArchAI Provider Config ────────────────────────",
            f"  Router LLM  : {self.router_model} ({self.router_provider.value})",
            f"  Agent LLM   : {self.agent_model} ({self.agent_provider.value})",
            f"  Embeddings  : {self.embedding_model} ({self.embedding_provider.value})",
            f"  Fully local : {'Yes' if self.is_fully_local() else 'No (uses external API)'}",
            "───────────────────────────────────────────────────",
        ])


# ─────────────────────────────────────────────────────────────────────────────
# PRESET PROFILES
# ─────────────────────────────────────────────────────────────────────────────

PROFILES = {
    # DEFAULT — Groq free API (current 2026 models). Fast, reliable.
    # Embeddings stay local with nomic-embed-text via Ollama.
    "groq_free": ProviderConfig(
        router_model="groq/llama-3.1-8b-instant",
        router_provider=LLMProvider.GROQ,
        agent_model="groq/llama-3.3-70b-versatile",
        agent_provider=LLMProvider.GROQ,
        embedding_model="nomic-embed-text",
        embedding_provider=EmbeddingProvider.OLLAMA,
    ),

    # 16GB RAM, fully local — slow (1-3 min/query) but $0 and offline
    "academic_local": ProviderConfig(
        router_model="llama3.1:8b",
        router_provider=LLMProvider.OLLAMA,
        agent_model="llama3.1:8b",
        agent_provider=LLMProvider.OLLAMA,
        embedding_model="nomic-embed-text",
        embedding_provider=EmbeddingProvider.OLLAMA,
    ),

    # 8GB RAM machines
    "low_ram": ProviderConfig(
        router_model="llama3.2:3b",
        router_provider=LLMProvider.OLLAMA,
        agent_model="llama3.2:3b",
        agent_provider=LLMProvider.OLLAMA,
        embedding_model="all-MiniLM-L6-v2",
        embedding_provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
    ),

    # Best quality, paid
    "production": ProviderConfig(
        router_model="gpt-4o-mini",
        router_provider=LLMProvider.OPENAI,
        agent_model="gpt-4o",
        agent_provider=LLMProvider.OPENAI,
        embedding_model="text-embedding-3-small",
        embedding_provider=EmbeddingProvider.OPENAI,
    ),
}


def get_config(profile: str = "groq_free") -> ProviderConfig:
    """Get a config profile. Reads ARCHITECTAI_PROFILE env var if set."""
    profile = os.getenv("ARCHITECTAI_PROFILE", profile)
    if profile not in PROFILES:
        raise ValueError(
            f"Unknown profile '{profile}'. Choose from: {list(PROFILES.keys())}"
        )
    return PROFILES[profile]


# Singleton — import this everywhere
config = get_config()
