import os
import json
import argparse
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.rag.retrieval import RetrievalService
from app.rag.generation import GenerationService, INSUFFICIENT_CONTEXT_MESSAGE
from app.schemas.rag import GenerateResponse

def run_benchmark():
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    eval_file = os.path.join(os.path.dirname(backend_dir), "knowledge", "evaluation", "benchmark_v1.json")
    
    with open(eval_file, "r") as f:
        eval_data = json.load(f)
        
    retrieval_service = RetrievalService()
    generation_service = GenerationService()
    
    total = len(eval_data)
    
    # Retrieval Metrics
    top_1_hits = 0
    top_3_hits = 0
    recall_k_sum = 0.0
    
    # Generation Metrics
    grounded_hits = 0
    citation_correct_hits = 0
    refusal_hits = 0
    
    supported_total = 0
    unsupported_total = 0
    
    print(f"Running Benchmark on {total} questions...\n")
    
    for i, item in enumerate(eval_data):
        query = item["question"]
        expected_type = item["type"] # "supported" or "unsupported"
        expected_ids = set(item["expected_document_ids"])
        
        # 1. Retrieval Phase
        retrieved = retrieval_service.search(query, top_k=5)
        retrieved_ids = [r.document_id for r in retrieved]
        
        # Calculate Retrieval Metrics
        if expected_ids:
            # Top-1
            if retrieved_ids and retrieved_ids[0] in expected_ids:
                top_1_hits += 1
            # Top-3
            if any(rid in expected_ids for rid in retrieved_ids[:3]):
                top_3_hits += 1
            # Recall@5
            found = sum(1 for eid in expected_ids if eid in retrieved_ids)
            recall_k_sum += found / len(expected_ids)
            
        # 2. Sufficiency Check & Generation
        is_sufficient = False
        if retrieved and min(r.distance for r in retrieved) <= 1.5:
            is_sufficient = True
            
        if not is_sufficient:
            res = GenerateResponse(answer=INSUFFICIENT_CONTEXT_MESSAGE, citations=[], grounded=False, insufficient_context=True)
        else:
            try:
                res = generation_service.generate_grounded_answer(query, retrieved)
            except Exception as e:
                print(f"Error on Q{i+1}: {e}")
                res = GenerateResponse(answer=str(e), citations=[], grounded=False, insufficient_context=True)
                
        # Calculate Generation Metrics
        if expected_type == "supported":
            supported_total += 1
            if res.generation_error:
                print(f"Error on Q{i+1}: Generation failed with code {res.error_code}")
            elif res.grounded and not res.insufficient_context:
                grounded_hits += 1
                
                cited_ids = set(c.document_id for c in res.citations)
                if cited_ids and any(cid in expected_ids for cid in cited_ids):
                    citation_correct_hits += 1
                    
        elif expected_type == "unsupported":
            unsupported_total += 1
            if res.generation_error:
                print(f"Error on Q{i+1}: Generation failed with code {res.error_code}")
            elif res.insufficient_context and not res.grounded:
                refusal_hits += 1
                
        print(f"Q{i+1}: {query[:50]}... ({expected_type})")
        print(f"  Retrieval -> Top-1: {retrieved_ids[0] in expected_ids if expected_ids and retrieved_ids else False}")
        print(f"  Generation -> Grounded: {res.grounded}, Refusal: {res.insufficient_context}, Error: {res.generation_error}")
    
    # Final Scores
    print("\n" + "="*50)
    print("           BENCHMARK RESULTS")
    print("="*50)
    print("--- RETRIEVAL METRICS ---")
    if supported_total > 0:
        print(f"Top-1 Accuracy:       {top_1_hits / supported_total * 100:.1f}%")
        print(f"Top-3 Accuracy:       {top_3_hits / supported_total * 100:.1f}%")
        print(f"Recall@5 (Avg):       {recall_k_sum / supported_total * 100:.1f}%")
    else:
        print("No supported questions to calculate retrieval.")
        
    print("\n--- GENERATION METRICS ---")
    if supported_total > 0:
        print(f"Groundedness Rate:    {grounded_hits / supported_total * 100:.1f}%")
        print(f"Citation Correctness: {citation_correct_hits / supported_total * 100:.1f}%")
    if unsupported_total > 0:
        print(f"Refusal Accuracy:     {refusal_hits / unsupported_total * 100:.1f}%")
    
    # Save Report
    report_path = os.path.join(os.path.dirname(backend_dir), "knowledge", "evaluation", "benchmark_report.md")
    with open(report_path, "w") as f:
        f.write("# Phase 4 Benchmark Report\n\n")
        f.write("## Retrieval Metrics\n")
        if supported_total > 0:
            f.write(f"- **Top-1 Accuracy**: {top_1_hits / supported_total * 100:.1f}%\n")
            f.write(f"- **Top-3 Accuracy**: {top_3_hits / supported_total * 100:.1f}%\n")
            f.write(f"- **Recall@5**: {recall_k_sum / supported_total * 100:.1f}%\n\n")
        f.write("## Generation Metrics\n")
        f.write("> **WARNING**: Generation metrics are NOT valid performance measurements because API 429 rate limits contaminated the evaluation.\n\n")
        if supported_total > 0:
            f.write(f"- **Groundedness**: {grounded_hits / supported_total * 100:.1f}%\n")
            f.write(f"- **Citation Correctness**: {citation_correct_hits / supported_total * 100:.1f}%\n")
        if unsupported_total > 0:
            f.write(f"- **Refusal Accuracy**: {refusal_hits / unsupported_total * 100:.1f}%\n\n")
        f.write("*(Note: This benchmark measures system behavior organically and is not a target for direct optimization.)*\n")
        
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 4 Evaluation Benchmark")
    args = parser.parse_args()
    run_benchmark()
