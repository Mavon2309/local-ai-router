import os
import sys
import json
import time
from collections import defaultdict

# Add project root to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

# Centralized config imports
from config import TEST_PROMPTS_V2

# Router import
from router_v3 import classify


def run_tests():
    with open(TEST_PROMPTS_V2, "r", encoding="utf-8") as f:
        tests = json.load(f)

    total = len(tests)
    correct = 0
    timings = []

    confusion = defaultdict(lambda: defaultdict(int))
    route_counts = defaultdict(int)

    print("=" * 80)
    print("LOCAL AI ROUTER TEST SUITE V2")
    print("=" * 80)

    for i, item in enumerate(tests, start=1):
        prompt = item["prompt"]
        expected = item["expected"]

        start = time.perf_counter()
        result = classify(prompt)
        elapsed = (time.perf_counter() - start) * 1000

        actual = result[0]
        timings.append(elapsed)

        confusion[expected][actual] += 1
        route_counts[actual] += 1

        passed = actual == expected
        if passed:
            correct += 1

        status = "PASS" if passed else "FAIL"

        print(f"\n{i}. {status} | {elapsed:.2f} ms")
        print("Prompt:   ", prompt)
        print("Expected: ", expected)
        print("Actual:   ", actual)
        print("Meta:     ", result)

    accuracy = (correct / total) * 100
    avg_ms = sum(timings) / len(timings)
    max_ms = max(timings)
    min_ms = min(timings)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Score: {correct}/{total} ({accuracy:.2f}%)")
    print(f"Avg classify time: {avg_ms:.2f} ms")
    print(f"Min classify time: {min_ms:.2f} ms")
    print(f"Max classify time: {max_ms:.2f} ms")

    print("\nROUTE DISTRIBUTION")
    for k, v in sorted(route_counts.items()):
        print(f"{k:12}: {v}")

    labels = ["general", "coding", "math", "writing", "reasoning"]

    print("\nCONFUSION MATRIX (expected -> predicted)")
    header = " " * 14 + "".join(f"{x:12}" for x in labels)
    print(header)

    for exp in labels:
        row = f"{exp:14}"
        for pred in labels:
            row += f"{confusion[exp][pred]:12}"
        print(row)

if __name__ == "__main__":
    run_tests()