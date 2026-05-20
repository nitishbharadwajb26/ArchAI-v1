"""
Tech Stack Registry — Single source of truth for all supported technologies.
To add a new tech: add an entry here. Nothing else needs to change.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TechStackConfig:
    """Configuration for a single technology stack."""
    id: str                          # Unique identifier e.g. "fastapi"
    name: str                        # Display name e.g. "FastAPI"
    category: str                    # "backend" | "frontend" | "fullstack" | "framework"
    language: str                    # Primary language e.g. "python"
    doc_urls: list[str]              # Entry point URLs to crawl
    allowed_domains: list[str]       # Domains to stay within during crawl
    url_patterns_include: list[str]  # URL substrings to crawl (e.g. "/docs/", "/guide/")
    url_patterns_exclude: list[str]  # URL substrings to skip
    max_pages: int = 300             # Safety cap per tech
    content_selectors: list[str] = field(default_factory=list)  # CSS selectors for main content
    code_selectors: list[str] = field(default_factory=list)      # CSS selectors for code blocks
    tags: list[str] = field(default_factory=list)               # For agent routing


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY: Add new technologies here only
# ─────────────────────────────────────────────────────────────────────────────

TECH_REGISTRY: dict[str, TechStackConfig] = {

    # ── PYTHON BACKEND ────────────────────────────────────────────────────────

    "fastapi": TechStackConfig(
        id="fastapi",
        name="FastAPI",
        category="backend",
        language="python",
        doc_urls=["https://fastapi.tiangolo.com/"],
        allowed_domains=["fastapi.tiangolo.com"],
        url_patterns_include=["/tutorial/", "/advanced/", "/deployment/", "fastapi.tiangolo.com"],
        url_patterns_exclude=["#", "mailto:", ".pdf", ".zip"],
        max_pages=200,
        content_selectors=["article", ".md-content", "main", ".content"],
        code_selectors=["pre code", ".highlight", "code"],
        tags=["python", "backend", "api", "rest", "async"],
    ),

   "django": TechStackConfig(
        id="django",
        name="Django",
        category="backend",
        language="python",
        doc_urls=["https://docs.djangoproject.com/en/5.2/contents/"],
        allowed_domains=["docs.djangoproject.com"],
        url_patterns_include=["/en/5.2/"],
        url_patterns_exclude=["#", "mailto:", "_modules/", "/_downloads/", "/_sources/", "genindex", "py-modindex"],
        max_pages=300,
        content_selectors=["#docs-content", ".section", "article", "main"],
        code_selectors=["pre", ".highlight", "code"],
        tags=["python", "backend", "orm", "mvc", "web"],
    ),

    "flask": TechStackConfig(
        id="flask",
        name="Flask",
        category="backend",
        language="python",
        doc_urls=["https://flask.palletsprojects.com/en/3.0.x/"],
        allowed_domains=["flask.palletsprojects.com"],
        url_patterns_include=["palletsprojects.com/en/"],
        url_patterns_exclude=["#", "mailto:", "_sources/"],
        max_pages=150,
        content_selectors=[".body", "article", "main", ".document"],
        code_selectors=["pre", ".highlight", "code"],
        tags=["python", "backend", "micro", "wsgi", "web"],
    ),

    # ── JAVASCRIPT / TYPESCRIPT BACKEND ──────────────────────────────────────

    "nodejs": TechStackConfig(
        id="nodejs",
        name="Node.js",
        category="backend",
        language="javascript",
        doc_urls=["https://nodejs.org/api/"],
        allowed_domains=["nodejs.org"],
        url_patterns_include=["nodejs.org/api/"],
        url_patterns_exclude=["#", "mailto:", ".pdf", ".zip", ".json", "blog", "download", "dist"],
        max_pages=200,
        content_selectors=["#apicontent", "article", "main", ".content"],
        code_selectors=["pre code", ".language-js", ".language-javascript"],
        tags=["javascript", "backend", "runtime", "async", "npm"],
    ),

    "nestjs": TechStackConfig(
        id="nestjs",
        name="NestJS",
        category="backend",
        language="typescript",
        doc_urls=["https://docs.nestjs.com/"],
        allowed_domains=["docs.nestjs.com"],
        url_patterns_include=["docs.nestjs.com"],
        url_patterns_exclude=["#", "mailto:"],
        max_pages=200,
        content_selectors=["article", ".content", "main"],
        code_selectors=["pre code", ".language-typescript", ".language-javascript"],
        tags=["typescript", "backend", "nodejs", "decorators", "modules", "enterprise"],
    ),

    "loopback": TechStackConfig(
        id="loopback",
        name="LoopBack 4",
        category="backend",
        language="typescript",
        doc_urls=["https://loopback.io/doc/en/lb4/"],
        allowed_domains=["loopback.io"],
        url_patterns_include=["/doc/en/lb4/"],
        url_patterns_exclude=["#", "mailto:"],
        max_pages=150,
        content_selectors=["article", ".content", "main", "#main-content"],
        code_selectors=["pre code", ".language-typescript"],
        tags=["typescript", "backend", "ibm", "rest", "api"],
    ),

    # ── JAVASCRIPT / TYPESCRIPT FRONTEND ─────────────────────────────────────

    "react": TechStackConfig(
        id="react",
        name="React",
        category="frontend",
        language="javascript",
        doc_urls=["https://react.dev/learn", "https://react.dev/reference/react"],
        allowed_domains=["react.dev"],
        url_patterns_include=["react.dev/learn", "react.dev/reference"],
        url_patterns_exclude=["#", "mailto:"],
        max_pages=200,
        content_selectors=["article", "main", ".content"],
        code_selectors=["pre code", ".sandpack", "code"],
        tags=["javascript", "typescript", "frontend", "ui", "spa", "hooks"],
    ),

    "angular": TechStackConfig(
        id="angular",
        name="Angular",
        category="frontend",
        language="typescript",
        doc_urls=["https://angular.dev/overview"],
        allowed_domains=["angular.dev"],
        url_patterns_include=["angular.dev/guide", "angular.dev/api", "angular.dev/tutorials"],
        url_patterns_exclude=["#", "mailto:"],
        max_pages=250,
        content_selectors=["article", "main", ".docs-content", ".content"],
        code_selectors=["pre code", ".docs-code", "code"],
        tags=["typescript", "frontend", "spa", "rxjs", "enterprise"],
    ),

    # ── .NET ─────────────────────────────────────────────────────────────────

    "dotnet_core": TechStackConfig(
        id="dotnet_core",
        name=".NET Core / ASP.NET Core",
        category="backend",
        language="csharp",
        doc_urls=["https://learn.microsoft.com/en-us/aspnet/core/?view=aspnetcore-8.0"],
        allowed_domains=["learn.microsoft.com"],
        url_patterns_include=["/en-us/aspnet/core/", "/en-us/dotnet/core/"],
        url_patterns_exclude=["#", "mailto:", "/previous-versions/", "?view=netframework"],
        max_pages=250,
        content_selectors=["#main-column", "article", ".content", "main"],
        code_selectors=["pre code", ".lang-csharp", ".language-csharp"],
        tags=["csharp", "dotnet", "backend", "api", "microsoft", "web"],
    ),

    "dotnet_mvc": TechStackConfig(
        id="dotnet_mvc",
        name="ASP.NET Core MVC",
        category="fullstack",
        language="csharp",
        doc_urls=["https://learn.microsoft.com/en-us/aspnet/core/mvc/overview?view=aspnetcore-8.0"],
        allowed_domains=["learn.microsoft.com"],
        url_patterns_include=["/en-us/aspnet/core/mvc/"],
        url_patterns_exclude=["#", "mailto:", "/previous-versions/"],
        max_pages=150,
        content_selectors=["#main-column", "article", "main"],
        code_selectors=["pre code", ".lang-csharp", ".language-csharp", ".lang-cshtml"],
        tags=["csharp", "dotnet", "mvc", "razor", "fullstack"],
    ),

    "blazor": TechStackConfig(
        id="blazor",
        name="Blazor",
        category="frontend",
        language="csharp",
        doc_urls=["https://learn.microsoft.com/en-us/aspnet/core/blazor/?view=aspnetcore-8.0"],
        allowed_domains=["learn.microsoft.com"],
        url_patterns_include=["/en-us/aspnet/core/blazor/"],
        url_patterns_exclude=["#", "mailto:", "/previous-versions/"],
        max_pages=150,
        content_selectors=["#main-column", "article", "main"],
        code_selectors=["pre code", ".lang-csharp", ".lang-razor"],
        tags=["csharp", "dotnet", "frontend", "wasm", "spa"],
    ),
}


def get_tech(tech_id: str) -> Optional[TechStackConfig]:
    return TECH_REGISTRY.get(tech_id)


def get_all_techs() -> list[TechStackConfig]:
    return list(TECH_REGISTRY.values())


def get_techs_by_language(language: str) -> list[TechStackConfig]:
    return [t for t in TECH_REGISTRY.values() if t.language == language]


def get_techs_by_tag(tag: str) -> list[TechStackConfig]:
    return [t for t in TECH_REGISTRY.values() if tag in t.tags]
