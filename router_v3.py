import ollama
import json
import os
import re
import time
from datetime import datetime
from config import MEMORY_FILE, STATS_FILE

# ==================================================
# LOCAL AI ROUTER v3
# Hybrid Rules + AI Classifier + Memory + Stats
# ==================================================

# ---------------- CONFIG ----------------

ROUTES = {
    "coding": "deepseek-coder",
    "math": "deepseek-r1:14b",
    "reasoning": "qwen2.5:7b",
    "writing": "mistral:7b",
    "general": "qwen2.5:3b",
    "rag": "qwen2.5:3b"
}

CLASSIFIER_MODEL = "qwen2.5:1.5b"
FALLBACK_MODEL = "qwen2.5:7b"

MAX_MEMORY_ITEMS = 12
LOW_CONFIDENCE_THRESHOLD = 40

# ---------------- RULE WORDS ----------------

CODE_WORDS = [
    "code", "python", "java", "javascript", "c++", "bug",
    "debug", "script", "program", "build", "function",
    "class", "api", "sql", "html", "css"
]

MATH_WORDS = [
    "solve", "integral", "derivative", "differentiate",
    "equation", "matrix", "algebra", "probability",
    "statistics", "limit", "calculus", "trigonometry"
]

WRITING_WORDS = [
    "email", "essay", "rewrite", "apology", "letter",
    "cover letter", "blog", "linkedin post", "paragraph"
]

REASONING_WORDS = [
    "should", "compare", "pros and cons", "strategy",
    "debate", "best option", "recommend", "why"
]

# ---------------- FILE INIT ----------------

def ensure_files():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({
                "total_prompts": 0,
                "routes": {},
                "models": {},
                "avg_response_sec": 0,
                "last_used": ""
            }, f)

# ---------------- STORAGE ----------------

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- MEMORY ----------------

def load_memory():
    return load_json(MEMORY_FILE)

def save_memory(memory):
    save_json(MEMORY_FILE, memory[-MAX_MEMORY_ITEMS:])

def clear_memory():
    save_memory([])
    print("🧹 Memory cleared.")

# ---------------- STATS ----------------

def update_stats(route, model, sec):
    stats = load_json(STATS_FILE)

    stats["total_prompts"] += 1
    stats["routes"][route] = stats["routes"].get(route, 0) + 1
    stats["models"][model] = stats["models"].get(model, 0) + 1
    stats["last_used"] = str(datetime.now())

    total = stats["total_prompts"]
    prev = stats["avg_response_sec"]
    stats["avg_response_sec"] = round(((prev * (total - 1)) + sec) / total, 2)

    save_json(STATS_FILE, stats)

def show_stats():
    stats = load_json(STATS_FILE)

    print("\n========== STATS ==========")
    print("Total Prompts:", stats["total_prompts"])
    print("Average Response Time:", stats["avg_response_sec"], "sec")
    print("Last Used:", stats["last_used"])

    print("\nRoutes:")
    for k, v in stats["routes"].items():
        print(f"  {k}: {v}")

    print("\nModels:")
    for k, v in stats["models"].items():
        print(f"  {k}: {v}")

# ---------------- ASK MODEL ----------------

def ask(model, prompt, stream=True):
    try:
        if stream:
            stream_resp = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            full = ""
            for chunk in stream_resp:
                token = chunk["message"]["content"]
                print(token, end="", flush=True)
                full += token

            print()
            return full

        else:
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]

    except Exception:
        print("\n⚠ Main model failed. Using fallback...\n")

        response = ollama.chat(
            model=FALLBACK_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        return response["message"]["content"]

# ---------------- RULE ROUTER ----------------

def contains_any(text, words):
    return any(w in text for w in words)

def rule_classify(prompt):
    p = prompt.lower()

    if contains_any(p, CODE_WORDS):
        return "coding", 98

    if contains_any(p, MATH_WORDS):
        return "math", 98

    if contains_any(p, WRITING_WORDS):
        return "writing", 95

    if contains_any(p, REASONING_WORDS):
        return "reasoning", 90

    return None, 0

# ---------------- AI CLASSIFIER ----------------

def ai_classify(prompt):
    router_prompt = f"""
You are an AI router.

Choose ONLY one label:

coding
math
reasoning
writing
general
rag

Return EXACTLY in one line:
label|confidence

Examples:
coding|95
math|98
general|80

Prompt: {prompt}
"""

    try:
        response = ollama.chat(
            model=CLASSIFIER_MODEL,
            messages=[
                {"role": "user", "content": router_prompt}
            ],
            options={
                "temperature": 0,
                "top_p": 0.1,
                "num_predict": 10
            }
        )

        result = response["message"]["content"].strip().lower()

        parts = result.split("|")

        if len(parts) != 2:
            return "general", 50

        label = parts[0].strip()
        conf = int(parts[1].strip())

        if label not in ROUTES:
            return "general", 50

        # confidence clamp
        conf = max(0, min(conf, 100))

        return label, conf

    except:
        return "general", 50
# ---------------- MASTER CLASSIFIER ----------------

def classify(prompt):
    p = prompt.lower().strip()

    # 1. rules first
    label, conf = rule_classify(p)
    if label:
        return label, conf, "rules"

    # 2. simple factual prompts only
    factual_starts = [
    "what is", "what are",
    "who is", "who was",
    "define",
    "explain",
    "how does",
    "tell me about"
]

    if any(p.startswith(x) for x in factual_starts):
        return "general", 96, "fact-rule"

    # 3. special reasoning concepts
    if "behind" in p:
        return "reasoning", 90, "logic-rule"

    if p.startswith("how does"):
        return "general", 94, "fact-rule"

    # 4. AI fallback
    label, conf = ai_classify(prompt)

    # distrust random writing outputs
    if label == "writing":
        if not any(x in p for x in [
            "write", "email", "essay", "rewrite",
            "cover letter", "draft"
        ]):
            return "general", 60, "fallback"

    if conf < 70:
        return "general", 50, "fallback"

    return label, conf, "ai"

# ---------------- COMMANDS ----------------

def show_models():
    print("\n======= MODELS =======")
    for k, v in ROUTES.items():
        print(f"{k:10} -> {v}")

# ---------------- MAIN ----------------

def main():
    ensure_files()

    print("🚀 Local AI Router v3 Started")
    print("Commands: /stats /clear /models /exit")

    while True:
        try:
            user = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Exiting...")
            break

        if not user:
            continue

        cmd = user.lower()

        # ---------------- EXIT ----------------
        if cmd in ["/exit", "exit", "quit"]:
            print("👋 Goodbye.")
            break

        # ---------------- COMMANDS ----------------
        if cmd == "/stats":
            show_stats()
            continue

        if cmd == "/clear":
            clear_memory()
            continue

        if cmd == "/models":
            show_models()
            continue

        # ---------------- LOAD MEMORY ----------------
        memory = load_memory()
        context = "\n".join(memory)

        # ---------------- CLASSIFY ----------------
        label, confidence, source = classify(user)

        # failsafe
        if label not in ROUTES:
            label = "general"
            confidence = 50
            source = "failsafe"

        model = ROUTES[label]

        print(f"\n[Router: {label} → {model} | {confidence}% | {source}]")
        print()

        # ---------------- BUILD PROMPT ----------------
        final_prompt = f"""
Previous conversation:
{context}

User request:
{user}
"""

        # ---------------- ASK MODEL ----------------
        start = time.time()

        try:
            answer = ask(model, final_prompt, stream=True)
        except Exception as e:
            print(f"\n⚠ Error: {e}")
            continue

        sec = round(time.time() - start, 2)

        # ---------------- SAVE MEMORY ----------------
        memory.append(f"User: {user}")
        memory.append(f"Assistant: {answer}")
        save_memory(memory)

        # ---------------- UPDATE STATS ----------------
        update_stats(label, model, sec)


if __name__ == "__main__":
    main()