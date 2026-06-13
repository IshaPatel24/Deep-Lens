import json
import logging
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_planner(query: str) -> List[str]:
    """
    Breaks a query into 3-6 distinct sub-questions/search angles.
    """
    logger.info(f"Running Planner Agent for query: {query}")
    llm = get_llm()
    
    system_prompt = """You are the Planner. Given a user research query, break it into 3-6 
distinct, non-overlapping sub-questions or search angles that together 
comprehensively cover the topic. Consider: definitions/background, 
current state, comparisons/alternatives, statistics/data, risks or 
controversies, and future outlook — but only include angles relevant 
to THIS query. Output strictly as a JSON list of sub-questions.

Example output:
[
  "What is the current technological state of solid-state batteries in 2026?",
  "What are the manufacturing costs and economic tradeoffs of solid-state EV batteries?"
]"""

    user_prompt = f"Research Query: {query}"
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Strip markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        questions = json.loads(content)
        if isinstance(questions, list) and len(questions) > 0:
            logger.info(f"Planner successfully generated {len(questions)} sub-questions.")
            return [q.strip() for q in questions]
    except Exception as e:
        logger.error(f"Error in Planner Agent: {e}")
        
    # Standard fallback
    return [
        f"What is the background and definition of {query}?",
        f"What are the key statistics and current state of {query}?",
        f"What are the main tradeoffs and future outlook for {query}?"
    ]
