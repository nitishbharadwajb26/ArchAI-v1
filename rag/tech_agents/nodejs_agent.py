"""Node.js specialist agent."""

from base_agent import BaseTechAgent
from registry import register_agent


@register_agent
class NodeJSAgent(BaseTechAgent):
    TECH_ID = "nodejs"
    TECH_NAME = "Node.js"

    EXPERT_PERSONA = (
        "You are a senior Node.js architect with deep knowledge of the event loop, "
        "non-blocking I/O, npm ecosystem, and the differences between Node's core "
        "modules and frameworks built on top (Express, Fastify, Koa). You think in "
        "streams, promises, and async iterators."
    )

    ARCHITECTURE_FOCUS = (
        "Single-threaded event loop awareness, non-blocking I/O at every boundary, "
        "proper async/await usage, streams for large data, cluster mode for "
        "multi-core, framework selection (Express for compatibility, Fastify for "
        "performance, Koa for modern middleware), and clean error propagation."
    )

    STRENGTHS = [
        "Real-time apps (WebSockets, Socket.IO, Server-Sent Events)",
        "I/O-bound APIs with high concurrency (chat backends, proxies, gateways)",
        "Streaming data pipelines",
        "Full-stack JavaScript — sharing types/code between frontend and backend",
        "Microservices and serverless functions (cold-start friendly)",
        "Glue services that talk to many APIs concurrently",
    ]

    WEAKNESSES = [
        "CPU-bound workloads (image processing, ML inference) — single-threaded hurts",
        "Large enterprise codebases without TypeScript discipline (NestJS better)",
        "Numerical/scientific computing (Python is the right answer)",
        "Teams unfamiliar with async/event-loop semantics — easy to write blocking code",
    ]

    ANTI_PATTERNS = [
        "Synchronous fs/crypto calls in request handlers — blocks the event loop",
        "Unhandled promise rejections — crashes the process in modern Node",
        "Loading huge files into memory instead of using streams",
        "Mutable global state across requests",
        "Mixing callbacks and async/await — keep one style",
    ]
