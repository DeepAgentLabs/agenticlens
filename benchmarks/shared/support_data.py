import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "datasets"


def load_json(filename: str) -> list[dict[str, Any]]:
    path = DATASET_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def load_support_cases() -> list[dict[str, Any]]:
    return load_json("support_cases.json")


def load_policy_docs() -> list[dict[str, Any]]:
    return load_json("refund_policy_docs.json")


def load_orders() -> list[dict[str, Any]]:
    return load_json("orders.json")


def lookup_order(order_id: str) -> dict[str, Any]:
    orders = load_orders()

    for order in orders:
        if order["order_id"] == order_id:
            return {
                "found": True,
                **order,
            }

    return {
        "found": False,
        "order_id": order_id,
    }


def simple_retrieve(query: str, top_k: int = 6) -> list[dict[str, Any]]:
    docs = load_policy_docs()

    clean_query = query.lower().replace("?", "").replace(".", "")
    query_words = set(clean_query.split())

    scored_docs = []

    for doc in docs:
        clean_doc = doc["text"].lower().replace("?", "").replace(".", "")
        doc_words = set(clean_doc.split())
        score = len(query_words.intersection(doc_words))
        scored_docs.append((score, doc))

    scored_docs.sort(reverse=True, key=lambda item: item[0])

    return [doc for score, doc in scored_docs[:top_k] if score > 0]


def estimate_avg_tokens_per_chunk(chunks: list[dict[str, Any]]) -> int:
    if not chunks:
        return 0

    total_words = sum(len(chunk["text"].split()) for chunk in chunks)

    # Rough practical approximation:
    # 1 word is around 1.3 tokens in many English text workflows.
    estimated_tokens = int(total_words * 1.3)

    return max(1, estimated_tokens // len(chunks))


def build_policy_context(chunks: list[dict[str, Any]]) -> str:
    return "\n".join(f"- {chunk['text']}" for chunk in chunks)