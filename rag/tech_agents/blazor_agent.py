"""Blazor specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class BlazorAgent(BaseTechAgent):
    TECH_ID = "blazor"
    TECH_NAME = "Blazor"

    EXPERT_PERSONA = (
        "You are a senior Blazor architect who understands the trade-offs between "
        "Blazor Server (SignalR-driven) and Blazor WebAssembly (in-browser .NET runtime). "
        "You think in components, render modes, and stateful UI in C#."
    )

    ARCHITECTURE_FOCUS = (
        "Choose the right hosting model: Server for low-latency intranet apps with cheap "
        "compute on the server, WASM for offline-capable PWAs, or interactive auto-render "
        "modes (Blazor Server with WebAssembly fallback). Component composition with "
        "parameters, cascading values for context, EventCallback for child→parent "
        "communication, JS interop only when essential, dependency injection for services."
    )

    STRENGTHS = [
        "C#-only teams that want to share models and validation with the backend",
        "Intranet apps with stable connections (Server mode shines)",
        "Internal tools where avoiding a JS toolchain is a real win",
        "Apps that need real-time updates (Blazor Server's SignalR is built-in)",
        "Reusing existing C# libraries directly in the browser (WASM mode)",
    ]

    WEAKNESSES = [
        "Public-facing apps with high user count (Server mode = expensive scaling)",
        "Mobile-heavy users — WASM bundle download is large and slow on mobile",
        "Teams that already have JavaScript expertise — hiring pool is tiny for Blazor",
        "Apps that want the React/Vue ecosystem (component libraries, dev tools)",
        "SEO-critical sites without prerendering configured carefully",
    ]

    ANTI_PATTERNS = [
        "Storing user-specific state in Blazor Server's circuit without thinking about scale",
        "Heavy JS interop for things Blazor can do natively — defeats the purpose",
        "Choosing Blazor WASM for tiny apps — bundle download dwarfs the app",
        "Treating Blazor Server like a SPA — every UI event is a server round-trip",
    ]
