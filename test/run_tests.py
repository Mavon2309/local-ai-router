import json
import time
import os
from collections import Counter, defaultdict
from router import classify


def load_tests(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate(tests):
    total = len(tests)
    correct = 0
    timings = []

    route_counter = Counter()
    confusion = defaultdict(lambda: defaultdict(int))

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

        print(f"{i}. {status} | {elapsed} ms")
        print(f"Prompt:   {prompt}")
        print(f"Expected: {expected}")
        print(f"Actual:   {label}")
        print(f"Meta:     ({label}, {conf}, {source})\n")

    accuracy = round((correct / total) * 100, 2)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
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
        
    with open("test/results/latest.txt", "w") as f:
        f.write(f"Accuracy: {accuracy}%\n")

    return accuracy


def main():
    dataset = input("Enter dataset filename (e.g. v3.json): ").strip()

    path = os.path.join("test", "datasets", dataset)

    if not os.path.exists(path):
        print("Dataset not found.")
        return

    tests = load_tests(path)
    evaluate(tests)


if __name__ == "__main__":
    main()