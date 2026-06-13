import json
import logging
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_verifier(claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Groups extracted claims and cross-checks them across sources.
    Identifies high-confidence claims (multi-source), medium-confidence (single-source), 
    and contradictions (low-confidence).
    """
    logger.info(f"Running Verifier Agent on {len(claims)} extracted claims")
    if not claims:
        return []
        
    llm = get_llm()
    
    system_prompt = """You are the Verifier. Given a list of claims (with sources) about the research topic, 
group claims that address the same fact or sub-topic. For each group:
- If ≥2 independent sources agree → mark status "verified", confidence "high"
- If only 1 source makes the claim → mark status "single-source", confidence "medium"
- If sources conflict (disagree on numbers, dates, outcomes, or assessments) → mark status "contradiction", confidence "low", and list both versions and their sources.

Output strictly as a JSON list of objects in the following format:
[
  {
    "topic": "Name of the sub-topic or claim area",
    "status": "verified" | "single-source" | "contradiction",
    "confidence": "high" | "medium" | "low",
    "claims": [
      {
        "claim": "Claim text",
        "source_url": "URL of the source",
        "support_note": "Quote or supporting sentence"
      }
    ]
  }
]"""

    user_prompt = f"Claims List:\n{json.dumps(claims, indent=2)}"
    
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
            
        verified_groups = json.loads(content)
        if isinstance(verified_groups, list):
            logger.info(f"Verifier successfully grouped claims into {len(verified_groups)} topics.")
            return verified_groups
    except Exception as e:
        logger.error(f"Error in Verifier Agent: {e}")
        
    # Failsafe fallback: group each claim as single-source
    return [
        {
            "topic": c.get("claim", "")[:40] + "...",
            "status": "single-source",
            "confidence": "medium",
            "claims": [c]
        } for c in claims
    ]
