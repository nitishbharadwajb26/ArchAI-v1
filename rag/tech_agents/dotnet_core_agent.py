""".NET Core / ASP.NET Core specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class DotNetCoreAgent(BaseTechAgent):
    TECH_ID = "dotnet_core"
    TECH_NAME = ".NET Core / ASP.NET Core"

    EXPERT_PERSONA = (
        "You are a senior .NET Core / ASP.NET Core architect with deep expertise in "
        "Minimal APIs, MediatR/CQRS, Entity Framework Core, and dependency injection. "
        "You think in middlewares, DI containers, and clean architecture layers."
    )

    ARCHITECTURE_FOCUS = (
        "Minimal APIs for lightweight microservices OR controller-based APIs for larger projects, "
        "Clean Architecture (Domain / Application / Infrastructure / Presentation layers), "
        "MediatR for CQRS where command/query separation is helpful, EF Core with proper "
        "tracking/no-tracking decisions, built-in DI container, FluentValidation, "
        "OpenAPI via Swashbuckle/NSwag, IOptions pattern for configuration."
    )

    STRENGTHS = [
        "High-performance enterprise APIs and microservices",
        "Teams already in the Microsoft ecosystem (Azure, SQL Server, Active Directory)",
        "CPU-bound and concurrent workloads (.NET threading is excellent)",
        "Long-lived enterprise apps with strong typing and refactoring stories",
        "Cross-platform deployment (Linux containers, Windows, macOS)",
        "Real-time apps via SignalR",
    ]

    WEAKNESSES = [
        "Quick prototypes and tiny scripts (Python/Node faster to start)",
        "Teams without C#/Java background — onboarding cost is real",
        "Apps that need a server-rendered admin out of the box (Django wins)",
        "Hosting on lowest-cost shared hosts (Node/PHP often easier to deploy)",
    ]

    ANTI_PATTERNS = [
        "Async-over-sync (.GetAwaiter().GetResult()) — kills throughput, can deadlock",
        "Long-lived DbContext as singleton — should be scoped per request",
        "Skipping AsNoTracking() on read-only queries — wasteful change-tracking",
        "Manual JSON parsing instead of using model binding + validation",
        "Putting business logic in controllers instead of MediatR handlers / services",
    ]
