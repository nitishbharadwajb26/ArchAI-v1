"""Django specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class DjangoAgent(BaseTechAgent):
    TECH_ID = "django"
    TECH_NAME = "Django"

    EXPERT_PERSONA = (
        "You are a senior Django architect with deep expertise in Django ORM, "
        "the MTV pattern, the admin site, and Django's batteries-included philosophy. "
        "You think in apps, models, signals, and migrations."
    )

    ARCHITECTURE_FOCUS = (
        "App-based modular architecture, ORM-first data modelling with proper migrations, "
        "class-based views (CBVs) over function views for reusability, Django REST Framework "
        "for API surfaces, the admin site as a productivity multiplier, signals for "
        "decoupled side-effects, custom managers/querysets for query logic."
    )

    STRENGTHS = [
        "Content-heavy applications, CMS-like sites, internal tools",
        "Apps where the admin site delivers real value out of the box",
        "Complex relational data models with many-to-many/foreign-key chains",
        "Teams that want batteries-included (auth, sessions, forms, ORM) on day 1",
        "Rapid prototyping with rock-solid security defaults",
        "Django REST Framework for traditional REST APIs",
    ]

    WEAKNESSES = [
        "High-concurrency async APIs (FastAPI better — Django async still maturing)",
        "Microservices where the full Django stack is overkill (Flask/FastAPI better)",
        "Real-time/WebSocket-heavy apps (need Channels — adds complexity)",
        "ML model serving (FastAPI better — built for this)",
    ]

    ANTI_PATTERNS = [
        "N+1 queries — not using select_related / prefetch_related on FK lookups",
        "Business logic in views or templates instead of model methods or services",
        "Skipping migrations and editing the schema manually",
        "Putting heavy work in request/response cycle instead of Celery tasks",
        "One giant 'project' app instead of many focused apps",
    ]
