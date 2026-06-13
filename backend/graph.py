import asyncio
import logging
import time
from typing import List, Dict, Any, Callable
from backend.agents.planner import run_planner
from backend.agents.searcher import run_searcher
from backend.agents.evaluator import run_evaluator
from backend.agents.extractor import run_extractor
from backend.agents.verifier import run_verifier
from backend.agents.writer import run_writer
from backend.agents.critic import run_critic
from backend.tools.search_tool import search_web
from backend.tools.fetch_tool import fetch_page_content

logger = logging.getLogger(__name__)

class ResearchState:
    """Represents the state of our multi-agent pipeline."""
    def __init__(self, query: str):
        self.query: str = query
        self.sub_questions: List[str] = []
        self.sources: List[Dict[str, Any]] = []
        self.extracted_claims: List[Dict[str, Any]] = []
        self.verified_data: List[Dict[str, Any]] = []
        self.report: str = ""
        self.critic_feedback: str = ""
        self.critic_loops: int = 0
        self.discarded_sources_count: int = 0

async def run_research_pipeline(query: str, session_id: str, publish_log: Callable[[Dict[str, Any]], None]):
    """
    Executes the research agent graph and streams intermediate states to the client.
    """
    state = ResearchState(query)
    
    # Helper to push updates to client
    async def log_step(agent: str, status: str, details: Any = None):
        msg = {
            "session_id": session_id,
            "agent": agent,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        logger.info(f"Agent Log [{agent}] - {status}")
        await publish_log(msg)
        await asyncio.sleep(0.5) # Give UI time to animate micro-steps

    try:
        # =====================================================================
        # 1. PLANNER NODE
        # =====================================================================
        await log_step("Planner", "running", "Analyzing query and breaking it down into sub-questions...")
        state.sub_questions = await run_planner(state.query)
        await log_step("Planner", "completed", state.sub_questions)

        # =====================================================================
        # 2. SEARCH & EVALUATE NODES (run per sub-question)
        # =====================================================================
        await log_step("Searcher", "running", "Expanding search queries per sub-question...")
        
        all_raw_results = []
        source_urls = set()
        
        for idx, sub_q in enumerate(state.sub_questions):
            await log_step("Searcher", "running", f"Generating search terms for: '{sub_q}'")
            queries = await run_searcher(sub_q)
            
            await log_step("Searcher", "running", f"Searching web for: {', '.join(queries[:2])}")
            
            # Fetch search results for queries
            search_tasks = [search_web(q) for q in queries]
            search_outputs = await asyncio.gather(*search_tasks)
            
            for results in search_outputs:
                for r in results:
                    if r["url"] not in source_urls:
                        source_urls.add(r["url"])
                        all_raw_results.append(r)
                        
        await log_step("Searcher", "completed", f"Collected {len(all_raw_results)} unique search results.")

        # Source Evaluator
        await log_step("Source Evaluator", "running", f"Scoring reliability of {len(all_raw_results)} sources...")
        evaluated_sources = await run_evaluator(all_raw_results)
        
        # Keep track of discarded count
        state.sources = evaluated_sources
        state.discarded_sources_count = len(all_raw_results) - len(evaluated_sources)
        
        eval_details = {
            "considered": len(all_raw_results),
            "accepted": len(evaluated_sources),
            "discarded": state.discarded_sources_count,
            "sources": evaluated_sources
        }
        await log_step("Source Evaluator", "completed", eval_details)

        # =====================================================================
        # 3. READER/EXTRACTOR NODE
        # =====================================================================
        if not state.sources:
            await log_step("Extractor", "failed", "No reliable sources found to extract claims.")
            raise Exception("No reliable sources found after evaluation.")

        await log_step("Extractor", "running", f"Fetching full texts and extracting claims from {len(state.sources)} sources...")
        
        extractor_tasks = []
        for src in state.sources:
            url = src["url"]
            # Map source to a relevant sub-question for contextual extraction
            # Just match keyword or use the first sub-question as default
            rel_sub_q = state.sub_questions[0]
            for sq in state.sub_questions:
                if any(word in sq.lower() for word in src.get("reason", "").lower().split()):
                    rel_sub_q = sq
                    break
                    
            async def fetch_and_extract(url=url, sub_q=rel_sub_q):
                text = await fetch_page_content(url)
                if not text.strip():
                    return []
                return await run_extractor(text, sub_q, url)
                
            extractor_tasks.append(fetch_and_extract())
            
        claims_lists = await asyncio.gather(*extractor_tasks)
        for claims in claims_lists:
            state.extracted_claims.extend(claims)
            
        await log_step("Extractor", "completed", {
            "total_claims": len(state.extracted_claims),
            "claims": state.extracted_claims
        })

        # =====================================================================
        # 4. VERIFIER NODE
        # =====================================================================
        await log_step("Verifier", "running", "Cross-checking claims and mapping contradictions...")
        state.verified_data = await run_verifier(state.extracted_claims)
        
        # Count contradictions vs verified
        contradiction_count = sum(1 for c in state.verified_data if c["status"] == "contradiction")
        verified_count = sum(1 for c in state.verified_data if c["status"] == "verified")
        single_source_count = sum(1 for c in state.verified_data if c["status"] == "single-source")
        
        await log_step("Verifier", "completed", {
            "contradictions": contradiction_count,
            "verified": verified_count,
            "single_source": single_source_count,
            "data": state.verified_data
        })

        # =====================================================================
        # 5. WRITER-CRITIC LOOP
        # =====================================================================
        state.critic_loops = 0
        state.critic_feedback = ""
        
        while state.critic_loops < 2:
            loop_idx = state.critic_loops + 1
            await log_step("Writer", "running", f"Drafting research report (Iteration {loop_idx})...")
            state.report = await run_writer(state.query, state.verified_data, state.critic_feedback)
            await log_step("Writer", "completed", {"draft": state.report, "loop": loop_idx})

            await log_step("Critic", "running", "Reviewing report for fact-checking & citation alignment...")
            critic_result = await run_critic(state.report, state.verified_data)
            
            if critic_result.strip().upper() == "APPROVED":
                await log_step("Critic", "completed", "APPROVED: Report meets all validation requirements.")
                break
            else:
                state.critic_feedback = critic_result
                state.critic_loops += 1
                await log_step("Critic", "revision_required", {
                    "feedback": state.critic_feedback,
                    "next_loop": state.critic_loops + 1
                })
        else:
            await log_step("Critic", "completed", "Maximum loops reached. Approving final version.")

        # =====================================================================
        # 6. FINAL SYNTHESIS
        # =====================================================================
        await log_step("DeepLens System", "completed", {
            "report": state.report,
            "verified_data": state.verified_data,
            "sources": state.sources,
            "discarded_count": state.discarded_sources_count
        })
        
        return state

    except Exception as e:
        logger.error(f"Error in research pipeline: {e}", exc_info=True)
        await log_step("DeepLens System", "failed", str(e))
        raise e
