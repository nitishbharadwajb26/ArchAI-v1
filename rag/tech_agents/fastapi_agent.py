"""FastAPI specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class FastAPIAgent(BaseTechAgent):
    TECH_ID = "fastapi"
    TECH_NAME = "FastAPI"

    EXPERT_PERSONA = (
        "You are a senior FastAPI architect with deep expertise in async Python, "
        "Pydantic v2, dependency injection, and high-performance API design. "
        "You think in terms of type hints, request lifecycle, and OpenAPI-first APIs."
    )

    ARCHITECTURE_FOCUS = (
        "Async-first design (async def routes), Pydantic models for validation, "
        "dependency injection via Depends(), proper APIRouter structure, "
        "middleware composition, BackgroundTasks for fire-and-forget work, "
        "clean separation of routers/services/repositories, and OpenAPI-first thinking."
    )

    STRENGTHS = [
        "High-throughput REST APIs and microservices",
        "ML model serving (low-latency inference)",
        "Real-time/WebSocket APIs requiring async I/O",
        "API-first projects where auto-generated OpenAPI docs are valuable",
        "Type-safe Python codebases",
        "Async database access (SQLAlchemy 2.0 + asyncpg, Tortoise, Motor)",
    ]

    WEAKNESSES = [
        "Server-rendered websites with traditional templating (Django/Flask better)",
        "CMS-style apps that need an admin panel out of the box (Django better)",
        "Tiny scripts where Pydantic overhead isn't justified (Flask better)",
        "Teams unfamiliar with async/await — concurrency bugs are easy to introduce",
    ]

    ANTI_PATTERNS = [
        "Using sync def for I/O-bound routes — defeats async performance",
        "Calling synchronous DB drivers (psycopg2) from async routes — blocks the event loop",
        "Skipping Pydantic models — loses validation and OpenAPI schema benefits",
        "Putting business logic inside route handlers instead of services",
    ]
