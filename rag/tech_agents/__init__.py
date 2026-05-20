"""
Specialised tech agents — one expert agent per tech stack.

The agent files use bare imports (e.g. `from base_agent import ...`).
This __init__.py ensures the tech_agents folder is on sys.path and
explicitly imports each agent file, populating the registry.

Use:
    from tech_agents import AGENT_REGISTRY, get_agent_class
"""

import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

# Import base + registry
import base_agent  # noqa: F401
import registry    # noqa: F401
from base_agent import BaseTechAgent, AgentResult
from registry import AGENT_REGISTRY, get_agent_class, register_agent

# Import every specialised agent module — the @register_agent decorator
# populates registry.AGENT_REGISTRY as a side-effect.
import fastapi_agent      # noqa: F401
import django_agent       # noqa: F401
import flask_agent        # noqa: F401
import nodejs_agent       # noqa: F401
import nestjs_agent       # noqa: F401
import loopback_agent     # noqa: F401
import react_agent        # noqa: F401
import angular_agent      # noqa: F401
import dotnet_core_agent  # noqa: F401
import dotnet_mvc_agent   # noqa: F401
import blazor_agent       # noqa: F401

__all__ = [
    "BaseTechAgent",
    "AgentResult",
    "AGENT_REGISTRY",
    "get_agent_class",
    "register_agent",
]
