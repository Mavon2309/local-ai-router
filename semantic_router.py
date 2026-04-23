import os
import logging
from sentence_transformers import util

# =====================================
# OFFLINE + CLEAN LOGGING
# =====================================
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# =====================================
# GLOBALS (LAZY LOADED)
# =====================================
model = None
INTENT_EMBEDDINGS = None


# =====================================
# MODEL LOADER (LAZY)
# =====================================
def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


# =====================================
# INTENT EMBEDDINGS (LAZY + CACHED)
# =====================================
def get_intent_embeddings():
    global INTENT_EMBEDDINGS

    if INTENT_EMBEDDINGS is None:
        model = get_model()

        INTENT_EXAMPLES = {
        "coding": [
            "write code", "build program", "debug script",
            "create api", "fix bug", "develop software"
        ],
        "math": [
            "solve equation", "calculate integral",
            "derivative problem", "algebra", "probability",
            "bayes theorem"
        ],
        "writing": [
            "write email", "draft essay", "rewrite paragraph",
            "cover letter", "formal writing"
        ],
        "reasoning": [
            "compare options", "pros and cons",
            "what is best", "should i", "decision making"
        ],
        "general": [
            "what is", "explain", "define concept",
            "how does it work"
        ],

        # ✅ ADD THIS BLOCK
        "rag": [
            "search documents",
            "retrieve information from files",
            "query knowledge base",
            "look up data",
            "find information in documents",
            "semantic search",
            "retrieve context",
            "search pdf",
            "search database"
        ]
}

        # Normalize embeddings for better cosine similarity
        INTENT_EMBEDDINGS = {
            k: model.encode(v, convert_to_tensor=True, normalize_embeddings=True)
            for k, v in INTENT_EXAMPLES.items()
        }

    return INTENT_EMBEDDINGS


# =====================================
# MAIN CLASSIFIER
# =====================================
def semantic_classify(prompt):
    model = get_model()
    embeddings = get_intent_embeddings()

    query_embedding = model.encode(
        prompt,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    best_label = None
    best_score = -1

    for label, examples in embeddings.items():
        score = util.cos_sim(query_embedding, examples).max().item()

        if score > best_score:
            best_score = score
            best_label = label

    return best_label, int(best_score * 100)