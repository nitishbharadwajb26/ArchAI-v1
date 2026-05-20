"""Flask specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class FlaskAgent(BaseTechAgent):
    TECH_ID = "flask"
    TECH_NAME = "Flask"

    EXPERT_PERSONA = (
        "You are a senior Flask architect who values simplicity, explicitness, and "
        "the 'micro' philosophy: ship only what you need. You think in blueprints, "
        "extensions, and minimal app factory patterns."
    )

    ARCHITECTURE_FOCUS = (
        "Application factory pattern, blueprints for modular routing, judicious choice "
        "of extensions (Flask-SQLAlchemy, Flask-Migrate, Flask-Login), explicit "
        "configuration over magic, WSGI-first thinking. Avoid over-engineering."
    )

    STRENGTHS = [
        "Small-to-medium services and microservices where Django is overkill",
        "Internal tools and dashboards (Flask + Jinja2 is unbeatable for quick UIs)",
        "Quick prototypes and MVPs",
        "Webhooks, integrations, lightweight glue services",
        "When you want fine-grained control over every dependency",
    ]

    WEAKNESSES = [
        "Large monolithic apps (Django's batteries save tons of work)",
        "High-concurrency async APIs (FastAPI better — Flask sync model dominates)",
        "ML model serving with auto OpenAPI docs (FastAPI better)",
        "Apps that need a built-in admin (Django wins by miles)",
    ]

    ANTI_PATTERNS = [
        "Single-file app for anything beyond a tiny prototype — use blueprints",
        "Globals everywhere instead of the application factory pattern",
        "Skipping a request-scoped DB session — leads to leaks and bad concurrency",
        "Reinventing what Flask-* extensions already provide",
    ]
