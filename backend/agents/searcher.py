import json
import logging
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_searcher(sub_question: str) -> List[str]:
    """
    Generates 2-3 distinct search queries for a given sub-question.
    """
    logger.info(f"Running Search Agent for sub-question: {sub_question}")
    llm = get_llm()
    
    system_prompt = """You are the Search Agent. For the given sub-question, generate 2-3 
distinct search queries (different phrasings/angles) to maximize 
source diversity and search coverage. Output strictly as a JSON list of query strings.

Example output:
[
  "solid-state battery cell-level energy density 2026",
  "solid-state batteries wh/kg ev range"
]"""

    user_prompt = f"Sub-question: {sub_question}"
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Strip markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        queries = json.loads(content)
        if isinstance(queries, list) and len(queries) > 0:
            return [q.strip() for q in queries]
    except Exception as e:
        logger.error(f"Error in Search Agent: {e}")
        
    return [sub_question, f"{sub_question} analysis", f"{sub_question} latest data"]
