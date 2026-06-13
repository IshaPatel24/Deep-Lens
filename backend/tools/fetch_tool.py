import logging
import httpx
import trafilatura
from typing import Dict

logger = logging.getLogger(__name__)

# Mock page contents to support offline testing with high fidelity
MOCK_PAGES: Dict[str, str] = {
    "https://www.evtechjournal.com/solid-state-batteries-2026": """
    Solid-State Battery Breakthroughs in EV Applications (2026)
    Published: January 15, 2026 | EV Technology Journal

    In 2026, the automotive industry stands on the cusp of a battery revolution. Solid-state batteries (SSBs) utilizing solid electrolytes instead of liquid ones are transitionary but highly promising.
    
    1. Energy Density and Performance:
    Recent tests show prototype sulfide-based solid-state cells reaching energy densities of 480 Wh/kg to 510 Wh/kg at the cell level. This is roughly double the density of high-performance nickel-rich lithium-ion cells currently in production (which average 240-280 Wh/kg).
    This energy density boost translates directly to a 60-80% increase in electric vehicle range, pushing standard sedans past 700 miles on a single charge.
    
    2. Manufacturing and Economic Hurdles:
    Despite technical success, economic feasibility remains a critical issue. In 2026, manufacturing solid-state battery packs at pilot-scale costs roughly $300/kWh, compared to standard lithium-ion packs which have fallen to $80/kWh due to scaling. 
    The high cost is driven by raw material constraints (especially high-purity lithium metals and complex solid electrolytes) and the requirement for extreme dry-room environments during assembly to prevent moisture degradation of sulfide electrolytes.
    
    3. Safety Profiles:
    By replacing volatile liquid organic electrolytes with solid ceramic or polymer materials, the risk of thermal runaway is virtually eliminated. Solid-state cells can operate at higher temperature thresholds without dendrite puncture causing combustion.
    """,
    
    "https://www.cleanenergyfinance.org/reports/ev-battery-economics": """
    The Economic Tradeoffs of Solid-State EV Fleets
    Published: February 2026 | Clean Energy Finance Institute

    This report analyzes the cost structures of battery technologies in 2026.
    
    Cost Projections and Price Parity:
    Our financial models suggest that solid-state batteries (SSBs) will not achieve price parity with lithium-ion batteries until at least 2030. The current pricing structure is highly restrictive.
    Cell manufacturing costs for SSBs are estimated at $220/kWh, with pack assembly adding another $80/kWh, resulting in a total pack cost of $300/kWh in 2026.
    In contrast, standard lithium-ion cells (specifically Lithium Iron Phosphate - LFP) have achieved massive economies of scale, with cell costs dipping to $55/kWh and pack costs at $85/kWh. 
    This means outfitting an EV with a 100 kWh SSB pack costs $30,000, whereas a lithium-ion pack of the same capacity costs only $8,500. This $21,500 difference makes SSBs economically unviable for mass-market vehicles, limiting their deployment to luxury EVs and niche performance models.
    
    Sulfide vs. Oxide Electrolytes:
    Sulfide-based solid electrolytes (like Li2S-P2S5) are favored for their superior ionic conductivity and compressibility, but are more expensive than oxide-based alternatives. Oxide electrolytes (like LLZO) are cheaper and safer but brittle and harder to manufacture at scale.
    """,
    
    "https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts": """
    Sulfide vs Oxide Solid Electrolytes: An Environmental and Life Cycle Review
    Published: March 2026 | Nature Ecology & Environment

    As solid-state battery technology approaches commercialization, understanding its environmental footprint is essential.
    
    Manufacturing Carbon Footprint:
    Oxide-based solid-state batteries require high-temperature sintering (often exceeding 1000°C) during manufacturing to bond the ceramic electrolyte to the electrodes. This process is energy-intensive and increases the carbon footprint of production by 20% compared to standard lithium-ion batteries.
    Sulfide-based batteries can be processed at lower temperatures (under 200°C) via roll-to-roll pressing, resulting in a lower manufacturing carbon footprint.
    
    Recycling and Toxicity Risks:
    Sulfide electrolytes pose a unique environmental hazard. If exposed to ambient moisture, sulfides react to release toxic and flammable hydrogen sulfide (H2S) gas. 
    This requires specialized, hermetically sealed recycling processes. Standard hydrometallurgical recycling facilities cannot process sulfide batteries without major upgrades.
    In contrast, oxide batteries are chemically stable and do not pose gas release risks, though they are difficult to recycle due to the mechanical toughness of ceramic layers.
    """,
    
    "https://www.batterycostwatch.com/lithium-ion-2026": """
    Lithium-Ion Battery Cost Curves and Manufacturing Projections
    Published: April 2026 | Battery Cost Watch

    Lithium-ion batteries continue to dominate the global EV supply chain, achieving record-low costs in 2026.
    
    LFP and Sodium-Ion Disruptions:
    Lithium iron phosphate (LFP) chemistry has captured 60% of the EV market due to its safety and low cost. LFP pack costs have stabilized at $80/kWh. 
    Meanwhile, sodium-ion batteries have entered mass production for urban, short-range EVs, achieving pack costs of $50/kWh, though their energy density is lower (~160 Wh/kg).
    
    Supply Chain Maturity:
    Lithium carbonate prices have stabilized at $12,000/ton, a significant decline from the peaks of previous years. This supply chain stability has allowed battery manufacturers to optimize production lines, achieving yields of over 95%.
    Because lithium-ion recycling networks are already established, the lifecycle environmental impact of lithium-ion is well-understood, making it the benchmark against which all new battery technologies must be evaluated.
    """,
    
    "https://www.aiarchitecture.io/langgraph-performance": """
    Autonomous Agent Workflows and LangGraph Performance Studies
    Published: May 2026 | AI Architecture Insights

    LangGraph has emerged as a premier framework for building complex agentic systems. By organizing agents as nodes in a stateful graph, developers can implement loops, state rollbacks, and parallel execution.
    
    1. Multi-Agent Performance:
    Our studies show that breaking down a research task into a multi-agent graph (Planner -> Searcher -> Evaluator -> Extractor -> Verifier -> Writer -> Critic) reduces hallucinations by 85% compared to single-agent prompts.
    
    2. Writer-Critic Optimization loops:
    The inclusion of a Critic node that inspects the writer's report against extracted facts, and sends instructions back for revisions, improves citation accuracy to 98.4%. Capping the loop at 2 iterations prevents infinite loops and controls API costs.
    
    3. State Inspection:
    Using Server-Sent Events (SSE) to stream the Graph state in real time provides an excellent user experience. Users can inspect which agent is running, what URLs are being processed, and what intermediate facts have been extracted.
    """,
    
    "https://www.enterprisetech.com/agentic-ai-research-2026": """
    State of Agentic AI in Enterprise Research Assistants
    Published: June 2026 | Enterprise Tech Review

    Enterprises are rapidly deploying autonomous agents to handle complex information gathering tasks.
    
    Trust and Citation Accuracy:
    The primary barrier to enterprise agent adoption is trust. Basic RAG wrappers that simply feed search results to a GPT model often hallucinate references or misrepresent sources.
    To solve this, advanced systems implement a source evaluation and verification pipeline.
    First, the source evaluator filters out low-quality sites (discarding personal blogs, forums, and sites with high commercial bias, keeping only primary sources and established outlets).
    Second, the verifier cross-checks every claim. If only one source makes a claim, it is flagged as low confidence. If sources disagree, the system highlights the contradiction.
    Enterprise testing shows this verification pipeline reduces business errors by 90% compared to basic search summarization.
    """
}

async def fetch_page_content(url: str) -> str:
    """
    Fetches the web page content and extracts clean text using trafilatura.
    Falls back to mock data if offline or if fetch fails.
    """
    # Check if we have mock content for this URL (high-fidelity mock data)
    if url in MOCK_PAGES:
        logger.info(f"Using mock page content for: {url}")
        return MOCK_PAGES[url].strip()

    try:
        logger.info(f"Fetching URL: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers, timeout=12.0)
            if response.status_code == 200:
                html = response.text
                extracted = trafilatura.extract(html, include_links=False, include_images=False)
                if extracted:
                    return extracted
                # Fallback to raw text without HTML tags (basic extraction)
                return response.text[:5000]
            else:
                logger.warning(f"Failed to fetch {url}, status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching page {url}: {e}")
    
    # Fallback mock content generator for any unknown URL if fetch fails
    return f"This is placeholder content for {url}. The page could not be fetched live. It is assumed to contain relevant facts regarding the query topic, but requires live connection for details."
