"""
Agent Registry
───────────────
Maps tech_id → specialised agent class. Used by the orchestrator
to pick the right agent for each tech.
"""

from typing import Optional, Type
from base_agent import BaseTechAgent

AGENT_REGISTRY: dict[str, Type[BaseTechAgent]] = {}


def register_agent(cls: Type[BaseTechAgent]) -> Type[BaseTechAgent]:
    """Decorator to register an agent subclass by its TECH_ID."""
    if not cls.TECH_ID:
        raise ValueError(f"{cls.__name__} has no TECH_ID")
    AGENT_REGISTRY[cls.TECH_ID] = cls
    return cls


def get_agent_class(tech_id: str) -> Optional[Type[BaseTechAgent]]:
    """Return the registered agent class for a given tech_id, or None."""
    return AGENT_REGISTRY.get(tech_id)
