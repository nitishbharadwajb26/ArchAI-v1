"""
Quick smoke test for the RAG pipeline.

Run from E:/ArchAI/rag:
    python test_rag.py                  # runs all tests
    python test_rag.py --test retriever # individual tests
    python test_rag.py --test router
    python test_rag.py --test chain
    python test_rag.py --test config    # just print config
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)

# Path bootstrap — add scraper/ and rag/ to sys.path
SCRAPER_ROOT = Path(__file__).resolve().parent.parent / "scraper"
sys.path.insert(0, str(SCRAPER_ROOT))

RAG_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(RAG_ROOT))


def show_config():
    print("\n" + "=" * 60)
    print("ACTIVE CONFIG")
    print("=" * 60)
    from config.provider_config import get_config
    cfg = get_config()
    print(cfg.summary())
    if cfg.agent_provider.value == "groq" and not cfg.groq_api_key:
        print("\n⚠ GROQ_API_KEY is NOT set!")
        print("  Add it to E:/ArchAI/.env, E:/ArchAI/rag/.env, or E:/ArchAI/scraper/.env")


def test_retriever():
    print("\n" + "=" * 60)
    print("TEST 1: Retriever")
    print("=" * 60)
    from retriever import Retriever
    r = Retriever()

    techs = r.get_available_techs()
    print(f"✓ Available tech collections: {[t['tech_id'] for t in techs]}")
    print(f"✓ Total chunks: {sum(t.get('chunk_count', 0) for t in techs)}")

    chunks = r.retrieve(["fastapi"], "how to create a REST endpoint", top_k=3)
    print(f"✓ Retrieved {len(chunks)} chunks for 'fastapi'")
    if chunks:
        print(f"  Top score: {chunks[0]['relevance_score']:.3f}")
        print(f"  Top chunk preview: {chunks[0]['content'][:120]}...")


def test_router():
    print("\n" + "=" * 60)
    print("TEST 2: Router")
    print("=" * 60)
    from router import Router
    r = Router()

    queries = [
        "I need to build a REST API with Python",
        "Build a dashboard with a React frontend and NestJS backend",
        "Create a .NET MVC web application",
    ]
    for q in queries:
        result = r.route(q)
        print(f"  Query: '{q}'")
        print(f"  → {result}\n")


def test_full_chain():
    print("\n" + "=" * 60)
    print("TEST 3: Full RAG Chain")
    print("=" * 60)
    from chain import RAGChain
    chain = RAGChain()

    query = (
        "I need to build a scalable REST API with Python. "
        "It should support async operations and auto-generated API docs."
    )
    print(f"Query: {query}\n")

    response = chain.run(query)
    print(f"\n✓ Routed to: {response.routed_techs}")
    summary = response.summary
    print(f"✓ Summary: {summary[:200]}{'...' if len(summary) > 200 else ''}")
    print(f"✓ Recommended stack: {response.recommended_stack}")
    print(f"✓ Agent details: {len(response.agent_details)}")

    if response.agent_details:
        for agent in response.agent_details[:2]:
            print(f"\n  → {agent['tech_name']} (confidence={agent['confidence']:.2f})")
            reason = agent.get("reason", "")
            print(f"    Reason: {reason[:150]}{'...' if len(reason) > 150 else ''}")
            if agent.get("error"):
                print(f"    ⚠ Error: {agent['error']}")

    if response.error:
        print(f"\n⚠ Warning: {response.error}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        choices=["config", "retriever", "router", "chain", "all"],
        default="all",
    )
    args = parser.parse_args()

    show_config()

    if args.test in ("retriever", "all"):
        test_retriever()
    if args.test in ("router", "all"):
        test_router()
    if args.test in ("chain", "all"):
        test_full_chain()

    print("\n✅ Tests complete.\n")
