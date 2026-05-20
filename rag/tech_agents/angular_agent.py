"""Angular specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class AngularAgent(BaseTechAgent):
    TECH_ID = "angular"
    TECH_NAME = "Angular"

    EXPERT_PERSONA = (
        "You are a senior Angular architect comfortable with TypeScript, RxJS, "
        "the Angular DI system, and the modern signals API. You think in modules, "
        "components, services, and observables."
    )

    ARCHITECTURE_FOCUS = (
        "Standalone components (modern Angular 17+) over NgModules where possible, "
        "Angular signals for fine-grained reactivity, RxJS for streams of events, "
        "smart/dumb component split, services + DI for shared state, "
        "lazy-loaded routes for code-splitting, OnPush change detection for performance."
    )

    STRENGTHS = [
        "Large enterprise SPAs with multi-team development",
        "TypeScript-first teams that value strong opinions and a full framework",
        "Apps with complex async data flows (RxJS operators are powerful)",
        "Long-lived projects — Angular's stability and update story is excellent",
        "Apps that want batteries-included (router, forms, HTTP, i18n, testing)",
    ]

    WEAKNESSES = [
        "Tiny apps and prototypes — Angular's overhead is too much",
        "Teams unfamiliar with TypeScript or RxJS — steep learning curve",
        "Marketing/content sites (SSR is possible but React/Astro ecosystem bigger)",
        "Apps where bundle size is critical (React/Svelte typically smaller)",
    ]

    ANTI_PATTERNS = [
        "Subscribing to observables in components without unsubscribing — memory leaks",
        "Putting business logic in components instead of services",
        "Imperative state mutation instead of immutable patterns + OnPush",
        "Skipping RxJS in favour of nested promises — fights the framework",
        "One giant module instead of feature modules / standalone components",
    ]
