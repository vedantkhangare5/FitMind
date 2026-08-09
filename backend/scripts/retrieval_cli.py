import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.rag.retrieval import RetrievalService

def run_interactive():
    print("FitMind AI Retrieval CLI")
    print("Type 'exit' or 'quit' to stop.")
    service = RetrievalService()
    
    while True:
        try:
            query = input("\nQuery: ")
            if query.strip().lower() in ["exit", "quit"]:
                break
            if not query.strip():
                continue
                
            results = service.search(query, top_k=3)
            
            for i, res in enumerate(results):
                print(f"\nRank {i+1}:")
                print(f"Source: {res.document_id}")
                print(f"Title: {res.title}")
                print(f"Score: {res.distance:.4f}")
                print(f"Text: {res.text[:200]}...")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def run_eval():
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    eval_file = os.path.join(os.path.dirname(backend_dir), "knowledge", "evaluation", "eval_set.json")
    
    with open(eval_file, "r") as f:
        eval_data = json.load(f)
        
    service = RetrievalService()
    
    total = len(eval_data)
    top_1_hits = 0
    top_3_hits = 0
    
    print(f"Running Evaluation on {total} questions...\n")
    
    for i, item in enumerate(eval_data):
        query = item["question"]
        expected_ids = item["expected_document_ids"]
        
        results = service.search(query, top_k=3)
        retrieved_ids = [res.document_id for res in results]
        
        # Check Top 1
        is_top_1 = len(retrieved_ids) > 0 and retrieved_ids[0] in expected_ids
        if is_top_1:
            top_1_hits += 1
            
        # Check Top 3
        is_top_3 = any(rid in expected_ids for rid in retrieved_ids)
        if is_top_3:
            top_3_hits += 1
            
        print(f"Q{i+1}: {query}")
        print(f"  Expected: {expected_ids}")
        print(f"  Retrieved: {retrieved_ids}")
        print(f"  Top-1: {'PASS' if is_top_1 else 'FAIL'}, Top-3: {'PASS' if is_top_3 else 'FAIL'}\n")
        
    print("=== Evaluation Summary ===")
    print(f"Questions evaluated: {total}")
    print(f"Expected source retrieved in Top-1: {top_1_hits}/{total} ({top_1_hits/total*100:.1f}%)")
    print(f"Expected source retrieved in Top-3: {top_3_hits}/{total} ({top_3_hits/total*100:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieval CLI")
    parser.add_argument("--eval", action="store_true", help="Run the evaluation dataset")
    args = parser.parse_args()
    
    if args.eval:
        run_eval()
    else:
        run_interactive()
