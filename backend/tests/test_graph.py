import pytest
import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.planner import run_planner
from backend.agents.searcher import run_searcher
from backend.tools.search_tool import search_web
from backend.tools.fetch_tool import fetch_page_content

@pytest.mark.asyncio
async def test_planner_agent():
    """Tests the Planner Agent's ability to divide queries."""
    sub_qs = await run_planner("ev solid state battery economic tradeoffs")
    assert isinstance(sub_qs, list)
    assert len(sub_qs) > 0
    assert any("battery" in q.lower() or "economic" in q.lower() or "cost" in q.lower() for q in sub_qs)

@pytest.mark.asyncio
async def test_searcher_agent():
    """Tests the Search Agent's ability to generate keywords."""
    queries = await run_searcher("How much do EV battery packs cost in 2026?")
    assert isinstance(queries, list)
    assert len(queries) > 0

@pytest.mark.asyncio
async def test_search_and_fetch_tools():
    """Tests the mock fallbacks for searches and page retrievals."""
    results = await search_web("solid-state battery")
    assert len(results) > 0
    assert results[0]["url"] is not None
    
    # Test fetch content
    content = await fetch_page_content(results[0]["url"])
    assert len(content) > 0
