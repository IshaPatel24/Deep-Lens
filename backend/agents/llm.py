import os
import json
import logging
from typing import List, Dict, Any, Type, Optional
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

logger = logging.getLogger(__name__)

class MockChatModel:
    """Mock LLM class to simulate agent decisions and text generations when API keys are missing."""
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    def invoke(self, messages: List[Any], response_format: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        # Extract prompt text from messages
        system_prompt = ""
        user_prompt = ""
        for m in messages:
            if m.type == "system" or isinstance(m, SystemMessage):
                system_prompt += m.content + "\n"
            elif m.type == "human" or isinstance(m, HumanMessage):
                user_prompt += m.content + "\n"

        logger.info(f"Mock LLM invoked. Model: {self.model_name}")
        
        # Determine which node is invoking the LLM based on system/user content
        prompt_combined = (system_prompt + "\n" + user_prompt).lower()
        
        # 1. Planner Agent
        if "planner" in prompt_combined:
            return self._handle_planner(user_prompt)
            
        # 2. Search Agent
        elif "search agent" in prompt_combined or "searcher" in prompt_combined:
            return self._handle_searcher(user_prompt)
            
        # 3. Source Evaluator Agent
        elif "source evaluator" in prompt_combined:
            return self._handle_evaluator(user_prompt)
            
        # 4. Reader/Extractor Agent
        elif "extractor" in prompt_combined or "key factual claims" in prompt_combined:
            return self._handle_extractor(user_prompt)
            
        # 5. Verifier Agent
        elif "verifier" in prompt_combined or "cross-check claims" in prompt_combined:
            return self._handle_verifier(user_prompt)
            
        # 6. Writer Agent
        elif "writer" in prompt_combined:
            return self._handle_writer(user_prompt)
            
        # 7. Critic Agent
        elif "critic" in prompt_combined:
            return self._handle_critic(user_prompt)
            
        # Generic fallback
        return MockResponse("Approved or completed task successfully.")

    def _handle_planner(self, prompt: str) -> Any:
        query = prompt.lower()
        if "solid-state" in query or "solid state" in query or "battery" in query:
            questions = [
                "What is the current technological state of solid-state batteries vs lithium-ion batteries in 2026?",
                "What are the comparative manufacturing costs and economic tradeoffs of solid-state EV packs?",
                "What are the environmental lifecycle differences and safety considerations between sulfide and oxide electrolytes?",
                "What are the supply chain bottlenecks and expected timeline for mass market adoption of solid-state batteries?"
            ]
        elif "ai" in query or "artificial intelligence" in query or "agent" in query:
            questions = [
                "What is the performance difference between multi-agent graphs and single-prompt agent systems in 2026?",
                "How do verification layers affect hallucination rates in research assistants?",
                "What are the latency and cost tradeoffs of implementing iterative Writer-Critic loops?"
            ]
        else:
            questions = [
                f"What is the background and definition of {prompt.strip()}?",
                f"What is the current state and latest developments of {prompt.strip()} in 2026?",
                f"What are the primary controversies, limitations, or risks of {prompt.strip()}?"
            ]
        return MockResponse(json.dumps(questions))

    def _handle_searcher(self, prompt: str) -> Any:
        # Extract the sub-question
        sub_q = prompt.strip()
        # Create queries
        queries = [
            f"{sub_q} research study 2026",
            f"{sub_q} data facts controversies"
        ]
        return MockResponse(json.dumps(queries))

    def _handle_evaluator(self, prompt: str) -> Any:
        # Prompt contains search results, parse or mock
        evals = []
        # Check URLs in prompt
        if "nature-ecology-reviews" in prompt:
            evals.append({"url": "https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts", "score": 9, "reason": "Academic publisher, peer-reviewed, high authority on environmental science."})
        if "evtechjournal" in prompt:
            evals.append({"url": "https://www.evtechjournal.com/solid-state-batteries-2026", "score": 8, "reason": "Established industry tech journal, highly recent details for 2026."})
        if "cleanenergyfinance" in prompt:
            evals.append({"url": "https://www.cleanenergyfinance.org/reports/ev-battery-economics", "score": 8, "reason": "Reputable finance think tank, detailed cost analysis."})
        if "batterycostwatch" in prompt:
            evals.append({"url": "https://www.batterycostwatch.com/lithium-ion-2026", "score": 7, "reason": "Niche analytics firm, good recency and data coverage."})
        if "aiarchitecture" in prompt:
            evals.append({"url": "https://www.aiarchitecture.io/langgraph-performance", "score": 8, "reason": "Specialized developer blog, clear code-level telemetry."})
        if "enterprisetech" in prompt:
            evals.append({"url": "https://www.enterprisetech.com/agentic-ai-research-2026", "score": 7, "reason": "Enterprise software review outlet, moderate bias but high authority."})
            
        # Add generic URL score if list empty
        if not evals:
            evals.append({"url": "https://www.academicsciencepress.org/article-9912", "score": 8, "reason": "Academic press, high authority, peer reviewed."})
            evals.append({"url": "https://www.industryinsights.co/reports/future-outlook", "score": 5, "reason": "Market research report, moderate commercial bias."})
            
        return MockResponse(json.dumps(evals))

    def _handle_extractor(self, prompt: str) -> Any:
        claims = []
        if "evtechjournal" in prompt:
            claims.extend([
                {
                    "claim": "Sulfide-based solid-state cells reach cell-level energy densities of 480 Wh/kg to 510 Wh/kg in prototype testing, roughly double standard lithium-ion cells.",
                    "source_url": "https://www.evtechjournal.com/solid-state-batteries-2026",
                    "support_note": "Recent tests show prototype sulfide-based solid-state cells reaching energy densities of 480 Wh/kg to 510 Wh/kg"
                },
                {
                    "claim": "Solid-state battery packs cost approximately $300/kWh in 2026 due to raw material limits and strict dry-room requirements.",
                    "source_url": "https://www.evtechjournal.com/solid-state-batteries-2026",
                    "support_note": "manufacturing solid-state battery packs at pilot-scale costs roughly $300/kWh"
                }
            ])
        elif "cleanenergyfinance" in prompt:
            claims.extend([
                {
                    "claim": "Solid-state batteries are not expected to reach cost parity with lithium-ion cells until 2030.",
                    "source_url": "https://www.cleanenergyfinance.org/reports/ev-battery-economics",
                    "support_note": "solid-state batteries will not achieve price parity with lithium-ion batteries until at least 2030"
                },
                {
                    "claim": "Lithium Iron Phosphate (LFP) pack costs have achieved massive scale, dropping to $85/kWh.",
                    "source_url": "https://www.cleanenergyfinance.org/reports/ev-battery-economics",
                    "support_note": "lithium-ion cells (specifically Lithium Iron Phosphate) pack costs at $85/kWh"
                }
            ])
        elif "nature-ecology-reviews" in prompt:
            claims.extend([
                {
                    "claim": "Oxide-based solid-state batteries have a 20% higher manufacturing carbon footprint than lithium-ion due to high-temperature sintering.",
                    "source_url": "https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts",
                    "support_note": "carbon footprint of production by 20% compared to standard lithium-ion batteries"
                },
                {
                    "claim": "Sulfide electrolytes pose environmental risks because they release toxic hydrogen sulfide gas (H2S) when exposed to moisture.",
                    "source_url": "https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts",
                    "support_note": "react to release toxic and flammable hydrogen sulfide (H2S) gas"
                }
            ])
        elif "batterycostwatch" in prompt:
            claims.extend([
                {
                    "claim": "Lithium iron phosphate (LFP) cells dominate 60% of the EV market and pack costs have stabilized at $80/kWh.",
                    "source_url": "https://www.batterycostwatch.com/lithium-ion-2026",
                    "support_note": "LFP chemistry has captured 60% of the EV market, LFP pack costs stabilized at $80/kWh"
                }
            ])
        elif "aiarchitecture" in prompt:
            claims.extend([
                {
                    "claim": "Multi-agent research pipelines on LangGraph reduce hallucinations by 85% compared to single-agent prompts.",
                    "source_url": "https://www.aiarchitecture.io/langgraph-performance",
                    "support_note": "multi-agent graph... reduces hallucinations by 85% compared to single-agent prompts"
                }
            ])
        elif "enterprisetech" in prompt:
            claims.extend([
                {
                    "claim": "Verification and source evaluation steps reduce research assistant errors by 90% in enterprise testing.",
                    "source_url": "https://www.enterprisetech.com/agentic-ai-research-2026",
                    "support_note": "verification pipeline reduces business errors by 90%"
                }
            ])
        else:
            claims.extend([
                {
                    "claim": "Current research indicates steady development in this field, with commercial products expected in limited quantities.",
                    "source_url": "https://www.academicsciencepress.org/article-9912",
                    "support_note": "consensus suggests a balanced approach to scaling"
                },
                {
                    "claim": "Industry scaling faces minor supply chain bottlenecks and cost-efficiency concerns.",
                    "source_url": "https://www.industryinsights.co/reports/future-outlook",
                    "support_note": "supply chains present barriers"
                }
            ])
        return MockResponse(json.dumps(claims))

    def _handle_verifier(self, prompt: str) -> Any:
        # Simulate grouping and checking agreements/contradictions
        # In a real run, it takes list of claims and groups them.
        groups = []
        if "solid-state" in prompt or "battery" in prompt:
            groups = [
                {
                    "topic": "Energy Density of Solid-State Cells",
                    "status": "verified",
                    "confidence": "high",
                    "claims": [
                        {"claim": "Sulfide prototype cells reach cell-level energy densities of 480-510 Wh/kg in 2026.", "source_url": "https://www.evtechjournal.com/solid-state-batteries-2026"}
                    ]
                },
                {
                    "topic": "Economic Feasibility and Costs",
                    "status": "verified",
                    "confidence": "high",
                    "claims": [
                        {"claim": "Solid-state pack costs are around $300/kWh in 2026.", "source_url": "https://www.evtechjournal.com/solid-state-batteries-2026"},
                        {"claim": "Solid-state battery pack costs are $300/kWh ($220/kWh cell + $80/kWh pack).", "source_url": "https://www.cleanenergyfinance.org/reports/ev-battery-economics"}
                    ]
                },
                {
                    "topic": "Lithium-Ion Cost Benchmarks",
                    "status": "contradiction",
                    "confidence": "low",
                    "claims": [
                        {"claim": "LFP lithium-ion packs cost $80/kWh.", "source_url": "https://www.batterycostwatch.com/lithium-ion-2026"},
                        {"claim": "LFP pack costs stabilized at $85/kWh ($55/kWh cell + $30/kWh pack).", "source_url": "https://www.cleanenergyfinance.org/reports/ev-battery-economics"}
                    ]
                },
                {
                    "topic": "Environmental H2S Gas Danger",
                    "status": "single-source",
                    "confidence": "medium",
                    "claims": [
                        {"claim": "Sulfide electrolytes release highly toxic hydrogen sulfide gas if exposed to moisture.", "source_url": "https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts"}
                    ]
                }
            ]
        elif "ai" in prompt or "agent" in prompt:
            groups = [
                {
                    "topic": "Hallucination Reduction Rates",
                    "status": "single-source",
                    "confidence": "medium",
                    "claims": [
                        {"claim": "Multi-agent LangGraph workflows reduce hallucinations by 85%.", "source_url": "https://www.aiarchitecture.io/langgraph-performance"}
                    ]
                },
                {
                    "topic": "Error Reduction in Enterprise Testing",
                    "status": "single-source",
                    "confidence": "medium",
                    "claims": [
                        {"claim": "Fact-verification pipelines reduce enterprise errors by 90%.", "source_url": "https://www.enterprisetech.com/agentic-ai-research-2026"}
                    ]
                }
            ]
        else:
            groups = [
                {
                    "topic": "General Research Findings",
                    "status": "verified",
                    "confidence": "high",
                    "claims": [
                        {"claim": "Steady development in this field is underway.", "source_url": "https://www.academicsciencepress.org/article-9912"},
                        {"claim": "The field is seeing significant investment from both public and private sectors.", "source_url": "https://www.industryinsights.co/reports/future-outlook"}
                    ]
                }
            ]
        return MockResponse(json.dumps(groups))

    def _handle_writer(self, prompt: str) -> Any:
        # Check if battery or AI is in query
        if "solid-state" in prompt or "battery" in prompt:
            report = """# DeepLens Research Report: Solid-State vs. Lithium-Ion EV Batteries (2026)

## Executive Summary
This report analyzes the environmental and economic tradeoffs of solid-state batteries (SSBs) compared to conventional lithium-ion batteries for electric vehicles in 2026. While SSBs deliver outstanding performance improvements, particularly in energy density and range, manufacturing complexities and high material costs remain substantial barriers to mass commercialization.

## Key Findings

### 1. Energy Density & range Advantages
Sulfide-based prototype solid-state cells have achieved energy densities between **480 Wh/kg and 510 Wh/kg** in cell-level testing [1]. This represents nearly double the energy density of standard high-performance lithium-ion cells, which currently average **240-280 Wh/kg** [1]. This transition allows electric vehicles to exceed **700 miles** of range on a single charge.

### 2. Economic Analysis & Cost Parity
There is a massive economic gap between the two battery architectures in 2026.
- **Solid-State Packs**: Currently cost **$300/kWh** at pilot-scale production, which includes $220/kWh for cell manufacturing and $80/kWh for pack integration [1, 2].
- **Lithium-Ion Packs**: Costs have stabilized at **$80/kWh** [3] to **$85/kWh** [2] for Lithium Iron Phosphate (LFP) chemistry due to massive scaling.
Consequently, outfitting a 100 kWh battery pack costs $30,000 for solid-state versus approximately $8,500 for LFP [2], making solid-state economically unviable for mass-market vehicles until at least **2030** [2].

### 3. Environmental & Lifecycle Impact
The environmental footprint of manufacturing depends heavily on the type of solid electrolyte:
- **Oxide-Based Electrolytes**: Require high-temperature sintering (>1000°C), increasing manufacturing energy consumption and carbon footprint by **20%** compared to lithium-ion [4].
- **Sulfide-Based Electrolytes**: Can be roll-pressed at temperatures under 200°C [4], but present a unique safety hazard. If exposed to ambient moisture, sulfides react to release **highly toxic and flammable hydrogen sulfide (H2S) gas** [4]. This requires hermetically sealed recycling processes, which current standard hydrometallurgical facilities cannot handle without upgrades [4].

## Contradictions & Open Questions
A minor contradiction exists in the literature regarding the exact price point of scaled LFP battery packs in 2026. According to *Battery Cost Watch*, LFP pack costs have stabilized at exactly **$80/kWh** [3], while the *Clean Energy Finance Institute* reports them at **$85/kWh** (consisting of $55/kWh cell cost and $30/kWh pack assembly cost) [2]. While minor, this reflects slight variations in supply-chain margins.

## Limitations
This study is limited by the proprietary nature of pilot-scale solid-state test data. Long-term cycle degradation data remains largely unavailable from manufacturers.

## References
1. [EV Technology Journal - Solid-State Battery Breakthroughs (2026)](https://www.evtechjournal.com/solid-state-batteries-2026)
2. [Clean Energy Finance Institute - The Economic Tradeoffs of Solid-State EV Fleets](https://www.cleanenergyfinance.org/reports/ev-battery-economics)
3. [Battery Cost Watch - Lithium-Ion Battery Cost Curves](https://www.batterycostwatch.com/lithium-ion-2026)
4. [Nature Ecology & Environment - Sulfide vs Oxide Solid Electrolytes Review](https://www.nature-ecology-reviews.org/sulfide-oxide-battery-impacts)
"""
        elif "ai" in prompt or "agent" in prompt:
            report = """# DeepLens Research Report: Multi-Agent Architectures vs Single-Prompt Agents (2026)

## Executive Summary
This report evaluates the performance, latency, and reliability metrics of multi-agent architectures (like LangGraph) compared to single-prompt agents for complex research tasks in 2026.

## Key Findings

### 1. Factual Reliability & Accuracy
Multi-agent graphs running structured pipelines (Planner -> Searcher -> Evaluator -> Extractor -> Verifier -> Writer -> Critic) reduce hallucination rates by **85%** compared to single-agent prompts [1]. Fact-checking across multiple independent sources reduces operational business errors by **90%** in enterprise settings [2].

### 2. State Streaming & Latency
Streaming agent actions in real time using Server-Sent Events (SSE) improves user trust and visibility [1]. However, multi-agent graphs suffer from higher latency due to sequential LLM calls, though iterative Writer-Critic feedback loops (capped at 2 iterations) balance quality against token costs [1].

## References
1. [AI Architecture Insights - Autonomous Agent Workflows & LangGraph](https://www.aiarchitecture.io/langgraph-performance)
2. [Enterprise Tech Review - State of Agentic AI in Enterprise Research Assistants](https://www.enterprisetech.com/agentic-ai-research-2026)
"""
        else:
            report = f"""# DeepLens Research Report: {prompt.strip()[:100]}

## Executive Summary
A comprehensive review of the requested topic, highlighting core findings, controversies, and future directions.

## Key Findings
- Current academic consensus suggests a balanced approach to scaling in this domain [1].
- Significant investment is flowing from both private and public sectors [2].
- Main barriers include supply chain maturity and initial capital expenditure [2].

## References
1. [Academic Science Press - Recent Studies](https://www.academicsciencepress.org/article-9912)
2. [Industry Insights Co - The Future Outlook](https://www.industryinsights.co/reports/future-outlook)
"""
        return MockResponse(report)

    def _handle_critic(self, prompt: str) -> Any:
        # Approve the report immediately in mock mode to avoid infinite loops
        return MockResponse("APPROVED")

class MockResponse:
    def __init__(self, content: str):
        self.content = content
        self.type = "ai"

def get_llm(model_name: str = "claude-3-5-sonnet-20241022", temperature: float = 0.0) -> BaseChatModel:
    """
    Returns an LLM client:
    1. ChatAnthropic if ANTHROPIC_API_KEY is present
    2. ChatGoogleGenAI if GEMINI_API_KEY is present
    3. MockChatModel otherwise
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if anthropic_key:
        logger.info("Initializing Anthropic Claude LLM client.")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name if "claude" in model_name else "claude-3-5-sonnet-20241022",
            temperature=temperature,
            anthropic_api_key=anthropic_key
        )
    elif gemini_key:
        logger.info("Initializing Google Gemini LLM client (Fallback).")
        from langchain_google_genai import ChatGoogleGenAI
        return ChatGoogleGenAI(
            model="gemini-1.5-pro" if "sonnet" in model_name else "gemini-1.5-flash",
            temperature=temperature,
            google_api_key=gemini_key
        )
    else:
        logger.warning("No API keys found. Returning MockChatModel.")
        return MockChatModel(model_name)
