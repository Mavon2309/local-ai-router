from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

INTENT_EXAMPLES = {
    "coding": [
        "write a program", "debug code", "fix script",
        "build an app", "create a function"
    ],
    "math": [
        "solve equation", "calculate derivative",
        "integral problem", "linear algebra"
    ],
    "writing": [
        "write an essay", "draft an email",
        "rewrite text", "professional message"
    ],
    "reasoning": [
        "compare options", "which is better",
        "pros and cons", "should I do this"
    ],
    "general": [
        "what is", "how does", "explain concept",
        "define term"
    ]
}

INTENT_EMBEDDINGS = {
    k: model.encode(v, convert_to_tensor=True)
    for k, v in INTENT_EXAMPLES.items()
}


def semantic_classify(prompt):
    emb = model.encode(prompt, convert_to_tensor=True)

    best_label = None
    best_score = -1

    for label, examples in INTENT_EMBEDDINGS.items():
        score = util.cos_sim(emb, examples).max().item()

        if score > best_score:
            best_score = score
            best_label = label

    return best_label, int(best_score * 100)