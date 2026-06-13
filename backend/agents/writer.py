import json
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.llm import get_llm

logger = logging.getLogger(__name__)

async def run_writer(query: str, verified_data: list, feedback: str = "") -> str:
    """
    Synthesizes the final research report in Markdown using the verified claims.
    """
    logger.info(f"Running Writer Agent for query: {query}")
    llm = get_llm()
    
    system_prompt = """You are the Writer. Using the verified claims data, write a 
structured research report in Markdown.
The report MUST contain these sections:
1. Title
2. Executive Summary
3. Key Findings (organized by sub-topic)
4. Comparative Analysis (if applicable)
5. Contradictions & Open Questions (discuss conflicting sources neutrally)
6. Limitations (discuss lack of data, single-source claims, or scope limitations)
7. References (numbered list with clickable URLs)

Rules:
- Never copy source text directly; write in your own words.
- Add inline citation markers [1], [2] etc. matching the reference list.
- For contradictions, present both sides neutrally.
- Flag low-confidence claims explicitly (e.g., "According to a single source...", "A single reference notes that...").
- Use professional, academic tone.
"""

    user_prompt = f"Research Query: {query}\n\nVerified Claims Data:\n{json.dumps(verified_data, indent=2)}"
    if feedback:
        user_prompt += f"\n\nCritic Feedback (Apply these edits): {feedback}"
        
    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Error in Writer Agent: {e}")
        
    return f"# DeepLens Research Report: {query}\n\nError occurred while writing the report."
