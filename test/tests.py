import os
import sys
import json

# Add project root to Python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from config import TEST_PROMPTS_V1
from router_v3 import classify

# Centralized prompts file from config.py
PROMPTS_FILE = TEST_PROMPTS_V1


def run_tests():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        tests = json.load(f)

    total = len(tests)
    correct = 0

    print("=" * 70)
    print("LOCAL AI ROUTER TEST SUITE")
    print("=" * 70)

    for i, item in enumerate(tests, start=1):
        prompt = item["prompt"]
        expected = item["expected"]

        result = classify(prompt)
        actual = result[0]

        passed = actual == expected

        if passed:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"

        print(f"\n{i}. {status}")
        print("Prompt:   ", prompt)
        print("Expected: ", expected)
        print("Actual:   ", actual)
        print("Meta:     ", result)

    accuracy = round((correct / total) * 100, 2)

    print("\n" + "=" * 70)
    print(f"Score: {correct}/{total} ({accuracy}%)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()