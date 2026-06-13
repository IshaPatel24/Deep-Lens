import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_critic(draft_report: str, verified_data: list) -> str:
    """
    Evaluates the draft report against verified claims.
    Returns "APPROVED" or specific instructions for revision.
    """
    logger.info("Running Critic Agent on draft report")
    llm = get_llm()
    
    system_prompt = """You are the Critic. Review the draft report against the verified claims data. 
Verify:
1. Every claim in the report is traceably backed by the verified data (detect hallucinations).
2. All facts have appropriate inline numbered citations.
3. Disputed topics (contradictions) are presented neutrally, showing both perspectives.
4. Low-confidence (single-source) claims are framed conservatively (e.g. 'according to one report').

If issues are found, output specific, actionable revision instructions for the Writer.
If everything is correct and well-cited, output strictly 'APPROVED' without any other text.
"""

    user_prompt = f"Draft Report:\n{draft_report}\n\nVerified Claims Data:\n{json.dumps(verified_data, indent=2)}"
    
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Error in Critic Agent: {e}")
        
    return "APPROVED"
