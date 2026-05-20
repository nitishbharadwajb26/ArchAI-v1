"""NestJS specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class NestJSAgent(BaseTechAgent):
    TECH_ID = "nestjs"
    TECH_NAME = "NestJS"

    EXPERT_PERSONA = (
        "You are a senior NestJS architect who thinks in modules, providers, and "
        "decorators. You have a strong Angular/Spring background and value "
        "dependency injection, separation of concerns, and TypeScript-first design."
    )

    ARCHITECTURE_FOCUS = (
        "Modular architecture (one module per feature), DI-driven providers, "
        "TypeScript strict mode everywhere, decorators for routes/guards/interceptors, "
        "DTOs with class-validator, repository pattern with TypeORM/Prisma, "
        "microservice transport layer (gRPC/Kafka/RabbitMQ) when scaling out, "
        "GraphQL via @nestjs/graphql when client needs flexible queries."
    )

    STRENGTHS = [
        "Enterprise TypeScript backends with long-term maintenance needs",
        "Teams coming from Angular/Spring — patterns transfer directly",
        "GraphQL APIs with type-safe schemas",
        "Microservice systems with multiple transports (HTTP + gRPC + queue)",
        "Domain-driven design and clean architecture in TypeScript",
        "Apps with complex authorisation (Guards + RBAC)",
    ]

    WEAKNESSES = [
        "Tiny prototypes — boilerplate and ceremony aren't worth it (Express/Fastify better)",
        "Pure I/O-bound serverless functions where cold-starts matter",
        "Teams without TypeScript experience — steep learning curve",
        "Apps that need rapid iteration — DI/decorator overhead slows experiments",
    ]

    ANTI_PATTERNS = [
        "Putting business logic in controllers instead of services",
        "Skipping DTOs and class-validator on inputs — breaks type safety",
        "Manually instantiating services instead of using DI",
        "One giant AppModule instead of feature modules",
        "Mixing repositories and services — keep data access isolated",
    ]
