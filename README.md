# 🚀 Local AI Router

A lightweight, modular **local AI routing system** that intelligently selects the best model for a given prompt using rule-based + AI-assisted classification.

Built for speed, efficiency, and experimentation with local LLMs.

Built for a very basic laptop with very basic user specs, models can be updated and retagged in router.py file, use whichever ones you want.

---

## 🔧 Features

- 🧠 Smart prompt classification (coding, math, reasoning, writing, general, rag)
- ⚡ Fast rule-based routing (near 0ms for most prompts if you can prompt engineer to include certain phrases)
- 🤖 AI fallback classifier for ambiguous queries
- 📊 Benchmark test suite with accuracy + latency tracking
- 📈 Performance dashboard (route distribution, timing, confusion matrix)
- 💾 Memory + stats tracking
- 🖥️ CLI interface with commands

---

## 🏗️ Project Structure

## Setup

For same environment

```bash
pip install -r requirements.txt
```

### (First Time Only)

To download the semantic model locally:

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```
