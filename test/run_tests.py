import json
import time
import os
from collections import Counter, defaultdict
from datetime import datetime

from router import classify
from config import get_dataset_path, DEFAULT_DATASET, RESULTS_DIR


# =====================================
# LOAD TESTS
# =====================================
def load_tests(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =====================================
# EVALUATION CORE
# =====================================
def evaluate(tests, dataset_name):
    total = len(tests)
    correct = 0
    timings = []

    route_counter = Counter()
    confusion = defaultdict(lambda: defaultdict(int))
    failures = []

    print("=" * 70)
    print(f"RUNNING DATASET: {dataset_name}")
    print("=" * 70)

    for i, t in enumerate(tests, 1):
        prompt = t["prompt"]
        expected = t["expected"]

        start = time.time()
        label, conf, source = classify(prompt)
        elapsed = round((time.time() - start) * 1000, 2)

        timings.append(elapsed)
        route_counter[label] += 1
        confusion[expected][label] += 1

        status = "PASS" if label == expected else "FAIL"

        if status == "PASS":
            correct += 1
        else:
            failures.append({
                "prompt": prompt,
                "expected": expected,
                "actual": label,
                "confidence": conf,
                "source": source
            })

        print(f"{i}. {status} | {elapsed} ms")
        print(f"Prompt:   {prompt}")
        print(f"Expected: {expected}")
        print(f"Actual:   {label}")
        print(f"Meta:     ({label}, {conf}, {source})\n")

    accuracy = round((correct / total) * 100, 2)

    # =====================================
    # SUMMARY
    # =====================================
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Score: {correct}/{total} ({accuracy}%)")
    print(f"Avg time: {round(sum(timings)/len(timings),2)} ms")
    print(f"Min time: {min(timings)} ms")
    print(f"Max time: {max(timings)} ms\n")

    print("ROUTE DISTRIBUTION")
    for k, v in route_counter.items():
        print(f"{k:10}: {v}")

    print("\nCONFUSION MATRIX")
    labels = ["general", "coding", "math", "writing", "reasoning"]
    print(f"{'':12}" + "".join(f"{l:12}" for l in labels))

    for exp in labels:
        row = f"{exp:12}"
        for pred in labels:
            row += f"{confusion[exp][pred]:12}"
        print(row)

    # =====================================
    # SAVE RESULTS
    # =====================================
    os.makedirs(RESULTS_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # latest summary
    with open(os.path.join(RESULTS_DIR, "latest.txt"), "w") as f:
        f.write(f"Dataset: {dataset_name}\n")
        f.write(f"Accuracy: {accuracy}%\n")
        f.write(f"Total: {total}\n")

    # historical log
    with open(os.path.join(RESULTS_DIR, f"run_{timestamp}.txt"), "w") as f:
        f.write(f"Dataset: {dataset_name}\n")
        f.write(f"Accuracy: {accuracy}%\n")
        f.write(f"Total: {total}\n")

    # failure log (VERY useful)
    if failures:
        with open(os.path.join(RESULTS_DIR, f"failures_{timestamp}.json"), "w") as f:
            json.dump(failures, f, indent=2)

    print("\nSaved results to:", RESULTS_DIR)

    return accuracy


# =====================================
# MAIN ENTRY
# =====================================
def main():
    dataset = input(f"Dataset (default={DEFAULT_DATASET}): ").strip()
    dataset = dataset if dataset else DEFAULT_DATASET

    path = get_dataset_path(dataset)

    if not os.path.exists(path):
        print(f"Dataset not found: {path}")
        return

    tests = load_tests(path)
    evaluate(tests, dataset)


if __name__ == "__main__":
    main()