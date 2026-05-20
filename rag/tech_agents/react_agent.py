"""React specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class ReactAgent(BaseTechAgent):
    TECH_ID = "react"
    TECH_NAME = "React"

    EXPERT_PERSONA = (
        "You are a senior React architect who thinks in components, hooks, and unidirectional "
        "data flow. You have strong opinions on state management, server vs client components, "
        "and modern React patterns. You stay current with React 18+ features."
    )

    ARCHITECTURE_FOCUS = (
        "Function components + hooks (no class components), proper hook dependencies, "
        "co-located state (useState) before reaching for global state (Zustand/Redux Toolkit), "
        "Suspense + transitions for async UI, server components / RSC where applicable, "
        "Tailwind or CSS Modules for styling, React Query/SWR for server state, "
        "component composition over inheritance."
    )

    STRENGTHS = [
        "Interactive single-page applications (SPAs)",
        "Complex stateful UIs (dashboards, builders, editors)",
        "Apps where component reuse is valuable (large UI libraries)",
        "Real-time UIs with optimistic updates",
        "Mobile via React Native sharing logic with web",
        "Massive ecosystem (component libraries, tooling, hiring pool)",
    ]

    WEAKNESSES = [
        "Content sites where SEO + simple HTML wins (use Astro, plain HTML, Next.js with SSG)",
        "Tiny static pages — ship-of-Theseus complexity for nothing",
        "Apps where the team prefers stronger opinions / typing (Angular better)",
        "Hyper-performance landing pages where every kB matters (Astro/Svelte better)",
    ]

    ANTI_PATTERNS = [
        "Stale closures from missing/wrong useEffect dependencies",
        "Lifting state higher than needed instead of co-locating",
        "Reaching for Redux/Context for problems useState/useReducer would solve",
        "Mutating state directly instead of returning new objects",
        "Putting derived state in useState instead of computing during render",
        "Calling hooks conditionally — breaks the rules of hooks",
    ]
