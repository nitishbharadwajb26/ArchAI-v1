"""LoopBack 4 specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class LoopBackAgent(BaseTechAgent):
    TECH_ID = "loopback"
    TECH_NAME = "LoopBack 4"

    EXPERT_PERSONA = (
        "You are a senior LoopBack 4 architect. You appreciate IBM/StrongLoop's "
        "model-driven approach, OpenAPI-first thinking, and the power of LoopBack's "
        "repository pattern for fast CRUD scaffolding."
    )

    ARCHITECTURE_FOCUS = (
        "Model-driven REST APIs, repository + datasource pattern, OpenAPI 3 spec "
        "generated from controllers, dependency injection via @inject, sequence-based "
        "request lifecycle, juggler ORM for connector flexibility, lb4 CLI for scaffolding."
    )

    STRENGTHS = [
        "REST APIs with many CRUD resources where model-driven scaffolding saves weeks",
        "OpenAPI/Swagger-first projects",
        "Apps that need to talk to many heterogeneous datasources (SQL, MongoDB, REST)",
        "TypeScript codebases that want repository pattern out of the box",
    ]

    WEAKNESSES = [
        "Smaller community vs NestJS/Express — fewer Stack Overflow answers",
        "Real-time/WebSocket apps (Express + Socket.IO is the standard)",
        "Tiny services where the LoopBack scaffolding is overkill",
        "Apps where GraphQL is preferred over REST",
    ]

    ANTI_PATTERNS = [
        "Bypassing repositories and querying datasources directly from controllers",
        "Custom auth instead of LoopBack's @authenticate decorator and Strategy pattern",
        "Skipping OpenAPI annotations and losing the auto-generated spec",
    ]
