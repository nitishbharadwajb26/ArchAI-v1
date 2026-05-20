"""ASP.NET Core MVC specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class DotNetMVCAgent(BaseTechAgent):
    TECH_ID = "dotnet_mvc"
    TECH_NAME = "ASP.NET Core MVC"

    EXPERT_PERSONA = (
        "You are a senior ASP.NET Core MVC architect who values server-rendered pages, "
        "Razor view composition, and tag helpers. You're equally comfortable with "
        "Razor Pages for page-centric apps and full MVC for controller-driven apps."
    )

    ARCHITECTURE_FOCUS = (
        "Razor Pages for page-centric flows; full MVC (Controllers + Views) when actions "
        "span multiple resources. Tag Helpers for clean Razor markup, ViewModels separating "
        "domain models from view shape, view components for reusable widgets, "
        "anti-forgery tokens for forms, partial views for composition, model binding "
        "with validation attributes, server-side rendering with progressive enhancement."
    )

    STRENGTHS = [
        "Server-rendered web apps with traditional CRUD flows",
        "Internal/enterprise apps in Microsoft shops",
        "SEO-friendly content sites that need server rendering",
        "Teams that prefer not to maintain a separate JS frontend",
        "Apps with complex forms — Razor + model binding is hard to beat",
    ]

    WEAKNESSES = [
        "Highly interactive UIs (use a SPA: React/Angular/Blazor instead)",
        "Pure REST APIs (use ASP.NET Core Web API / Minimal APIs)",
        "Mobile apps that need to share UI logic with web",
        "Apps where the team prefers component-based UI over page-based",
    ]

    ANTI_PATTERNS = [
        "Passing domain entities directly to views instead of ViewModels",
        "Putting business logic in controllers or, worse, in views",
        "Skipping anti-forgery tokens on POST forms",
        "Doing server-side rendering of huge tables that should be virtualised on the client",
        "Mixing MVC and Razor Pages randomly — pick a primary pattern",
    ]
