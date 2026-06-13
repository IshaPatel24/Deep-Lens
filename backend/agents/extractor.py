import json
import logging
from typing import List, Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_extractor(page_text: str, sub_question: str, source_url: str) -> List[Dict[str, Any]]:
    """
    Extracts 2-5 key factual claims from clean page text based on a sub-question.
    """
    logger.info(f"Running Extractor Agent for {source_url} on sub-question: {sub_question}")
    
    # Cap text length to prevent context exhaustion
    truncated_text = page_text[:15000]
    
    llm = get_llm()
    
    system_prompt = """You are the Extractor. Given the full text of a fetched page and the 
sub-question it relates to, extract 2-5 key factual claims relevant 
to the sub-question. For each claim, note:
- claim: the claim text (in your own words, written professionally and objectively)
- source_url: the exact source URL provided
- support_note: a direct supporting sentence or short text fragment from the source text (do not quote more than ~15 words verbatim)

Output strictly as a JSON list of objects.
Example output:
[
  {
    "claim": "Solid state batteries possess twice the energy density of standard lithium cells.",
    "source_url": "https://www.example.com",
    "support_note": "reaching energy densities of 480 Wh/kg to 510 Wh/kg... roughly double standard"
  }
]"""

    user_prompt = f"Source URL: {source_url}\nSub-Question: {sub_question}\n\nPage Content:\n{truncated_text}"
    
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
            
        claims = json.loads(content)
        if isinstance(claims, list):
            # Ensure correct source URL mapping
            for c in claims:
                c["source_url"] = source_url
            return claims
    except Exception as e:
        logger.error(f"Error in Extractor Agent: {e}")
        
    return []
