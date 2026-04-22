import os
import sys
import json
import time
from collections import Counter

# Add project root to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Centralized config imports
from config import TEST_PROMPTS_V2

# Router imports
from router_v3 import classify, ROUTES

# Shared prompts file path
PROMPTS_FILE = TEST_PROMPTS_V2


def dashboard():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        tests = json.load(f)

    times = []
    routes = []
    sources = []

    for item in tests:
        prompt = item["prompt"]

        start = time.perf_counter()
        label, conf, source = classify(prompt)
        elapsed = (time.perf_counter() - start) * 1000

        times.append(elapsed)
        routes.append(label)
        sources.append(source)

    route_counter = Counter(routes)
    source_counter = Counter(sources)

    print("=" * 80)
    print("ROUTER PERFORMANCE DASHBOARD")
    print("=" * 80)

    print(f"Total Prompts Tested: {len(tests)}")
    print(f"Average Classification Time: {sum(times)/len(times):.2f} ms")
    print(f"Fastest Classification: {min(times):.2f} ms")
    print(f"Slowest Classification: {max(times):.2f} ms")

    print("\nROUTES USED")
    for k, v in route_counter.items():
        print(f"{k:12}: {v:3} -> {ROUTES.get(k)}")

    print("\nDECISION SOURCE")
    for k, v in source_counter.items():
        print(f"{k:12}: {v}")

    print("\nESTIMATED LIVE SPEED")
    for route, model in ROUTES.items():
        if "14b" in model.lower():
            speed = "Slow / heavy"
        elif "7b" in model.lower():
            speed = "Medium"
        else:
            speed = "Fast"
        print(f"{route:12}: {model:20} {speed}")

if __name__ == "__main__":
    dashboard()