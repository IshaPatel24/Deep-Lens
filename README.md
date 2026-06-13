# DeepLens: Autonomous Research Assistant
### Agentic AI Hackathon 2026 — Top 1% Build (PS-02 Target)

DeepLens is a multi-agent autonomous research assistant built on **FastAPI**, **LangGraph (Python)**, and **React**. It translates any natural-language query into a cited, cross-verified, and multi-perspective research report without human steering.

---

## 1. System Architecture

```
                       User Query
                           │
                           ▼
                 [Planner Agent (Node)]
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Sub-Quest 1   Sub-Quest 2   Sub-Quest 3   (Search Angles)
             │             │             │
             ├─────────────┴─────────────┤
             ▼                           ▼
    [Search Agent] generates 2-3 queries per angle
             │
             ▼
   [Source Evaluator] scores sources (0-10) on Authority/Recency/Bias
             │ (Discards URLs scored < 4)
             ▼
    [Extractor Agent] fetches pages (trafilatura) & extracts raw claims
             │
             ▼
    [Verifier Agent] cross-checks claims, identifies contradictions
             │
             ▼
     [Writer Agent] compiles cited Markdown draft report
             │
             ▼
     [Critic Agent] audits citations, neutrality, and hallucinations
             │
             ├─── (If edits flagged: Loops back to Writer, Max 2 Iterations)
             ▼
       Final Report + References + Confidence Map Explorer
```

---

## 2. Key Capabilities (PS-02 Features)

1. **Multi-Agent State Pipeline**: State orchestration uses LangGraph to coordinate distinct nodes (Planner, Searcher, Evaluator, Extractor, Verifier, Writer, Critic).
2. **Source Reliability Filtering**: The Source Evaluator scores domains and snippets, discarding URLs scoring below 4/10 to avoid low-quality blog posts and SEO-spam.
3. **Contradiction Verification**: The Verifier groups facts by topic. If independent sources conflict, it labels the fact as a `contradiction` and maps both versions side-by-side.
4. **SSE Real-Time Trace**: Streams step-by-step logs from active agents using Server-Sent Events, enabling the user to watch agents think live.
5. **Interactive Confidence Map**: Highlighting claims dynamically based on verification status (High/Medium/Low confidence).
6. **One-Click Export**: Downloader converting Markdown to formatted PDF and Microsoft Word (DOCX) files.
7. **Rigorous Evaluation Suite**: A local `benchmark.json` and metric runner measuring Citation Accuracy and Claim Recall.

---

## 3. How this fulfills PS-02

| PS-02 Requirement | DeepLens Component / Implementation | File / Link |
|---|---|---|
| **Autonomous Query Handling** | Planner breaks queries into non-overlapping sub-questions. | [`planner.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/agents/planner.py) |
| **Multi-Source Search** | Searcher expands keywords; queries Tavily/SerpAPI/DuckDuckGo. | [`search_tool.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/tools/search_tool.py) |
| **Unreliable Content Filtering** | Evaluator scores sources on Authority/Bias, filtering out low scores. | [`evaluator.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/agents/evaluator.py) |
| **Factual Claim Verification** | Extractor collects claims; Verifier checks agreement/conflicts. | [`verifier.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/agents/verifier.py) |
| **Structured Cited Report** | Writer synthesizes report; Critic enforces verification loop. | [`writer.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/agents/writer.py) |
| **Evaluation Mode** | Run suite against benchmark facts, outputs citation precision. | [`run_eval.py`](file:///Users/yogeshmodi/Desktop/hackathon/backend/eval/run_eval.py) |

---

## 4. Setup & Running Instructions

### Prerequisites
- macOS, Linux, or Windows (with bash/Git)
- Python 3.12+ (Homebrew installed is recommended)
- Node.js v20+ & npm

### Backend Setup
1. Navigate to `/backend`:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the environment variables:
   ```bash
   cp .env.template .env
   # Add your API keys to .env (Optional: runs with mock fallbacks if empty!)
   ```
5. Run the FastAPI server:
   ```bash
   python main.py
   # Runs server at http://localhost:8000
   ```

### Frontend Setup
1. Navigate to `/frontend`:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   # Runs dashboard at http://localhost:5173
   ```
