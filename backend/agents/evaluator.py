import json
import logging
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_evaluator(results: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Evaluates search results and scores them 0-10. Discards anything below 4.
    """
    logger.info(f"Running Source Evaluator Agent on {len(results)} results")
    if not results:
        return []
        
    llm = get_llm()
    
    system_prompt = """You are the Source Evaluator. For each search result (title, URL, 
snippet), score it from 0-10 on:
- Authority (official/primary source, established outlet = 8-10; 
  reputable blog/secondary source = 5-7; random blog/forum/ad-heavy site = 0-4)
- Recency (relevant to topic's time-sensitivity)
- Likely bias (flag and penalize if source has known strong commercial or ideological bias)

Return strictly a JSON list with: url, score, reason.
Example output:
[
  {
    "url": "https://www.example.com/report",
    "score": 8,
    "reason": "Primary industry source with detailed data, recent as of 2026, low bias."
  }
]"""

    # Format list for the prompt
    formatted_results = []
    for r in results:
        formatted_results.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('snippet')}\n---")
    
    user_prompt = "\n".join(formatted_results)
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        eval_list = json.loads(content)
        if isinstance(eval_list, list):
            # Enforce schema structure and score filtering >= 4
            scored_sources = []
            for item in eval_list:
                url = item.get("url")
                score = int(item.get("score", 0))
                reason = item.get("reason", "No evaluation reason provided.")
                
                if score >= 4:
                    scored_sources.append({
                        "url": url,
                        "score": score,
                        "reason": reason
                    })
                else:
                    logger.info(f"Discarding source {url} due to low score ({score}): {reason}")
            return scored_sources
    except Exception as e:
        logger.error(f"Error in Source Evaluator: {e}")
        
    # Failsafe fallback: keep all sources with score 7
    return [{"url": r["url"], "score": 7, "reason": "Failsafe fallback score."} for r in results]
