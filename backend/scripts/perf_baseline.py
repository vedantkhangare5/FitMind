import os
import sys
import time
import json
import logging
from typing import List, Dict

# Setup paths and environment
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env.local"))
load_dotenv(os.path.join(backend_dir, ".env"))

# Disable logging to keep output clean
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("app").setLevel(logging.WARNING)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def calculate_stats(times: List[float]) -> Dict[str, float]:
    if not times:
        return {"min": 0, "max": 0, "avg": 0, "p95": 0}
    
    sorted_times = sorted(times)
    n = len(sorted_times)
    avg = sum(sorted_times) / n
    
    # Calculate p95 index (nearest rank)
    p95_idx = int(round(n * 0.95)) - 1
    if p95_idx < 0:
        p95_idx = 0
    elif p95_idx >= n:
        p95_idx = n - 1
        
    p95 = sorted_times[p95_idx]
    
    return {
        "min": sorted_times[0],
        "max": sorted_times[-1],
        "avg": avg,
        "p95": p95
    }

def print_stats(name: str, stats: Dict[str, float]):
    if stats["avg"] == 0:
        return
    print(f"  {name}:")
    print(f"    Min: {stats['min']:.2f}ms")
    print(f"    Max: {stats['max']:.2f}ms")
    print(f"    Avg: {stats['avg']:.2f}ms")
    print(f"    P95: {stats['p95']:.2f}ms")

def run_baseline(n: int = 5):
    print(f"Running Performance Baseline (N={n})...")
    
    # 1. /api/health
    print("\n--- /api/health ---")
    health_times = []
    for _ in range(n):
        start = time.time()
        res = client.get("/api/health")
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        health_times.append(duration)
    print_stats("Total Request Time", calculate_stats(health_times))
    
    # 2. /api/fitness/calculate
    print("\n--- /api/fitness/calculate ---")
    calc_times = []
    payload = {
        "age": 30,
        "sex": "male",
        "weight_kg": 80.0,
        "height_cm": 180.0,
        "activity_level": "moderately_active",
        "goal": "build_muscle"
    }
    for _ in range(n):
        start = time.time()
        res = client.post("/api/fitness/calculate", json=payload)
        if res.status_code != 200:
            print(f"  Error: {res.status_code} - {res.text}")
            continue
        duration = (time.time() - start) * 1000
        calc_times.append(duration)
    print_stats("Total Request Time", calculate_stats(calc_times))
    
    # 3. /api/rag/search
    print("\n--- /api/rag/search ---")
    search_times = []
    for _ in range(n):
        start = time.time()
        res = client.post("/api/rag/search", json={"query": "What is the recommended protein intake?", "top_k": 3})
        duration = (time.time() - start) * 1000
        assert res.status_code == 200
        search_times.append(duration)
    print_stats("Total Request Time (includes retrieval)", calculate_stats(search_times))
    
    # 4. /api/agent/ask
    print("\n--- /api/agent/ask ---")
    agent_total_times = []
    agent_tool_times = []
    agent_generation_times = [] # We can infer this roughly
    
    queries = [
        "What is my BMI?", # Will use tool
        "How much protein do I need?", # Will use RAG
        "Summarize my progress.", # Will use progress tool
        "Hello", # Will likely just answer
        "Calculate TDEE for me." # Will use calculate_tdee tool
    ]
    
    # Ensure profile exists for these queries
    from app.database import ProfileRepository
    repo = ProfileRepository()
    repo.save_profile(age=30, sex="male", height_cm=180, weight_kg=80, activity_level="sedentary", goal="lose_fat")
    
    for i in range(min(n, len(queries))):
        start = time.time()
        res = client.post("/api/agent/ask", json={"query": queries[i]})
        duration = (time.time() - start) * 1000
        
        if res.status_code != 200:
            print(f"  Request {i+1} failed with status {res.status_code}")
            continue
            
        data = res.json()
        agent_total_times.append(duration)
        
        # Extract internal tool times
        tool_time_sum = 0
        if "tool_calls" in data:
            for call in data["tool_calls"]:
                if "duration_ms" in call and call["duration_ms"]:
                    agent_tool_times.append(call["duration_ms"])
                    tool_time_sum += call["duration_ms"]
                    
        # Infer generation time (total - tool time)
        # It's not perfect but gives a sense of LLM + overhead
        inferred_gen_time = duration - tool_time_sum
        agent_generation_times.append(inferred_gen_time)

    print_stats("Total Request Time", calculate_stats(agent_total_times))
    if agent_tool_times:
        print_stats("Tool Execution Time (per call)", calculate_stats(agent_tool_times))
    print_stats("Generation/Overhead Time", calculate_stats(agent_generation_times))

if __name__ == "__main__":
    run_baseline()
