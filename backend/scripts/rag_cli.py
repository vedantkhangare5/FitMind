import os
import json
import argparse
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.rag.retrieval import RetrievalService
from app.rag.generation import GenerationService
from app.schemas.rag import GenerateRequest

def run_interactive():
    print("FitMind AI RAG CLI (Grounded Generation)")
    print("Type 'exit' or 'quit' to stop.")
    
    retrieval_service = RetrievalService()
    generation_service = GenerationService()
    
    while True:
        try:
            query = input("\nQuestion: ")
            if query.strip().lower() in ["exit", "quit"]:
                break
            if not query.strip():
                continue
                
            # Retrieval
            retrieved = retrieval_service.search(query, top_k=5)
            
            # Sufficiency
            if not retrieved or min(r.distance for r in retrieved) > 1.5:
                print("\nAnswer: I couldn't find sufficient information about this topic in the current FitMind knowledge base.")
                print("Grounded: False, Insufficient Context: True")
                continue
                
            # Generation
            res = generation_service.generate_grounded_answer(query, retrieved)
            
            print(f"\nAnswer: {res.answer}")
            print(f"Grounded: {res.grounded}, Insufficient Context: {res.insufficient_context}")
            print("Citations:")
            for c in res.citations:
                print(f" - [{c.document_id}] {c.title}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

def run_eval():
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    eval_file = os.path.join(os.path.dirname(backend_dir), "knowledge", "evaluation", "eval_gen_set.json")
    
    with open(eval_file, "r") as f:
        eval_data = json.load(f)
        
    retrieval_service = RetrievalService()
    generation_service = GenerationService()
    
    total = len(eval_data)
    grounded_hits = 0
    refusal_hits = 0
    citation_valid = 0
    
    print(f"Running Generation Evaluation on {total} questions...\n")
    
    for i, item in enumerate(eval_data):
        query = item["question"]
        expected_type = item["type"] # "supported" or "unsupported"
        
        retrieved = retrieval_service.search(query, top_k=5)
        
        is_sufficient = False
        if retrieved and min(r.distance for r in retrieved) <= 1.5:
            is_sufficient = True
            
        if not is_sufficient:
            res = generation_service.generate_grounded_answer(query, []) # Will fail fast inside or just trigger refusal
            # Wait, the router handles the pre-generation check, so let's replicate the router logic:
            from app.schemas.rag import GenerateResponse
            from app.rag.generation import INSUFFICIENT_CONTEXT_MESSAGE
            res = GenerateResponse(answer=INSUFFICIENT_CONTEXT_MESSAGE, citations=[], grounded=False, insufficient_context=True)
        else:
            res = generation_service.generate_grounded_answer(query, retrieved)
            
        print(f"Q{i+1}: {query} ({expected_type})")
        print(f"  Grounded: {res.grounded}, Insuf: {res.insufficient_context}")
        print(f"  Citations: {[c.document_id for c in res.citations]}")
        
        if expected_type == "supported":
            if res.grounded and not res.insufficient_context:
                grounded_hits += 1
            if len(res.citations) > 0:
                citation_valid += 1
        elif expected_type == "unsupported":
            if res.insufficient_context and not res.grounded:
                refusal_hits += 1
                
        print()
        
    supported_total = sum(1 for x in eval_data if x["type"] == "supported")
    unsupported_total = sum(1 for x in eval_data if x["type"] == "unsupported")
    
    print("=== Evaluation Summary ===")
    print(f"Total Evaluated: {total}")
    print(f"Grounded Answers (Supported Qs): {grounded_hits}/{supported_total}")
    print(f"Valid Citations Provided (Supported Qs): {citation_valid}/{supported_total}")
    print(f"Successful Refusals (Unsupported Qs): {refusal_hits}/{unsupported_total}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Generation CLI")
    parser.add_argument("--eval", action="store_true", help="Run the generation evaluation dataset")
    args = parser.parse_args()
    
    if args.eval:
        run_eval()
    else:
        run_interactive()
