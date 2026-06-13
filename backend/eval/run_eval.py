import os
import json
import time
import asyncio
import re
import logging
from typing import Dict, List, Any
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph import run_research_pipeline
from backend.db import init_db, save_eval

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_citation_score(report: str) -> float:
    """
    Computes a citation score (0.0 to 1.0) based on:
    1. Presence of a References section.
    2. Format of inline citation markers (e.g. [1], [2]).
    3. Alignment between inline citations and the References list.
    """
    report_lower = report.lower()
    if "references" not in report_lower:
        return 0.0

    # Find all inline citations [1], [2], etc.
    citations = re.findall(r'\[(\d+)\]', report)
    if not citations:
        return 0.0

    # Find reference list item numbers like "1. ", "2. " or "[1] "
    ref_list = re.findall(r'(?:^|\n)(?:\[?(\d+)\]?[\.\:\s])', report)
    
    if not ref_list:
        return 0.5 # Has references header and inline citations, but references format is weird

    # Convert to sets of integers
    citation_ints = {int(x) for x in citations}
    ref_ints = {int(x) for x in ref_list}

    # Verify if every cited item exists in reference list
    valid_citations = citation_ints.intersection(ref_ints)
    if not citation_ints:
        return 0.0
        
    accuracy = len(valid_citations) / len(citation_ints)
    return accuracy

def compute_coverage_score(report: str, ground_truth_facts: List[str]) -> float:
    """
    Computes claim coverage/recall (0.0 to 1.0) based on text matching keywords of ground truth facts.
    """
    report_lower = report.lower()
    matches = 0
    
    for fact in ground_truth_facts:
        # Extract alphanumeric words longer than 3 characters as keywords
        keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', fact)]
        if not keywords:
            # Fallback if short words only
            keywords = [w.lower() for w in re.split(r'\s+', fact) if w]
            
        # Count how many keywords appear in the report
        match_count = sum(1 for kw in keywords if kw in report_lower)
        
        # If more than 60% of keywords match, we count this fact as covered
        if keywords and (match_count / len(keywords)) >= 0.6:
            matches += 1
            
    return matches / len(ground_truth_facts) if ground_truth_facts else 0.0

async def run_benchmark():
    init_db()
    
    benchmark_path = os.path.join(os.path.dirname(__file__), "benchmark.json")
    if not os.path.exists(benchmark_path):
        logger.error(f"Benchmark file not found at {benchmark_path}")
        return

    with open(benchmark_path, "r") as f:
        questions = json.load(f)

    logger.info(f"Running evaluation benchmark on {len(questions)} questions...")
    results = []
    
    total_citation_score = 0.0
    total_coverage_score = 0.0
    start_time_all = time.time()
    
    # Null publisher for intermediate steps during evaluation
    async def dummy_publisher(msg):
        pass

    for item in questions:
        q_id = item["id"]
        question = item["question"]
        gt_facts = item["ground_truth_facts"]
        
        logger.info(f"Evaluating Q: {question}")
        session_id = f"eval_{q_id}_{int(time.time())}"
        
        start_time = time.time()
        try:
            state = await run_research_pipeline(question, session_id, dummy_publisher)
            latency = time.time() - start_time
            
            report = state.report
            citation_score = compute_citation_score(report)
            coverage_score = compute_coverage_score(report, gt_facts)
            
            total_citation_score += citation_score
            total_coverage_score += coverage_score
            
            results.append({
                "id": q_id,
                "question": question,
                "latency_seconds": round(latency, 2),
                "citation_accuracy": round(citation_score * 100, 1),
                "claim_coverage": round(coverage_score * 100, 1)
            })
            
            logger.info(f"Q: {q_id} complete. Citation Acc: {citation_score*100}%, Coverage: {coverage_score*100}%")
        except Exception as e:
            logger.error(f"Failed to evaluate question {q_id}: {e}")
            results.append({
                "id": q_id,
                "question": question,
                "error": str(e)
            })

    total_latency = time.time() - start_time_all
    avg_citation = total_citation_score / len(questions) if questions else 0.0
    avg_coverage = total_coverage_score / len(questions) if questions else 0.0
    
    eval_summary = {
        "timestamp": time.time(),
        "score_citation": round(avg_citation * 100, 1),
        "score_coverage": round(avg_coverage * 100, 1),
        "latency_seconds": round(total_latency, 2),
        "details": results
    }
    
    # Save to DB
    save_eval(avg_citation, avg_coverage, total_latency, eval_summary)
    
    # Write to local file for direct frontend reading
    results_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(results_path, "w") as f:
        json.dump(eval_summary, f, indent=2)
        
    logger.info(f"Benchmark run complete. Avg Citation: {avg_citation*100}%, Avg Coverage: {avg_coverage*100}%")
    return eval_summary

if __name__ == "__main__":
    asyncio.run(run_benchmark())
